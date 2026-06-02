{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import requests\
\
from config import TREASURY_SERIES\
\
# -----------------------------------------------------------------------------\
# Treasury Yields\
# -----------------------------------------------------------------------------\
\
def fetch_treasury_yields():\
\
    results = \{\}\
\
    for label, series_id in TREASURY_SERIES.items():\
\
        try:\
\
            url = (\
                f"https://fred.stlouisfed.org/"\
                f"graph/fredgraph.csv?id=\{series_id\}"\
            )\
\
            response = requests.get(\
                url,\
                timeout=15\
            )\
\
            response.raise_for_status()\
\
            lines = response.text.strip().splitlines()\
\
            for row in reversed(lines[1:]):\
\
                date_str, value = row.split(",")\
\
                if value not in (".", ""):\
\
                    results[label] = \{\
                        "date": date_str,\
                        "value": float(value)\
                    \}\
\
                    break\
\
        except Exception:\
\
            results[label] = None\
\
    return results\
\
\
# -----------------------------------------------------------------------------\
# SOFR\
# -----------------------------------------------------------------------------\
\
def fetch_sofr():\
\
    try:\
\
        response = requests.get(\
            "https://markets.newyorkfed.org/api/rates/sofr/last/1.json",\
            timeout=15\
        )\
\
        response.raise_for_status()\
\
        item = response.json()["refRates"][0]\
\
        return \{\
            "date": item["effectiveDate"],\
            "value": float(item["percentRate"])\
        \}\
\
    except Exception:\
\
        return None\
\
\
# -----------------------------------------------------------------------------\
# Market Snapshot\
# -----------------------------------------------------------------------------\
\
def build_market_snapshot():\
\
    treasuries = fetch_treasury_yields()\
\
    sofr = fetch_sofr()\
\
    spread = None\
\
    if (\
        treasuries.get("2Y")\
        and treasuries.get("10Y")\
    ):\
\
        spread = (\
            treasuries["10Y"]["value"]\
            -\
            treasuries["2Y"]["value"]\
        )\
\
    return \{\
        "treasuries": treasuries,\
        "sofr": sofr,\
        "spread": spread\
    \}\
\
\
# -----------------------------------------------------------------------------\
# Narrative\
# -----------------------------------------------------------------------------\
\
def generate_market_commentary(snapshot):\
\
    spread = snapshot["spread"]\
\
    if spread is None:\
        return "Yield curve unavailable."\
\
    if spread > 0.25:\
\
        return (\
            "Positive yield curve supports "\
            "new-money rates, annuity spreads, "\
            "and stable reserve assumptions."\
        )\
\
    if spread < -0.10:\
\
        return (\
            "Inverted yield curve may pressure "\
            "spread products and warrants "\
            "close ALM monitoring."\
        )\
\
    return (\
        "Yield curve remains relatively flat. "\
        "Limited immediate impact on reserves "\
        "or spread-sensitive products."\
    )}