import requests
from datetime import datetime, timedelta

# ---------------------------------------------------------------------
# FRED JSON API — no API key required for public series
# More reliable than the CSV endpoint
# ---------------------------------------------------------------------

FRED_BASE = "https://fred.stlouisfed.org/graph/fredgraph.csv"

# Treasury yields
TREASURY_SERIES = {
    "2Y":  "DGS2",
    "5Y":  "DGS5",
    "10Y": "DGS10",
    "30Y": "DGS30",
}

# Additional market indicators
# OAS series are in PERCENT (e.g. 0.77 = 77 bps) — multiply by 100 for display
# VIX is in Index points (e.g. 16.1) — display as-is
# T10YIE is in percent (e.g. 2.40) — display as-is
ADDITIONAL_SERIES = {
    "IG_OAS":        ("BAMLC0A0CM",  "pct_to_bps"),  # multiply × 100
    "HY_OAS":        ("BAMLH0A0HYM2","pct_to_bps"),  # multiply × 100
    "BREAKEVEN_10Y": ("T10YIE",      "pct"),          # display as-is
    "VIX":           ("VIXCLS",      "index"),        # display as-is
}


def fetch_fred_csv(series_id):
    """
    Fetches the most recent non-null observation for a FRED series
    via the public CSV endpoint (no API key required).
    Returns {"date": str, "value": float} or None.
    """
    url = f"{FRED_BASE}?id={series_id}"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()

        lines = resp.text.strip().splitlines()
        # Walk backwards to find the most recent non-missing value
        for row in reversed(lines[1:]):
            parts = row.split(",")
            if len(parts) < 2:
                continue
            date_str, raw_value = parts[0].strip(), parts[1].strip()
            if raw_value in (".", "", "NA"):
                continue
            try:
                return {"date": date_str, "value": float(raw_value)}
            except ValueError:
                continue

    except Exception as e:
        print(f"    FRED error [{series_id}]: {e}")

    return None


def fetch_sofr():
    """
    NY Fed SOFR — most recent rate.
    Returns {"date": str, "value": float} or None.
    """
    try:
        resp = requests.get(
            "https://markets.newyorkfed.org/api/rates/sofr/last/1.json",
            timeout=15,
        )
        resp.raise_for_status()
        item = resp.json()["refRates"][0]
        return {
            "date":  item["effectiveDate"],
            "value": float(item["percentRate"]),
        }
    except Exception as e:
        print(f"    SOFR error: {e}")
        return None


def build_market_snapshot():
    """
    Fetches all market data and returns a structured dict.
    Every value is either {"date": str, "value": float} or None —
    never a missing key.
    """
    treasuries = {
        label: fetch_fred_csv(sid)
        for label, sid in TREASURY_SERIES.items()
    }

    sofr = fetch_sofr()

    # 2Y/10Y spread
    t2  = treasuries.get("2Y")
    t10 = treasuries.get("10Y")
    spread = (
        round(t10["value"] - t2["value"], 4)
        if t2 and t10 else None
    )

    # Additional — fetch raw, store raw value + unit tag
    additional = {}
    for key, (series_id, unit_type) in ADDITIONAL_SERIES.items():
        raw = fetch_fred_csv(series_id)
        if raw:
            # Convert OAS from percent to bps immediately at fetch time
            # so the rest of the code never has to remember to multiply
            if unit_type == "pct_to_bps":
                additional[key] = {
                    "date":  raw["date"],
                    "value": round(raw["value"] * 100, 1),  # now in bps
                    "unit":  "bps",
                }
            else:
                additional[key] = {
                    "date":  raw["date"],
                    "value": raw["value"],
                    "unit":  unit_type,
                }
        else:
            additional[key] = None

    return {
        "treasuries": treasuries,
        "sofr":       sofr,
        "spread":     spread,
        "additional": additional,
    }


def safe_pct(item, decimals=2):
    """Format a market item as a percentage string, or N/A."""
    if not item:
        return "N/A"
    return f"{item['value']:.{decimals}f}%"


def safe_val(item, fmt="{:.1f}", suffix=""):
    """Format a market item with arbitrary format, or N/A."""
    if not item:
        return "N/A"
    try:
        return fmt.format(item["value"]) + suffix
    except Exception:
        return "N/A"


def generate_market_narrative(snapshot):
    """
    Plain-text market summary for injection into the Groq prompt.
    All values are safely guarded.
    """
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
