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
    entries = root.findall(".//{http://www.w3.org/2005/Atom}entry")
    return entries[-1] if entries else None


def _try_months():
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
# TIPS real yields
# ------------------------------------------------------------------

def fetch_tips_real_yield():
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
# SOFR — three attempts in reliability order
# Attempt 1: Treasury XML (most reliable, same source as yields)
# Attempt 2: NY Fed rates HTML page (more stable than their CSV API)
# Attempt 3: NY Fed CSV (often 503 in CI — last resort)
# ------------------------------------------------------------------

def fetch_sofr():
    """
    Fetch SOFR in reliability order:
    1. FRED series SOFR  — same infrastructure as OAS, works reliably in CI
    2. Treasury XML      — sometimes includes SOFR field
    3. NY Fed HTML page  — scrape fallback
    4. NY Fed CSV API    — frequently 503 in CI, last resort
    """

    # Attempt 1: yfinance — same mechanism that successfully fetches VIX every run
    try:
        import yfinance as yf
        # SOFR 30-day average trades as ^SOFR on some feeds; fallback to EFFR proxy
        for ticker in ["^SOFR", "SOFR=X"]:
            try:
                hist = yf.Ticker(ticker).history(period="5d")
                if not hist.empty:
                    val = round(float(hist["Close"].iloc[-1]), 2)
                    date = str(hist.index[-1].date())
                    if 0.01 < val < 15:
                        print(f"    SOFR from yfinance ({ticker}): {val}%")
                        return {"value": val, "date": date}
            except Exception:
                continue
    except Exception as e:
        print(f"    SOFR yfinance error: {e}")

    # Attempt 2: FRED CSV streamed — read tail only, avoids full-file download timeout
    # The full SOFR CSV is ~8 years of daily data; streaming tail avoids the timeout
    try:
        resp = requests.get(
            "https://fred.stlouisfed.org/graph/fredgraph.csv?id=SOFR",
            timeout=45,
            stream=True,
            headers={"User-Agent": "ActuarialIntelligence/1.0"},
        )
        resp.raise_for_status()
        # Collect chunks until we have the full content (SOFR CSV is ~200KB)
        chunks = []
        total  = 0
        for chunk in resp.iter_content(chunk_size=8192):
            chunks.append(chunk)
            total += len(chunk)
            if total > 300_000:  # 300KB cap — more than enough for full history
                break
        resp.close()
        text  = b"".join(chunks).decode("utf-8", errors="replace")
        lines = text.strip().splitlines()
        for row in reversed(lines[1:]):
            parts = row.split(",")
            if len(parts) < 2:
                continue
            val_str = parts[1].strip()
            if val_str in (".", "", "NA"):
                continue
            val = float(val_str)
            if 0.01 < val < 15:
                print(f"    SOFR from FRED stream: {val}% ({parts[0].strip()})")
                return {"value": val, "date": parts[0].strip()}
    except Exception as e:
        print(f"    SOFR FRED stream error: {e}")

    # Attempt 2: Treasury XML SOFR field
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

    # Attempt 3: NY Fed HTML page
    try:
        resp = requests.get(
            "https://www.newyorkfed.org/markets/reference-rates/sofr",
            timeout=15,
            headers={"User-Agent": "ActuarialIntelligence/1.0"},
        )
        resp.raise_for_status()
        match = re.search(
            r"SOFR[^<]{0,400}?(\d{1,2}\.\d{2})",
            resp.text[:10000],
            re.DOTALL,
        )
        if match:
            val = float(match.group(1))
            if 0.01 < val < 15:
                print(f"    SOFR from NY Fed HTML: {val}%")
                return {"value": val, "date": "scraped"}
    except Exception as e:
        print(f"    SOFR HTML error: {e}")

    # Attempt 4: NY Fed CSV API (frequently 503 in CI)
    try:
        today = datetime.utcnow()
        start = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        url   = (
            "https://markets.newyorkfed.org/read"
            f"?startDt={start}&eventCodes=SOFR"
            "&productCode=50&sort=postDt:-1&format=csv"
        )
        resp  = requests.get(url, timeout=10,
                             headers={"User-Agent": "ActuarialIntelligence/1.0"})
        resp.raise_for_status()
        lines = resp.text.strip().splitlines()
        for line in lines:
            parts = line.split(",")
            if len(parts) >= 2:
                try:
                    val = float(parts[-1].strip())
                    if 0.01 < val < 15:
                        return {"value": val, "date": parts[0].strip()}
                except ValueError:
                    continue
    except Exception as e:
        print(f"    SOFR CSV error: {e}")

    print("    SOFR: all sources failed — showing N/A")
    return None


# ------------------------------------------------------------------
# VIX via yfinance
# ------------------------------------------------------------------

def fetch_vix():
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
# OAS spreads via FRED
# ------------------------------------------------------------------

def fetch_oas_spreads():
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
                    "value": round(float(val) * 100, 1),
                    "date":  parts[0].strip(),
                    "unit":  "bps",
                }
                break
        except Exception:
            pass

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
