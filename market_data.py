import requests
from config import TREASURY_SERIES, FRED_ADDITIONAL


def fetch_fred_series(series_id):
    """
    Fetches the most recent non-null value for a FRED series.
    Returns {"date": str, "value": float} or None on any failure.
    """
    try:
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        lines = response.text.strip().splitlines()
        for row in reversed(lines[1:]):
            parts = row.split(",")
            if len(parts) < 2:
                continue
            date_str, value = parts[0], parts[1]
            if value not in (".", ""):
                return {"date": date_str, "value": float(value)}

    except Exception:
        pass

    return None


def fetch_treasury_yields():
    return {
        label: fetch_fred_series(series_id)
        for label, series_id in TREASURY_SERIES.items()
    }


def fetch_sofr():
    try:
        response = requests.get(
            "https://markets.newyorkfed.org/api/rates/sofr/last/1.json",
            timeout=15,
        )
        response.raise_for_status()
        item = response.json()["refRates"][0]
        return {"date": item["effectiveDate"], "value": float(item["percentRate"])}
    except Exception:
        return None


def fetch_additional_market_data():
    return {
        key: fetch_fred_series(series_id)
        for key, series_id in FRED_ADDITIONAL.items()
    }


def build_market_snapshot():
    treasuries = fetch_treasury_yields()
    sofr       = fetch_sofr()
    additional = fetch_additional_market_data()

    spread = None
    t2  = treasuries.get("2Y")
    t10 = treasuries.get("10Y")
    if t2 and t10:
        spread = t10["value"] - t2["value"]

    return {
        "treasuries": treasuries,
        "sofr":       sofr,
        "spread":     spread,
        "additional": additional,
    }


def generate_market_narrative(snapshot):
    """
    Produces a plain-text market summary for injection into the Groq prompt.
    All values safely guarded against None.
    """
    t          = snapshot.get("treasuries", {})
    spread     = snapshot.get("spread")
    additional = snapshot.get("additional", {})

    def safe_pct(item, decimals=2):
        return f"{item['value']:.{decimals}f}%" if item else "N/A"

    def safe_bps(item):
        # FRED OAS series are in percent (0.77 = 77 bps)
        return f"{item['value'] * 100:.0f} bps" if item else "N/A"

    def safe_float(item, decimals=1):
        return f"{item['value']:.{decimals}f}" if item else "N/A"

    lines = [
        f"2Y Treasury:             {safe_pct(t.get('2Y'))}",
        f"5Y Treasury:             {safe_pct(t.get('5Y'))}",
        f"10Y Treasury:            {safe_pct(t.get('10Y'))}",
        f"30Y Treasury:            {safe_pct(t.get('30Y'))}",
        f"SOFR:                    {safe_pct(snapshot.get('sofr'))}",
        f"2Y/10Y Spread:           "
        + (f"{spread:+.2f}% ({'normal' if spread > 0 else 'inverted'} curve)"
           if spread is not None else "N/A"),
        f"IG Credit Spread (OAS):  {safe_bps(additional.get('IG_OAS'))}",
        f"HY Credit Spread (OAS):  {safe_bps(additional.get('HY_OAS'))}",
        f"10Y Inflation Breakeven: {safe_pct(additional.get('BREAKEVEN_10Y'))}",
        f"VIX:                     {safe_float(additional.get('VIX'))}",
    ]

    return "\n".join(lines)
