import requests

from config import TREASURY_SERIES, FRED_ADDITIONAL

# -----------------------------------------------------------------------------
# FRED Fetcher (generic)
# -----------------------------------------------------------------------------

def fetch_fred_series(series_id):
    """
    Fetches the most recent non-null value for any FRED series.
    Returns {"date": str, "value": float} or None.
    """
    try:
        url = (
            f"https://fred.stlouisfed.org/"
            f"graph/fredgraph.csv?id={series_id}"
        )
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        lines = response.text.strip().splitlines()

        for row in reversed(lines[1:]):
            parts = row.split(",")
            if len(parts) < 2:
                continue
            date_str, value = parts[0], parts[1]
            if value not in (".", ""):
                return {
                    "date":  date_str,
                    "value": float(value),
                }

    except Exception:
        pass

    return None

# -----------------------------------------------------------------------------
# Treasury Yields
# -----------------------------------------------------------------------------

def fetch_treasury_yields():
    return {
        label: fetch_fred_series(series_id)
        for label, series_id in TREASURY_SERIES.items()
    }

# -----------------------------------------------------------------------------
# SOFR
# -----------------------------------------------------------------------------

def fetch_sofr():
    try:
        response = requests.get(
            "https://markets.newyorkfed.org/api/rates/sofr/last/1.json",
            timeout=15,
        )
        response.raise_for_status()
        item = response.json()["refRates"][0]
        return {
            "date":  item["effectiveDate"],
            "value": float(item["percentRate"]),
        }
    except Exception:
        return None

# -----------------------------------------------------------------------------
# Additional Market Data
# -----------------------------------------------------------------------------

def fetch_additional_market_data():
    return {
        key: fetch_fred_series(series_id)
        for key, series_id in FRED_ADDITIONAL.items()
    }

# -----------------------------------------------------------------------------
# Market Snapshot
# -----------------------------------------------------------------------------

def build_market_snapshot():

    treasuries  = fetch_treasury_yields()
    sofr        = fetch_sofr()
    additional  = fetch_additional_market_data()

    spread = None
    if treasuries.get("2Y") and treasuries.get("10Y"):
        spread = (
            treasuries["10Y"]["value"]
            - treasuries["2Y"]["value"]
        )

    snapshot = {
        "treasuries": treasuries,
        "sofr":       sofr,
        "spread":     spread,
        "additional": additional,
    }

    return snapshot

# -----------------------------------------------------------------------------
# Market Narrative (for Groq prompt injection)
# -----------------------------------------------------------------------------

def generate_market_narrative(snapshot):

    t           = snapshot.get("treasuries", {})
    spread      = snapshot.get("spread")
    additional  = snapshot.get("additional", {})

    lines = []

    # Yield curve
    t10 = t.get("10Y")
    t30 = t.get("30Y")
    t2  = t.get("2Y")

    if t10:
        lines.append(f"10Y Treasury: {t10['value']:.2f}%")
    if t30:
        lines.append(f"30Y Treasury: {t30['value']:.2f}%")
    if t2:
        lines.append(f"2Y Treasury:  {t2['value']:.2f}%")

    if spread is not None:
        direction = "normal" if spread > 0 else "inverted"
        lines.append(
            f"2Y/10Y Spread: {spread:+.2f}% ({direction} curve)"
        )

    # Credit spreads
    ig = additional.get("IG_OAS")
    hy = additional.get("HY_OAS")
    if ig:
        lines.append(f"IG Credit Spread (OAS): {ig['value'] * 100:.0f} bps")
    if hy:
        lines.append(f"HY Credit Spread (OAS): {hy['value'] * 100:.0f} bps")

    # Inflation breakeven
    be = additional.get("BREAKEVEN_10Y")
    if be:
        lines.append(f"10Y Inflation Breakeven: {be['value']:.2f}%")

    # VIX
    vix = additional.get("VIX")
    if vix:
        lines.append(f"VIX: {vix['value']:.1f}")

    return "\n".join(lines) if lines else "Market data unavailable."
