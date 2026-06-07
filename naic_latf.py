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

NAIC_TTL_DAYS  = 90
NAIC_MAX_ITEMS = 1500

BASE_URL  = "https://content.naic.org"
INDEX_URL = f"{BASE_URL}/cmte_a_latf.htm"

# File extensions that indicate an actual document download.
# ALL legitimate NAIC LATF documents are files.
# ALL navigation/topic/consumer pages are HTML — no file extension.
# This single filter eliminates 100% of the nav noise.
DOCUMENT_EXTENSIONS = (".pdf", ".docx", ".doc", ".xlsx", ".pptx")


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
        print(f"    NAIC cache save error: {e}")


def make_id(url: str) -> str:
    return re.sub(r"[^a-z0-9]", "", url.lower())


# ------------------------------------------------------------------
# Document classification (title-based only)
# ------------------------------------------------------------------

def classify_doc_type(text: str) -> str:
    t = text.lower()
    if "impact"                     in t: return "impact_study"
    if "exposure" in t and "draft"  in t: return "exposure_draft"
    if "faq"                        in t: return "faq"
    if "memo" in t or "memorandum"  in t: return "memo"
    if "report"                     in t: return "report"
    if "update"                     in t: return "update"
    if "study"                      in t: return "study"
    if "minutes"                    in t: return "minutes"
    if "survey"                     in t: return "survey"
    if "review"                     in t: return "review"
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


# ------------------------------------------------------------------
# Main fetcher
# ------------------------------------------------------------------

def fetch_naic_latf():
    """
    Scrapes the NAIC LATF page for document file links ONLY.

    The key design principle: every legitimate LATF document (VM-20 study,
    PBR reports, exposure drafts, memos, minutes) is a file download with
    a .pdf, .docx, or .doc extension.

    Every navigation link (Auto Insurance, Health Insurance, Consumer Search,
    Glossary, Model Laws, committee overview pages, etc.) points to an HTML
    page with no file extension.

    By accepting ONLY file-extension URLs, we eliminate all navigation noise
    without needing to fetch individual pages, check content types, or
    maintain an ever-growing noise phrase list.
    """
    old_state = load_naic_cache()
    new_state = {}
    new_items = []

    try:
        resp = requests.get(INDEX_URL, headers=BROWSER_HEADERS, timeout=20)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")

        seen_urls = set()

        for a in soup.select("a[href]"):
            text = (a.get_text(strip=True) or "").strip()
            href = (a.get("href") or "").strip()

            # Must have meaningful link text
            if len(text) < 6:
                continue

            # Build absolute URL
            if href.startswith("/"):
                url = BASE_URL + href
            elif href.startswith("http"):
                url = href
            else:
                continue

            url_lower = url.lower()

            # --------------------------------------------------------
            # CORE FILTER: only accept actual document file downloads.
            # This eliminates all navigation/topic/consumer page noise.
            # --------------------------------------------------------
            if not any(url_lower.endswith(ext) for ext in DOCUMENT_EXTENSIONS):
                continue

            doc_id = make_id(url)

            # Already in old cache — carry forward unchanged
            if doc_id in old_state:
                new_state[doc_id] = old_state[doc_id]
                continue

            # Duplicate URL found on same page (two links to same file)
            if doc_id in new_state or url in seen_urls:
                continue
            seen_urls.add(url)

            # Classify document type from title alone
            # No need to fetch the file — title is sufficient and avoids
            # reading binary PDF/DOCX content
            doc_type = classify_doc_type(text)
            if doc_type == "other":
                continue

            record = {
                "id":        doc_id,
                "title":     text,
                "doc_type":  doc_type,
                "committee": "LATF",
                "date":      extract_date(text),
                "url":       url,
                "source":    "NAIC LATF",
                "snippet":   text,   # Title IS the snippet — clean, no binary
            }

            new_state[doc_id] = record
            new_items.append(record)

        merged = prune_state({**old_state, **new_state})
        save_naic_cache(merged)

        print(f"    NAIC LATF: {len(new_items)} new | {len(merged)} stored")
        return new_items

    except Exception as e:
        print(f"    NAIC LATF error: {e}")
        return []


# ------------------------------------------------------------------
# Change log for LLM prompt
# ------------------------------------------------------------------

def build_naic_change_log(regulatory_articles):
    """
    Summarises new NAIC LATF documents for the LLM prompt.
    Filters to only genuine LATF records (have a doc_type key).
    """
    latf_items = [i for i in regulatory_articles if "doc_type" in i]

    if not latf_items:
        return "No new NAIC LATF documents."

    grouped = {}
    for item in latf_items:
        grouped.setdefault(item["doc_type"], []).append(item)

    lines = ["NAIC LATF Documents (new since last run):"]
    for k, v in grouped.items():
        lines.append(f"\n[{k.upper()}]")
        for i in v[:10]:
            lines.append(f"- {i['title']}")

    return "\n".join(lines)
