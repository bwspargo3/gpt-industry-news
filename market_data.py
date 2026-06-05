import os
import requests
import config

# Use the FRED API key from environment, fallback to a default if necessary
FRED_API_KEY = os.getenv("FRED_API_KEY", "demo")

def fetch_fred_series(series_id):
    """
    Queries the FRED API for the most recent observation of a given series.
    Safely catches missing values and handles holiday string placeholders.
    """
    try:
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": series_id,
            "sort_order": "desc",
            "limit": 1,
            "file_type": "json",
            "api_key": FRED_API_KEY
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        observations = data.get("observations", [])
        if observations:
            obs = observations[0]
            # Handle cases where FRED returns '.' for missing/holiday data points
            if obs["value"] == ".":
                return None
            return {
                "date": obs["date"],
                "value": float(obs["value"])
            }
    except Exception as e:
        print(f"    Error fetching FRED series {series_id}: {e}")
    return None

def fetch_sofr():
    """
    Bypasses the NY Fed firewall by pulling SOFR directly from FRED 
    via the dedicated 'SOFR' tracking series.
    """
    try:
        result = fetch_fred_series("SOFR")
        if not result:
            print("    Warning: SOFR data returned None from FRED.")
        return result
    except Exception as e:
        print(f"    Error in fetch_sofr: {e}")
        return None

def fetch_macro_indicators():
    """
    Fetches macroeconomic data from FRED for asset adequacy and assumption governance.
    """
    try:
        return {
            "unemployment": fetch_fred_series("UNRATE"),
            "mortgage_30y": fetch_fred_series("MORTGAGE30US")
        }
    except Exception as e:
        print(f"    Error fetching macro indicators: {e}")
        return {}

def build_market_data():
    """
    Main data aggregation pipeline that loops through configurations dynamically.
    Ensures that adding or editing metrics in config.py auto-updates the engine.
    """
    print("Gathering market data context programmatically...")
    
    # Pull core treasuries dynamically from config mapping
    treasuries = {}
    for label, series_id in config.TREASURY_SERIES.items():
        treasuries[label] = fetch_fred_series(series_id)
        
    # Pull credit spreads and volatility dynamically from config mapping
    additional = {}
    for label, series_id in config.FRED_ADDITIONAL.items():
        additional[label] = fetch_fred_series(series_id)
        
    # Calculate 2Y/10Y yield spread dynamically if both metrics are valid
    spread = None
    if treasuries.get("10Y") and treasuries.get("2Y"):
        spread = treasuries["10Y"]["value"] - treasuries["2Y"]["value"]
        
    return {
        "treasuries": treasuries,
        "sofr": fetch_sofr(),
        "spread": spread,
        "additional": additional,
        "macro": fetch_macro_indicators()
    }
