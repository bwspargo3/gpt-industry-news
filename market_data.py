import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# ------------------------------------------------------------------
# US Treasury Direct XML Feed — official source, no rate limiting,
# no API key. Returns full yield curve for current month.
# Field names in the XML for par yield curve:
#   d:BC_2YEAR, d:BC_5YEAR, d:BC_10YEAR, d:BC_30YEAR
# ------------------------------------------------------------------

TREASURY_XML_URL = (
    "https://home.treasury.gov/resource-center/data-chart-center"
    "/interest-rates/pages/xml"
)

TREASURY_NS = {
    "d": "http://schemas.microsoft.com/ado/2007/08/dataservices",
    "m": "http://schemas.microsoft.com/ado/2007/08/dataservices/metadata",
}

TREASURY_FIELDS = {
    "2Y":  "BC_2YEAR",
    "5Y":  "BC_5YEAR",
    "10Y": "BC_10YEAR",
    "30Y": "BC_30YEAR",
}


def fetch_treasury_yields():
    """
    Fetches daily Treasury par yield curve from Treasury.gov XML feed.
    Returns the most recent business day's rates.
    No API key required, no rate limiting.
    """
    results = {k: None for k in TREASURY_FIELDS}

    # Fetch current month; if we're early in the month and get nothing,
    # also try prior month
    now   = datetime.utcnow()
    months = [
        now.strftime("%Y%m"),
        (now.replace(day=1) - timedelta(days=1)).strftime("%Y%m"),
    ]

    for yyyymm in months:
        try:
            resp = requests.get(
                TREASURY_XML_URL,
                params={
                    "data":                    "daily_treasury_yield_curve",
                    "field_tdr_date_value_month": yyyymm,
                },
                timeout=20,
                headers={"User-Agent": "ActuarialIntelligence/1.0"},
            )
            resp.raise_for_status()

            root     = ET.fromstring(resp.content)
            # Entries are in chronological order — take the last one
            entries  = root.findall(".//{http://www.w3.org/2005/Atom}entry")
            if not entries:
                continue

            latest = entries[-1]

            any_found = False
            for label, field in TREASURY_FIELDS.items():
                el = latest.find(f".//d:{field}", TREASURY_NS)
                if el is not None and el.text and el.text.strip() not in ("", "null"):
                    try:
                        results[label] = {
                            "value": float(el.text.strip()),
                            "date":  yyyymm,
                        }
                        any_found = True
                    except ValueError:
                        pass

            if any_found:
                break   # Got good data, no need to try prior month

        except Exception as e:
            print(f"    Treasury XML error [{yyyymm}]: {e}")

    found = sum(1 for v in results.values() if v)
    print(f"    Treasury yields: {found}/4 fetched")
    return results


# ------------------------------------------------------------------
# SOFR — NY Fed (corrected endpoint)
# ------------------------------------------------------------------

def fetch_sofr():
    """
    NY Fed SOFR rate. Uses the correct endpoint with proper params.
    """
    urls_to_try = [
        "https://markets.newyorkfed.org/api/rates/sofr/last/1.json",
        "https://markets.newyorkfed.org/api/rates/all/last/1.json",
    ]
    for url in urls_to_try:
        try:
            resp = requests.get(url, timeout=15,
                                headers={"Accept": "application/json"})
            resp.raise_for_status()
            data = resp.json()

            # Try refRates key (standard response)
            rates = data.get("refRates", [])
            if not rates:
                # Try flat list
                rates = data if isinstance(data, list) else []

            for rate in rates:
                if rate.get("type", "").upper() == "SOFR" or "sofr" in str(rate).lower():
                    val = rate.get("percentRate") or rate.get("rate")
                    if val:
                        return {
                            "value": float(val),
                            "date":  rate.get("effectiveDate", ""),
                        }
        except Exception as e:
            print(f"    SOFR error [{url}]: {e}")

    return None


# ------------------------------------------------------------------
# FRED CSV — used for OAS spreads, VIX, breakeven
# Longer timeout + retry since FRED can be slow from CI environments
# ------------------------------------------------------------------

FRED_SERIES = {
    # OAS stored in percent (0.77 = 77 bps) — converted at fetch time
    "IG_OAS":        ("BAMLC0A0CM",   "pct_to_bps"),
    "HY_OAS":        ("BAMLH0A0HYM2", "pct_to_bps"),
    # Breakeven in percent — display as-is
    "BREAKEVEN_10Y": ("T10YIE",        "pct"),
    # VIX in index points — display as-is
    "VIX":           ("VIXCLS",        "index"),
}


def fetch_fred_csv(series_id, timeout=30, retries=2):
    """
    FRED public CSV endpoint. Longer timeout and retry logic
    to handle GitHub Actions network variability.
    """
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"

    for attempt in range(retries):
        try:
            resp = requests.get(
                url, timeout=timeout,
                headers={"User-Agent": "ActuarialIntelligence/1.0"},
            )
            resp.raise_for_status()

            lines = resp.text.strip().splitlines()
            for row in reversed(lines[1:]):
                parts = row.split(",")
                if len(parts) < 2:
                    continue
                date_str, val = parts[0].strip(), parts[1].strip()
                if val in (".", "", "NA"):
                    continue
                try:
                    return {"date": date_str, "value": float(val)}
                except ValueError:
                    continue

        except Exception as e:
            if attempt < retries - 1:
                print(f"    FRED [{series_id}] attempt {attempt+1} failed, retrying...")
            else:
                print(f"    FRED error [{series_id}]: {e}")

    return None


def fetch_additional():
    additional = {}
    for key, (series_id, unit_type) in FRED_SERIES.items():
        raw = fetch_fred_csv(series_id)
        if raw:
            if unit_type == "pct_to_bps":
                additional[key] = {
                    "value": round(raw["value"] * 100, 1),
                    "date":  raw["date"],
                    "unit":  "bps",
                }
            else:
                additional[key] = {
                    "value": raw["value"],
                    "date":  raw["date"],
                    "unit":  unit_type,
                }
        else:
            additional[key] = None
    return additional


# ------------------------------------------------------------------
# Build snapshot
# ------------------------------------------------------------------

def build_market_snapshot():
    treasuries = fetch_treasury_yields()
    sofr       = fetch_sofr()
    additional = fetch_additional()

    t2  = treasuries.get("2Y")
    t10 = treasuries.get("10Y")
    spread = (
        round(t10["value"] - t2["value"], 4)
        if t2 and t10 else None
    )

    return {
        "treasuries": treasuries,
        "sofr":       sofr,
        "spread":     spread,
        "additional": additional,
    }


# ------------------------------------------------------------------
# Formatting helpers (imported by email_template.py)
# ------------------------------------------------------------------

def safe_pct(item, decimals=2):
    if not item:
        return "N/A"
    return f"{item['value']:.{decimals}f}%"


def safe_val(item, fmt="{:.1f}", suffix=""):
    if not item:
        return "N/A"
    try:
        return fmt.format(item["value"]) + suffix
    except Exception:
        return "N/A"


def generate_market_narrative(snapshot):
    t    = snapshot.get("treasuries", {})
    add  = snapshot.get("additional", {})
    sofr = snapshot.get("sofr")
    sprd = snapshot.get("spread")

    spread_str = (
        f"{sprd:+.2f}% ({'normal' if sprd > 0 else 'inverted'})"
        if sprd is not None else "N/A"
    )

    ig  = add.get("IG_OAS")
    hy  = add.get("HY_OAS")
    be  = add.get("BREAKEVEN_10Y")
    vix = add.get("VIX")

    return "\n".join([
        f"2Y Treasury:             {safe_pct(t.get('2Y'))}",
        f"5Y Treasury:             {safe_pct(t.get('5Y'))}",
        f"10Y Treasury:            {safe_pct(t.get('10Y'))}",
        f"30Y Treasury:            {safe_pct(t.get('30Y'))}",
        f"SOFR:                    {safe_pct(sofr)}",
        f"2Y/10Y Spread:           {spread_str}",
        f"IG Credit Spread (OAS):  {safe_val(ig, '{:.0f}', ' bps')}",
        f"HY Credit Spread (OAS):  {safe_val(hy, '{:.0f}', ' bps')}",
        f"10Y Inflation Breakeven: {safe_pct(be)}",
        f"VIX:                     {safe_val(vix, '{:.1f}')}",
    ])
