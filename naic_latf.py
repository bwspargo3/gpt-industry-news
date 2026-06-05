import re
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

# -----------------------------
# CONFIG
# -----------------------------
NAIC_TTL_DAYS = 90
NAIC_MAX_ITEMS = 1500

BASE_URL = "https://content.naic.org"
INDEX_URL = f"{BASE_URL}/cmte_a_latf.htm"


# -----------------------------
# CACHE (STATE STORE)
# -----------------------------
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


# -----------------------------
# HELPERS
# -----------------------------
def make_id(url: str) -> str:
    return re.sub(r"[^a-z0-9]", "", url.lower())


def classify_doc_type(text: str) -> str:
    t = text.lower()

    if "impact" in t:
        return "impact_study"
    if "exposure" in t or "draft" in t:
        return "exposure_draft"
    if "faq" in t:
        return "faq"
    if "memo" in t:
        return "memo"
    if "report" in t:
        return "report"
    if "update" in t:
        return "update"
    if "study" in t:
        return "study"

    return "other"


def extract_date(text: str):
    m = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    if m:
        return m.group(1)
    return None


def prune_state(state: dict) -> dict:
    cutoff = datetime.utcnow() - timedelta(days=NAIC_TTL_DAYS)

    def parse(d):
        try:
            return datetime.strptime(d, "%Y-%m-%d")
        except Exception:
            return None

    # remove old
    pruned = {}
    for k, v in state.items():
        d = parse(v.get("date"))
        if d and d < cutoff:
            continue
        pruned[k] = v

    # cap size (keep newest first)
    def sort_key(item):
        d = parse(item[1].get("date"))
        return d or datetime.min

    if len(pruned) > NAIC_MAX_ITEMS:
        items = sorted(pruned.items(), key=sort_key, reverse=True)
        pruned = dict(items[:NAIC_MAX_ITEMS])

    return pruned


# -----------------------------
# MAIN SCRAPER (STATEFUL DIFF)
# -----------------------------
def fetch_naic_latf():
    old_state = load_naic_cache()
    new_state = {}
    new_items = []

    NAV_NOISE = {
        "committee", "working group", "subgroup", "task force",
        "materials", "membership", "agenda", "minutes",
        "calendar", "forms", "tools", "access", "view"
    }

    try:
        resp = requests.get(INDEX_URL, headers=BROWSER_HEADERS, timeout=20)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
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

            # skip unchanged
            if doc_id in old_state:
                new_state[doc_id] = old_state[doc_id]
                continue

            # fetch page
            try:
                page = requests.get(url, headers=BROWSER_HEADERS, timeout=20)
                page.raise_for_status()
                page_text = page.text
            except Exception:
                continue

            doc_type = classify_doc_type(text + page_text)

            if doc_type == "other":
                continue

            record = {
                "id": doc_id,
                "title": text,
                "doc_type": doc_type,
                "committee": "LATF",
                "date": extract_date(page_text),
                "url": url,
                "snippet": page_text[:250],
            }

            new_state[doc_id] = record
            new_items.append(record)

        # merge old + new
        merged = {**old_state, **new_state}

        # prune
        merged = prune_state(merged)

        save_naic_cache(merged)

        print(f"    NAIC LATF new: {len(new_items)} | stored: {len(merged)}")

        return new_items

    except Exception as e:
        print(f"    NAIC LATF error: {e}")
        return []


# -----------------------------
# CHANGE LOG FOR LLM
# -----------------------------
def build_naic_change_log(new_items):
    if not new_items:
        return "No new NAIC LATF developments."

    grouped = {}

    for item in new_items:
        grouped.setdefault(item["doc_type"], []).append(item)

    lines = ["NAIC LATF Changes (since last run):"]

    for k, v in grouped.items():
        lines.append(f"\n[{k.upper()}]")
        for i in v[:10]:
            lines.append(f"- {i['title']}")

    return "\n".join(lines)
