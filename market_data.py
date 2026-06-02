import requests

from config import TREASURY_SERIES

# -----------------------------------------------------------------------------
# Treasury Yields
# -----------------------------------------------------------------------------

def fetch_treasury_yields():

    results = {}

    for label, series_id in TREASURY_SERIES.items():

        try:

            url = (
                f"https://fred.stlouisfed.org/"
                f"graph/fredgraph.csv?id={series_id}"
            )

            response = requests.get(
                url,
                timeout=15
            )

            response.raise_for_status()

            lines = response.text.strip().splitlines()

            for row in reversed(lines[1:]):

                date_str, value = row.split(",")

                if value not in (".", ""):

                    results[label] = {
                        "date": date_str,
                        "value": float(value)
                    }

                    break

        except Exception:

            results[label] = None

    return results


# -----------------------------------------------------------------------------
# SOFR
# -----------------------------------------------------------------------------

def fetch_sofr():

    try:

        response = requests.get(
            "https://markets.newyorkfed.org/api/rates/sofr/last/1.json",
            timeout=15
        )

        response.raise_for_status()

        item = response.json()["refRates"][0]

        return {
            "date": item["effectiveDate"],
            "value": float(item["percentRate"])
        }

    except Exception:

        return None


# -----------------------------------------------------------------------------
# Market Snapshot
# -----------------------------------------------------------------------------

def build_market_snapshot():

    treasuries = fetch_treasury_yields()

    sofr = fetch_sofr()

    spread = None

    if (
        treasuries.get("2Y")
        and treasuries.get("10Y")
    ):

        spread = (
            treasuries["10Y"]["value"]
            -
            treasuries["2Y"]["value"]
        )

    return {
        "treasuries": treasuries,
        "sofr": sofr,
        "spread": spread
    }


# -----------------------------------------------------------------------------
# Narrative
# -----------------------------------------------------------------------------

def generate_market_commentary(snapshot):

    spread = snapshot["spread"]

    if spread is None:
        return "Yield curve unavailable."

    if spread > 0.25:

        return (
            "Positive yield curve supports "
            "new-money rates, annuity spreads, "
            "and stable reserve assumptions."
        )

    if spread < -0.10:

        return (
            "Inverted yield curve may pressure "
            "spread products and warrants "
            "close ALM monitoring."
        )

    return (
        "Yield curve remains relatively flat. "
        "Limited immediate impact on reserves "
        "or spread-sensitive products."
    )
