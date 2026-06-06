import re
import html as html_lib
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

NAIC_CACHE_FILE = "naic_latf_cache.json"

BROWSER_HEADERS = {
    "User-Agent": "ActuarialIntelligence/1.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}

NAIC_TTL_DAYS  = 90
NAIC_MAX_ITEMS = 1500

BASE_URL  = "https://content.naic.org"
INDEX_URL = f"{BASE_URL}/cmte_a_latf.htm"


# ------------------------------------------------------------------
# Cache helpers
# ------------------------------------------------------------------

def load_naic_cache():
    try:
        with open(NAIC_CACHE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_naic_cache(state):
    try:
        with open(NAIC_CACHE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"NAIC cache save error: {e}")


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def make_id(url: str) -> str:
    return re.sub(r"[^a-z0-9]", "", url.lower())


def classify_doc_type(text: str) -> str:
    t = text.lower()
    if "impact"                    in t: return "impact_study"
    if "exposure" in t or "draft"  in t: return "exposure_draft"
    if "faq"                       in t: return "faq"
    if "memo"                      in t: return "memo"
    if "report"                    in t: return "report"
    if "update"                    in t: return "update"
    if "study"                     in t: return "study"
    return "other"


def extract_date(text: str):
    m = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    return m.group(1) if m else None


def prune_state(state: dict) -> dict:
    cutoff = datetime.utcnow() - timedelta(days=NAIC_TTL_DAYS)

    def parse(d):
        try:
            return datetime.strptime(d, "%Y-%m-%d")
        except Exception:
            return None

    pruned = {
        k: v for k, v in state.items()
        if not (parse(v.get("date")) and parse(v.get("date")) < cutoff)
    }

    if len(pruned) > NAIC_MAX_ITEMS:
        items = sorted(
            pruned.items(),
            key=lambda x: parse(x[1].get("date")) or datetime.min,
            reverse=True,
        )
        pruned = dict(items[:NAIC_MAX_ITEMS])

    return pruned


def _clean_text(raw: str) -> str:
    """Strip HTML tags and entities, normalize whitespace."""
    stripped  = re.sub(r"<[^>]+>", " ", raw)
    unescaped = html_lib.unescape(stripped)
    return re.sub(r"\s+", " ", unescaped).strip()


def _is_pdf(url: str, content_type: str) -> bool:
    return (
        url.lower().endswith(".pdf")
        or "application/pdf" in content_type.lower()
    )


# ------------------------------------------------------------------
# Main fetcher
# ------------------------------------------------------------------

NAV_NOISE = {
    "committee", "working group", "subgroup", "task force",
    "materials", "membership", "calendar", "forms", "tools",
    "access", "view", "login", "subscribe", "contact",
}


def fetch_naic_latf():
    old_state = load_naic_cache()
    new_state = {}
    new_items = []

    try:
        resp = requests.get(INDEX_URL, headers=BROWSER_HEADERS, timeout=20)
        resp.raise_for_status()

        soup  = BeautifulSoup(resp.text, "lxml")
        links = soup.select("a[href]")

        for a in links:
            text = a.get_text(strip=True)
            href = a.get("href", "")

            if len(text) < 10:
                continue
            if any(n in text.lower() for n in NAV_NOISE):
                continue

            if href.startswith("/"):
                url = BASE_URL + href
            elif href.startswith("http"):
                url = href
            else:
                continue

            doc_id = make_id(url)

            # Already cached — carry forward unchanged
            if doc_id in old_state:
                new_state[doc_id] = old_state[doc_id]
                continue

            # Fetch the linked resource
            try:
                page = requests.get(
                    url, headers=BROWSER_HEADERS,
                    timeout=15, stream=True,
                )
                page.raise_for_status()
                content_type = page.headers.get("Content-Type", "")

                if _is_pdf(url, content_type):
                    # PDF — never read binary body; use link text for everything
                    page.close()
                    page_clean  = ""
                    # Snippet is just the title — clean, no "PDF document:" prefix
                    snippet     = text
                    date_source = text
                else:
                    raw_html    = page.text
                    page_clean  = _clean_text(raw_html)[:1000]
                    snippet     = page_clean[:250]
                    date_source = page_clean

            except Exception:
                continue

            # Classify using link text + cleaned page text only (never binary)
            doc_type = classify_doc_type(text + " " + page_clean)

            if doc_type == "other":
                continue

            record = {
                "id":        doc_id,
                "title":     text,
                "doc_type":  doc_type,
                "committee": "LATF",
                "date":      extract_date(date_source),
                "url":       url,
                "source":    "NAIC LATF",   # FIXED: was missing, caused "(Unknown)" in LLM
                "snippet":   snippet,
            }

            new_state[doc_id] = record
            new_items.append(record)

        merged = prune_state({**old_state, **new_state})
        save_naic_cache(merged)

        print(f"    NAIC LATF new: {len(new_items)} | stored: {len(merged)}")
        return new_items

    except Exception as e:
        print(f"    NAIC LATF error: {e}")
        return []


# ------------------------------------------------------------------
# Change log for LLM prompt
# ------------------------------------------------------------------

def build_naic_change_log(regulatory_articles):
    """
    Builds a structured summary of new NAIC LATF items for the LLM.
    Only processes genuine LATF records (have doc_type key).
    Regular regulatory news articles are ignored here.
    """
    latf_items = [i for i in regulatory_articles if "doc_type" in i]

    if not latf_items:
        return "No new NAIC LATF developments."

    grouped = {}
    for item in latf_items:
        grouped.setdefault(item["doc_type"], []).append(item)

    lines = ["NAIC LATF Changes (since last run):"]
    for k, v in grouped.items():
        lines.append(f"\n[{k.upper()}]")
        for i in v[:10]:
            lines.append(f"- {i['title']}")

    return "\n".join(lines)
