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
        print(f"    NAIC cache save error: {e}")


# ------------------------------------------------------------------
# Content-type helpers
# ------------------------------------------------------------------

def _is_binary_content(url: str, content_type: str) -> bool:
    """
    Returns True if the URL or Content-Type indicates binary content
    that should never be read as text (PDF, DOCX, ZIP, etc.).
    """
    ct  = content_type.lower()
    url_lower = url.lower()
    return (
        url_lower.endswith((".pdf", ".docx", ".doc", ".xlsx", ".pptx", ".zip"))
        or "application/pdf"              in ct
        or "application/vnd.openxml"      in ct   # DOCX, XLSX, PPTX
        or "application/msword"           in ct   # Legacy DOC
        or "application/octet-stream"     in ct   # Generic binary
        or "application/zip"              in ct
    )


def _is_garbage(text: str) -> bool:
    """
    Returns True if text appears to be binary data, raw JavaScript,
    or other non-human-readable content.
    """
    if not text:
        return True

    sample = text[:400]

    # Known binary file headers
    binary_markers = ["%PDF", "PK!\x03\x04", "\x00\x00\x00", "Content_Types"]
    if any(m in sample for m in binary_markers):
        return True

    # JavaScript / dynamic page content that BeautifulSoup missed
    js_markers = [
        "(function(w,d,", "window.soutronContext", "gtm.js",
        "OfrsWeb", "dataLayer", "googletagmanager",
        "ApplicationBaseUrl", "ApplicationLmsUrl",
    ]
    if any(m in sample for m in js_markers):
        return True

    # High density of non-printable / non-ASCII characters = binary
    weird = sum(
        1 for c in sample
        if ord(c) > 255 or (ord(c) < 32 and c not in "\t\n\r ")
    )
    if sample and (weird / len(sample)) > 0.12:
        return True

    return False


# ------------------------------------------------------------------
# Text cleaning
# ------------------------------------------------------------------

def _clean_text(raw: str) -> str:
    """
    Strips HTML including script/style element CONTENT,
    unescapes HTML entities, normalizes whitespace.

    Uses BeautifulSoup to correctly remove <script>/<style> blocks
    (regex tag-stripping leaves JS code between the tags intact).
    """
    try:
        soup = BeautifulSoup(raw, "lxml")
        # Remove entire elements including their text content
        for tag in soup(["script", "style", "noscript", "meta", "link", "head"]):
            tag.decompose()
        text = soup.get_text(separator=" ")
    except Exception:
        # Fallback if lxml not available
        text = re.sub(r"<[^>]+>", " ", raw)

    text = html_lib.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


# ------------------------------------------------------------------
# Document classification
# ------------------------------------------------------------------

def classify_doc_type(text: str) -> str:
    t = text.lower()
    if "impact"                      in t: return "impact_study"
    if "exposure" in t and "draft"   in t: return "exposure_draft"
    if "faq"                         in t: return "faq"
    if "memo" in t or "memorandum"   in t: return "memo"
    if "report"                      in t: return "report"
    if "update"                      in t: return "update"
    if "study"                       in t: return "study"
    if "minutes"                     in t: return "minutes"
    if "survey"                      in t: return "survey"
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
# Navigation noise filter
# Words/phrases in a link's text that mean it is a nav/utility
# item, not an actuarial document.
# ------------------------------------------------------------------

NAV_NOISE_WORDS = {
    # Generic nav
    "committee", "working group", "subgroup", "task force",
    "materials", "membership", "calendar", "forms", "tools",
    "login", "subscribe", "contact", "sign in",
    # NAIC utility pages that slip through classify_doc_type
    "state disaster",           # "State Disaster Reporting"
    "online fraud",             # "Online Fraud Reporting System"
    "disaster reporting",
    "fraud reporting",
    "library archives",         # "Library Archives and regulatory resources"
    "libraryarchives",
    "see all current",          # "See all Current Exposure Drafts" (nav link)
    "mynaic",                   # myNAIC portal
    "technology applications",  # "Technology Applications (myNAIC)"
    "regulatory resources",     # generic library page
    "proceedings of the naic",  # large compendium, too broad
}

# Actuarial keywords that must appear in the document title.
# Documents with NONE of these are unlikely to be relevant.
ACTUARIAL_TITLE_KEYWORDS = {
    "life", "annuity", "actuarial", "reserve", "pbr",
    "vm-", "rbc", "reinsurance", "mortality", "fia", "rila",
    "iul", "myga", "valuation", "model", "sofr", "libor",
    "principle", "capital", "insurance", "policyholder",
    "group annuity", "impact study", "pilot project",
    "exposure draft", "minutes", "memo", "report",
    "survey", "faq", "guideline",
}


def _is_nav_noise(text: str) -> bool:
    t = text.lower()
    return any(phrase in t for phrase in NAV_NOISE_WORDS)


def _has_actuarial_content(text: str) -> bool:
    t = text.lower()
    return any(kw in t for kw in ACTUARIAL_TITLE_KEYWORDS)


# ------------------------------------------------------------------
# Main fetcher
# ------------------------------------------------------------------

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

            # Basic length check
            if len(text) < 8:
                continue

            # Filter navigation / utility links
            if _is_nav_noise(text):
                continue

            # Must have at least one actuarial keyword in title
            if not _has_actuarial_content(text):
                continue

            # Build absolute URL
            if href.startswith("/"):
                url = BASE_URL + href
            elif href.startswith("http"):
                url = href
            else:
                continue

            doc_id = make_id(url)

            # Already in old cache — carry forward
            if doc_id in old_state:
                new_state[doc_id] = old_state[doc_id]
                continue

            # Already processed this run (duplicate link on page)
            if doc_id in new_state:
                continue

            # --------------------------------------------------------
            # Fetch the linked resource
            # --------------------------------------------------------
            try:
                page = requests.get(
                    url,
                    headers=BROWSER_HEADERS,
                    timeout=15,
                    stream=True,
                )
                page.raise_for_status()
                content_type = page.headers.get("Content-Type", "")

                if _is_binary_content(url, content_type):
                    # Never read binary body — use link text as snippet
                    page.close()
                    page_clean  = ""
                    snippet     = text
                    date_source = text
                else:
                    # Read HTML, strip scripts, clean text
                    raw_html    = page.text

                    # Safety check: server lied about Content-Type
                    if _is_garbage(raw_html[:200]):
                        page_clean  = ""
                        snippet     = text
                        date_source = text
                    else:
                        page_clean  = _clean_text(raw_html)[:1000]
                        date_source = page_clean

                        # Validate cleaned text is usable
                        if _is_garbage(page_clean[:200]):
                            snippet = text
                        else:
                            snippet = page_clean[:250] if page_clean else text

            except Exception:
                continue

            # --------------------------------------------------------
            # Classify document type
            # --------------------------------------------------------
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
                "source":    "NAIC LATF",
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


def make_id(url: str) -> str:
    return re.sub(r"[^a-z0-9]", "", url.lower())


# ------------------------------------------------------------------
# Change log for LLM prompt
# ------------------------------------------------------------------

def build_naic_change_log(regulatory_articles):
    """
    Summarises new NAIC LATF items for injection into the LLM prompt.
    Filters to only genuine LATF records (have a doc_type key).
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
