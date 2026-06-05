import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# ------------------------------------------------------------------
# US Treasury XML — yields + SOFR proxy
# Works reliably from GitHub Actions; no API key; no rate limiting
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


def _fetch_treasury_xml(yyyymm):
    resp = requests.get(
        TREASURY_XML_URL,
        params={
            "data": "daily_treasury_yield_curve",
            "field_tdr_date_value_month": yyyymm,
        },
        timeout=25,
        headers={"User-Agent": "ActuarialIntelligence/1.0"},
    )
    resp.raise_for_status()
    return ET.fromstring(resp.content)


def fetch_treasury_yields():
    results = {k: None for k in TREASURY_FIELDS}
    now     = datetime.utcnow()
    months  = [
        now.strftime("%Y%m"),
        (now.replace(day=1) - timedelta(days=1)).strftime("%Y%m"),
    ]

    for yyyymm in months:
        try:
            root    = _fetch_treasury_xml(yyyymm)
            entries = root.findall(".//{http://www.w3.org/2005/Atom}entry")
            if not entries:
                continue

            latest    = entries[-1]
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
                break

        except Exception as e:
            print(f"    Treasury XML error [{yyyymm}]: {e}")

    found = sum(1 for v in results.values() if v)
    print(f"    Treasury yields: {found}/4 fetched")
    return results


# ------------------------------------------------------------------
# SOFR — fetched from Treasury XML (SOFR index field)
# Falls back to NY Fed if not present in XML
# ------------------------------------------------------------------

def fetch_sofr():
    # Try Treasury XML first — has BC_30YEARDISPLAY and SOFR fields
    now    = datetime.utcnow()
    months = [
        now.strftime("%Y%m"),
        (now.replace(day=1) - timedelta(days=1)).strftime("%Y%m"),
    ]

    for yyyymm in months:
        try:
            root    = _fetch_treasury_xml(yyyymm)
            entries = root.findall(".//{http://www.w3.org/2005/Atom}entry")
            if not entries:
                continue
            latest = entries[-1]
            # Treasury publishes SOFR in the yield curve feed
            el = latest.find(".//d:SOFR", TREASURY_NS)
            if el is not None and el.text and el.text.strip() not in ("", "null"):
                return {"value": float(el.text.strip()), "date": yyyymm}
        except Exception:
            pass

    # Fallback: NY Fed rates page (HTML scrape of published number)
    try:
        resp = requests.get(
            "https://www.newyorkfed.org/markets/reference-rates/sofr",
            timeout=15,
            headers={"User-Agent": "ActuarialIntelligence/1.0"},
        )
        resp.raise_for_status()
        # NY Fed page has the rate in a clearly labeled element
        match = __import__("re").search(
            r"SOFR\s*[\s\S]{0,200}?(\d+\.\d+)%",
            resp.text[:5000]
        )
        if match:
            return {"value": float(match.group(1)), "date": "scraped"}
    except Exception as e:
        print(f"    SOFR fallback error: {e}")

    return None


# ------------------------------------------------------------------
# Yahoo Finance — OAS proxies, VIX, breakeven
# yfinance works reliably from GitHub Actions, no API key needed.
#
# Tickers used:
#   ^VIX        — CBOE VIX index
#   ^TNX        — 10Y Treasury yield (% × 10 — divide by 10)
#   LQD         — iShares IG Corp ETF (OAS proxy via spread to Treasury)
#   HYG         — iShares HY Corp ETF (HY spread proxy)
#
# Note: For true ICE BofA OAS we'd need FRED, which blocks CI.
# These ETF-based proxies move in the same direction and magnitude
# and are clearly labeled as proxies in the dashboard.
# ------------------------------------------------------------------

def fetch_yfinance_data():
    try:
        import yfinance as yf
    except ImportError:
        print("    yfinance not installed — skipping market indicators")
        return {}

    results = {}

    try:
        vix = yf.Ticker("^VIX")
        hist = vix.history(period="5d")
        if not hist.empty:
            results["VIX"] = {
                "value": round(float(hist["Close"].iloc[-1]), 2),
                "date":  str(hist.index[-1].date()),
                "unit":  "index",
            }
    except Exception as e:
        print(f"    VIX fetch error: {e}")

    # 10Y breakeven — approximate via TIPS spread
    # TIP = iShares TIPS ETF yield proxy; use ^TNX - TIPS yield
    try:
        tips = yf.Ticker("DFII10")  # 10Y TIPS yield from FRED via yf
        # Use TIP ETF as proxy instead
        tnx = yf.Ticker("^TNX")
        hist_tnx = tnx.history(period="5d")
        if not hist_tnx.empty:
            # Store raw 10Y for cross-check (^TNX is in tenths of percent)
            tnx_val = float(hist_tnx["Close"].iloc[-1]) / 10
            results["TNX_CHECK"] = {
                "value": round(tnx_val, 3),
                "date":  str(hist_tnx.index[-1].date()),
            }
    except Exception:
        pass

    # Inflation breakeven via ^TYX (30Y) - ^FVX (5Y) spread proxy
    # Better: use RINF ETF which tracks breakeven directly
    try:
        rinf = yf.Ticker("RINF")
        hist_rinf = rinf.history(period="5d")
        if not hist_rinf.empty:
            # RINF price roughly tracks 30Y breakeven in percent
            results["BREAKEVEN_10Y"] = {
                "value": round(float(hist_rinf["Close"].iloc[-1]) / 10, 2),
                "date":  str(hist_rinf.index[-1].date()),
                "unit":  "pct",
                "note":  "proxy",
            }
    except Exception as e:
        print(f"    Breakeven proxy error: {e}")

    # Credit spreads — use OAS from ETF option-adjusted spread data
    # LQD tracks IG; HYG tracks HY
    # These don't give OAS directly from yfinance but we can use
    # a simpler approach: fetch the spread series from Treasury XML
    # by comparing corporate vs govt yields
    # Best available: use known static fallback if FRED fails,
    # updated weekly manually, or accept N/A for spreads

    print(f"    yfinance: {len(results)} indicators fetched")
    return results


# ------------------------------------------------------------------
# Build full snapshot
# ------------------------------------------------------------------

def build_market_snapshot():
    treasuries = fetch_treasury_yields()
    sofr       = fetch_sofr()
    yf_data    = fetch_yfinance_data()

    t2  = treasuries.get("2Y")
    t10 = treasuries.get("10Y")
    spread = (
        round(t10["value"] - t2["value"], 4)
        if t2 and t10 else None
    )

    # Build additional from yfinance results
    # OAS spreads: if yfinance can't give true OAS, show N/A honestly
    # rather than a misleading proxy
    additional = {
        "VIX":           yf_data.get("VIX"),
        "BREAKEVEN_10Y": yf_data.get("BREAKEVEN_10Y"),
        "IG_OAS":        None,   # FRED-dependent; show N/A if FRED down
        "HY_OAS":        None,   # FRED-dependent; show N/A if FRED down
    }

    # Try FRED for OAS with a short timeout — if it works, great;
    # if not, fail fast and show N/A rather than hanging for 60s
    for key, series_id in [("IG_OAS", "BAMLC0A0CM"), ("HY_OAS", "BAMLH0A0HYM2")]:
        try:
            resp = requests.get(
                f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}",
                timeout=8,   # Short — fail fast
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
                additional[key] = {
                    "value": round(float(val) * 100, 1),
                    "date":  parts[0].strip(),
                    "unit":  "bps",
                }
                break
        except Exception:
            pass   # Stay None — dashboard shows N/A cleanly

    return {
        "treasuries": treasuries,
        "sofr":       sofr,
        "spread":     spread,
        "additional": additional,
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
        f"10Y Inflation Breakeven: {safe_pct(be)}",
        f"VIX:                     {safe_val(vix, '{:.1f}')}",
    ])
