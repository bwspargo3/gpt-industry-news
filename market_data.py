import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta


TREASURY_XML_URL = (
    "https://home.treasury.gov/resource-center/data-chart-center"
    "/interest-rates/pages/xml"
)

TREASURY_NS = {
    "d": "http://schemas.microsoft.com/ado/2007/08/dataservices",
    "m": "http://schemas.microsoft.com/ado/2007/08/dataservices/metadata",
}


def _fetch_treasury_xml(data_type, yyyymm):
    """Generic Treasury.gov XML fetcher for any data type."""
    resp = requests.get(
        TREASURY_XML_URL,
        params={
            "data":                       data_type,
            "field_tdr_date_value_month": yyyymm,
        },
        timeout=25,
        headers={"User-Agent": "ActuarialIntelligence/1.0"},
    )
    resp.raise_for_status()
    return ET.fromstring(resp.content)


def _latest_entry(root):
    """Returns the most recent Atom entry from a Treasury XML response."""
    entries = root.findall(".//{http://www.w3.org/2005/Atom}entry")
    return entries[-1] if entries else None


def _try_months():
    """Returns [current month YYYYMM, prior month YYYYMM]."""
    now = datetime.utcnow()
    return [
        now.strftime("%Y%m"),
        (now.replace(day=1) - timedelta(days=1)).strftime("%Y%m"),
    ]


# ------------------------------------------------------------------
# Treasury yields (nominal)
# ------------------------------------------------------------------

NOMINAL_FIELDS = {
    "2Y":  "BC_2YEAR",
    "5Y":  "BC_5YEAR",
    "10Y": "BC_10YEAR",
    "30Y": "BC_30YEAR",
}


def fetch_treasury_yields():
    results = {k: None for k in NOMINAL_FIELDS}

    for yyyymm in _try_months():
        try:
            root   = _fetch_treasury_xml("daily_treasury_yield_curve", yyyymm)
            latest = _latest_entry(root)
            if not latest:
                continue

            any_found = False
            for label, field in NOMINAL_FIELDS.items():
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
                break

        except Exception as e:
            print(f"    Treasury XML error [{yyyymm}]: {e}")

    found = sum(1 for v in results.values() if v)
    print(f"    Treasury yields: {found}/4 fetched")
    return results


# ------------------------------------------------------------------
# TIPS real yields — used to calculate breakeven inflation
# 10Y Breakeven = Nominal 10Y - TIPS Real 10Y
# Both from Treasury.gov; same reliable source as nominal yields
# ------------------------------------------------------------------

def fetch_tips_real_yield():
    """
    Returns the 10Y TIPS real yield as a float, or None.
    Source: Treasury.gov daily_treasury_real_yield_curve
    Field: TC_10YEAR
    """
    for yyyymm in _try_months():
        try:
            root   = _fetch_treasury_xml("daily_treasury_real_yield_curve", yyyymm)
            latest = _latest_entry(root)
            if not latest:
                continue
            el = latest.find(".//d:TC_10YEAR", TREASURY_NS)
            if el is not None and el.text and el.text.strip() not in ("", "null"):
                return float(el.text.strip())
        except Exception as e:
            print(f"    TIPS real yield error [{yyyymm}]: {e}")
    return None


# ------------------------------------------------------------------
# SOFR
# ------------------------------------------------------------------

def fetch_sofr():
    """
    Tries multiple sources for SOFR in order of reliability.
    Returns {"value": float, "date": str} or None.
    """
    # Attempt 1: Treasury XML may include SOFR field
    for yyyymm in _try_months():
        try:
            root   = _fetch_treasury_xml("daily_treasury_yield_curve", yyyymm)
            latest = _latest_entry(root)
            if not latest:
                continue
            el = latest.find(".//d:SOFR", TREASURY_NS)
            if el is not None and el.text and el.text.strip() not in ("", "null"):
                return {"value": float(el.text.strip()), "date": yyyymm}
        except Exception:
            pass

    # Attempt 2: NY Fed rates CSV download
    try:
        today  = datetime.utcnow()
        start  = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        url    = (
            "https://markets.newyorkfed.org/read"
            f"?startDt={start}&eventCodes=SOFR"
            "&productCode=50&sort=postDt:-1&format=csv"
        )
        resp   = requests.get(
            url, timeout=15,
            headers={"User-Agent": "ActuarialIntelligence/1.0"},
        )
        resp.raise_for_status()
        lines  = resp.text.strip().splitlines()
        for line in lines:
            parts = line.split(",")
            if len(parts) >= 2:
                try:
                    return {
                        "value": float(parts[-1].strip()),
                        "date":  parts[0].strip(),
                    }
                except ValueError:
                    continue
    except Exception as e:
        print(f"    SOFR CSV error: {e}")

    # Attempt 3: NY Fed rates page HTML
    try:
        resp = requests.get(
            "https://www.newyorkfed.org/markets/reference-rates/sofr",
            timeout=15,
            headers={"User-Agent": "ActuarialIntelligence/1.0"},
        )
        resp.raise_for_status()
        # Rate appears as a standalone decimal like "5.33" near "SOFR"
        match = re.search(
            r"SOFR[^<]{0,300}?(\d{1,2}\.\d{2})",
            resp.text[:8000],
            re.DOTALL,
        )
        if match:
            val = float(match.group(1))
            # Sanity check: SOFR is typically between 0.01 and 15
            if 0.01 < val < 15:
                return {"value": val, "date": "scraped"}
    except Exception as e:
        print(f"    SOFR page error: {e}")

    return None


# ------------------------------------------------------------------
# VIX via yfinance
# ------------------------------------------------------------------

def fetch_vix():
    """Fetch CBOE VIX via yfinance."""
    try:
        import yfinance as yf
        hist = yf.Ticker("^VIX").history(period="5d")
        if not hist.empty:
            return {
                "value": round(float(hist["Close"].iloc[-1]), 2),
                "date":  str(hist.index[-1].date()),
                "unit":  "index",
            }
    except Exception as e:
        print(f"    VIX fetch error: {e}")
    return None


# ------------------------------------------------------------------
# OAS spreads — try FRED with short timeout (fail fast)
# ------------------------------------------------------------------

def fetch_oas_spreads():
    """
    Attempts to fetch IG and HY OAS from FRED.
    Uses a short timeout to fail fast if FRED is blocking CI IPs.
    Returns dict with IG_OAS and HY_OAS (or None for each).
    """
    result = {"IG_OAS": None, "HY_OAS": None}

    for key, series_id in [("IG_OAS", "BAMLC0A0CM"), ("HY_OAS", "BAMLH0A0HYM2")]:
        try:
            resp = requests.get(
                f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}",
                timeout=8,
                headers={"User-Agent": "ActuarialIntelligence/1.0"},
            )
            resp.raise_for_status()
            lines = resp.text.strip().splitlines()
            for row in reversed(lines[1:]):
                parts = row.split(",")
                if len(parts) < 2:
                    continue
                val = parts[1].strip()
                if val in (".", "", "NA"):
                    continue
                result[key] = {
                    "value": round(float(val) * 100, 1),  # percent → bps
                    "date":  parts[0].strip(),
                    "unit":  "bps",
                }
                break
        except Exception:
            pass  # Show N/A — better than wrong value or hanging

    return result


# ------------------------------------------------------------------
# Full market snapshot
# ------------------------------------------------------------------

def build_market_snapshot():
    treasuries = fetch_treasury_yields()
    sofr       = fetch_sofr()
    vix        = fetch_vix()
    oas        = fetch_oas_spreads()

    t2  = treasuries.get("2Y")
    t10 = treasuries.get("10Y")
    spread = (
        round(t10["value"] - t2["value"], 4)
        if t2 and t10 else None
    )

    # 10Y breakeven = nominal 10Y - TIPS real 10Y
    # Both from Treasury.gov — same source, most accurate available
    tips_real = fetch_tips_real_yield()
    if t10 and tips_real is not None:
        breakeven = {
            "value": round(t10["value"] - tips_real, 2),
            "date":  t10.get("date", ""),
            "unit":  "pct",
        }
        print(f"    10Y Breakeven: {breakeven['value']:.2f}% "
              f"({t10['value']:.2f}% nominal - {tips_real:.2f}% TIPS)")
    else:
        breakeven = None

    additional = {
        "VIX":           vix,
        "BREAKEVEN_10Y": breakeven,
        "IG_OAS":        oas.get("IG_OAS"),
        "HY_OAS":        oas.get("HY_OAS"),
    }

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
        f"IG OAS (ICE BofA):       {safe_val(ig, '{:.0f}', ' bps')}",
        f"HY OAS (ICE BofA):       {safe_val(hy, '{:.0f}', ' bps')}",
        f"10Y Breakeven:           {safe_pct(be)}",
        f"VIX:                     {safe_val(vix, '{:.1f}')}",
    ])
