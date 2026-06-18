import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
})

TREASURY_XML_URL = (
    "https://home.treasury.gov/resource-center/data-chart-center"
    "/interest-rates/pages/xml"
)

TREASURY_NS = {
    "d": "http://schemas.microsoft.com/ado/2007/08/dataservices",
    "m": "http://schemas.microsoft.com/ado/2007/08/dataservices/metadata",
}


def _fetch_treasury_xml(data_type, yyyymm):
    resp = SESSION.get(
        TREASURY_XML_URL,
        params={
            "data":                       data_type,
            "field_tdr_date_value_month": yyyymm,
        },
        timeout=15,
    )
    resp.raise_for_status()
    return ET.fromstring(resp.content)


def _latest_entry(root):
    if root is None: return None
    entries = root.findall(".//{http://www.w3.org/2005/Atom}entry")
    return entries[-1] if entries else None


def _try_months():
    now = datetime.utcnow()
    return [
        now.strftime("%Y%m"),
        (now.replace(day=1) - timedelta(days=1)).strftime("%Y%m"),
    ]


# ------------------------------------------------------------------
# Treasury Data (Nominal, Real, SOFR)
# Single source of truth: Treasury XML
# ------------------------------------------------------------------

TREASURY_FIELDS = {
    "2Y":        "BC_2YEAR",
    "5Y":        "BC_5YEAR",
    "10Y":       "BC_10YEAR",
    "30Y":       "BC_30YEAR",
    "SOFR":      "SOFR",
}

def fetch_treasury_data():
    """
    Fetches yields and SOFR from Treasury Yield Curve XML.
    Returns (results_dict, sofr_dict).
    """
    results = {k: None for k in ["2Y", "5Y", "10Y", "30Y"]}
    sofr    = None

    for yyyymm in _try_months():
        try:
            root   = _fetch_treasury_xml("daily_treasury_yield_curve", yyyymm)
            latest = _latest_entry(root)
            if not latest: continue

            any_found = False
            for label, field in TREASURY_FIELDS.items():
                el = latest.find(f".//d:{field}", TREASURY_NS)
                if el is not None and el.text and el.text.strip() not in ("", "null"):
                    val = float(el.text.strip())
                    if label == "SOFR":
                        sofr = {"value": val, "date": yyyymm}
                    else:
                        results[label] = {"value": val, "date": yyyymm}
                        any_found = True

            if any_found: break
        except Exception as e:
            print(f"    Treasury Yield XML error [{yyyymm}]: {e}")

    return results, sofr


def fetch_tips_real_yield():
    for yyyymm in _try_months():
        try:
            root   = _fetch_treasury_xml("daily_treasury_real_yield_curve", yyyymm)
            latest = _latest_entry(root)
            if not latest: continue
            el = latest.find(".//d:TC_10YEAR", TREASURY_NS)
            if el is not None and el.text and el.text.strip() not in ("", "null"):
                return float(el.text.strip())
        except Exception as e:
            print(f"    TIPS real yield error [{yyyymm}]: {e}")
    return None


# ------------------------------------------------------------------
# SOFR — Fallbacks
# ------------------------------------------------------------------

def fetch_sofr_fallback():
    """
    NY Fed JSON and FRED fallbacks if Treasury SOFR is missing.
    """
    # Attempt 1: NY Fed JSON API (Fast, structured)
    try:
        resp = SESSION.get("https://markets.newyorkfed.org/api/rates/all/latest.json", timeout=8)
        resp.raise_for_status()
        data = resp.json()
        for rate in data.get("rates", []):
            if rate.get("type") == "SOFR":
                val = float(rate["percentRate"])
                print(f"    SOFR from NY Fed API: {val}%")
                return {"value": val, "date": rate.get("effectiveDate", "latest")}
    except Exception as e:
        print(f"    SOFR NY Fed API error: {e}")

    # Attempt 2: FRED CSV streamed (often throttled/slow)
    try:
        resp = SESSION.get("https://fred.stlouisfed.org/graph/fredgraph.csv?id=SOFR", timeout=12, stream=True)
        resp.raise_for_status()
        chunks = []
        for chunk in resp.iter_content(chunk_size=8192):
            chunks.append(chunk)
            if sum(len(c) for c in chunks) > 100_000: break
        resp.close()
        lines = b"".join(chunks).decode("utf-8", errors="replace").strip().splitlines()
        for row in reversed(lines[1:]):
            parts = row.split(",")
            if len(parts) < 2 or parts[1].strip() in (".", "", "NA"): continue
            val = float(parts[1].strip())
            print(f"    SOFR from FRED: {val}% ({parts[0].strip()})")
            return {"value": val, "date": parts[0].strip()}
    except Exception as e:
        print(f"    SOFR FRED error: {e}")

    return None


# ------------------------------------------------------------------
# VIX via yfinance (removed to avoid slow imports/timeouts)
# Fallback to FRED for VIX
# ------------------------------------------------------------------

def fetch_vix():
    """Fetches VIX from FRED (VIXCLS series)."""
    try:
        resp = SESSION.get(
            "https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS",
            timeout=10,
        )
        resp.raise_for_status()
        lines = resp.text.strip().splitlines()
        for row in reversed(lines[1:]):
            parts = row.split(",")
            if len(parts) < 2: continue
            val_str = parts[1].strip()
            if val_str in (".", "", "NA"): continue
            return {
                "value": round(float(val_str), 2),
                "date":  parts[0].strip(),
                "unit":  "index",
            }
    except Exception as e:
        print(f"    VIX fetch error: {e}")
    return None


# ------------------------------------------------------------------
# OAS spreads via FRED
# ------------------------------------------------------------------

def fetch_oas_spreads():
    result = {"IG_OAS": None, "HY_OAS": None}
    for key, series_id in [("IG_OAS", "BAMLC0A0CM"), ("HY_OAS", "BAMLH0A0HYM2")]:
        try:
            resp = SESSION.get(
                f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}",
                timeout=10,
            )
            resp.raise_for_status()
            lines = resp.text.strip().splitlines()
            for row in reversed(lines[1:]):
                parts = row.split(",")
                if len(parts) < 2: continue
                val = parts[1].strip()
                if val in (".", "", "NA"): continue
                result[key] = {
                    "value": round(float(val) * 100, 1),
                    "date":  parts[0].strip(),
                    "unit":  "bps",
                }
                break
        except Exception: pass
    return result


# ------------------------------------------------------------------
# Full market snapshot (Parallelized)
# ------------------------------------------------------------------

def build_market_snapshot():
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=5) as executor:
        # Step 1: Sequential fetch of primary source (Yields + possible SOFR)
        # This is fast enough to do first.
        treasuries, sofr = fetch_treasury_data()

        # Step 2: Parallelize fallbacks and additional data
        futures = {
            "vix":       executor.submit(fetch_vix),
            "oas":       executor.submit(fetch_oas_spreads),
            "tips":      executor.submit(fetch_tips_real_yield),
        }
        if not sofr:
            futures["sofr"] = executor.submit(fetch_sofr_fallback)

        vix  = futures["vix"].result()
        oas  = futures["oas"].result()
        tips_real = futures["tips"].result()
        if not sofr and "sofr" in futures:
            sofr = futures["sofr"].result()

    t2   = treasuries.get("2Y")
    t10  = treasuries.get("10Y")
    sprd = (round(t10["value"] - t2["value"], 4) if t2 and t10 else None)

    breakeven = None
    if t10 and tips_real is not None:
        breakeven = {
            "value": round(t10["value"] - tips_real, 2),
            "date":  t10.get("date", ""),
            "unit":  "pct",
        }

    found_yields = sum(1 for v in treasuries.values() if v)
    print(f"    Market Data: {found_yields}/4 yields, SOFR={'Yes' if sofr else 'N/A'}, VIX={'Yes' if vix else 'N/A'}")

    return {
        "treasuries": treasuries,
        "sofr":       sofr,
        "spread":     sprd,
        "additional": {
            "VIX":           vix,
            "BREAKEVEN_10Y": breakeven,
            "IG_OAS":        oas.get("IG_OAS"),
            "HY_OAS":        oas.get("HY_OAS"),
        },
    }


# ------------------------------------------------------------------
# Formatting helpers
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
