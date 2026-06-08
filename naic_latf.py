import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

NAIC_CACHE_FILE   = "naic_latf_cache.json"
BROWSER_HEADERS   = {
    "User-Agent":      "ActuarialIntelligence/1.0",
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection":      "keep-alive",
}
NAIC_TTL_DAYS  = 90
NAIC_MAX_ITEMS = 1500
BASE_URL       = "https://content.naic.org"
INDEX_URL      = f"{BASE_URL}/cmte_a_latf.htm"
DOCUMENT_EXTS  = (".pdf", ".docx", ".doc", ".xlsx", ".pptx")

MONTH_MAP = {
    "january": "01", "february": "02", "march":    "03",
    "april":   "04", "may":      "05", "june":     "06",
    "july":    "07", "august":   "08", "september":"09",
    "october": "10", "november": "11", "december": "12",
}


# ------------------------------------------------------------------
# Cache helpers
# ------------------------------------------------------------------

def load_naic_cache() -> dict:
    try:
        with open(NAIC_CACHE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_naic_cache(state: dict) -> None:
    try:
        with open(NAIC_CACHE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"    NAIC cache save error: {e}")


def make_id(url: str) -> str:
    return re.sub(r"[^a-z0-9]", "", url.lower())


# ------------------------------------------------------------------
# Date extraction — three-tier hierarchy
# ------------------------------------------------------------------

def _parse_slash_date(date_str: str) -> str | None:
    """M/D, M/D/YY, or M/D/YYYY → YYYY-MM-DD. Two-digit year assumed 20XX."""
    parts = date_str.strip().split("/")
    try:
        if len(parts) == 2:
            month, day = int(parts[0]), int(parts[1])
            year = datetime.now(tz=timezone.utc).year
        elif len(parts) == 3:
            month, day = int(parts[0]), int(parts[1])
            raw = parts[2].strip()
            year = int(raw) if len(raw) == 4 else 2000 + int(raw)
        else:
            return None
        return datetime(year, month, day).strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def extract_date_from_title(text: str) -> tuple[str | None, str]:
    """
    Tier 1 — no HTTP required.

    Handles:
      "Materials (Updated 3/18/26)"          → 2026-03-18
      "Minutes (Updated 4/16)"               → 2026-04-16
      "2024 PBR Review Report"               → 2024-01-01
      "VM-22 Exposure Draft January 2026"    → 2026-01-01
      "March 18, 2026 Meeting Materials"     → 2026-03-18
      "Adopted Model Regulation August 2025" → 2025-08-01
    """
    t = text.strip()

    # "Updated M/D/YY", "Updated M/D/YYYY", "Updated M/D"
    m = re.search(r"\bUpdated\s+(\d{1,2}/\d{1,2}(?:/\d{2,4})?)\b", t, re.IGNORECASE)
    if m:
        result = _parse_slash_date(m.group(1))
        if result:
            return result, "title:updated"

    # "Month D, YYYY"  e.g. "March 18, 2026"
    m = re.search(
        r"\b(January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})\b",
        t, re.IGNORECASE,
    )
    if m:
        mm = MONTH_MAP.get(m.group(1).lower(), "01")
        try:
            return f"{m.group(3)}-{mm}-{int(m.group(2)):02d}", "title:full_date"
        except ValueError:
            pass

    # "Month YYYY"  e.g. "January 2026"
    m = re.search(
        r"\b(January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+(\d{4})\b",
        t, re.IGNORECASE,
    )
    if m:
        mm = MONTH_MAP.get(m.group(1).lower(), "01")
        return f"{m.group(2)}-{mm}-01", "title:month_year"

    # Four-digit year alone  e.g. "2024 PBR Review Report"
    m = re.search(r"\b(20\d{2})\b", t)
    if m:
        return f"{m.group(1)}-01-01", "title:year_only"

    return None, "none"


def extract_date_from_http_headers(url: str) -> str | None:
    """Tier 2 — HEAD request only, no body downloaded."""
    try:
        resp = requests.head(url, headers=BROWSER_HEADERS, timeout=8, allow_redirects=True)
        last_mod = resp.headers.get("Last-Modified", "")
        if last_mod:
            dt = parsedate_to_datetime(last_mod).replace(tzinfo=None)
            return dt.strftime("%Y-%m-%d")
    except Exception:
        pass
    return None


def extract_date_from_pdf_header(url: str) -> str | None:
    """
    Tier 3 — reads first 4 KB of PDF to find /CreationDate or /ModDate.
    PDF date format: D:20260318143022+00'00'
    """
    if not url.lower().endswith(".pdf"):
        return None
    try:
        resp = requests.get(url, headers=BROWSER_HEADERS, timeout=12, stream=True)
        resp.raise_for_status()
        chunk = b""
        for data in resp.iter_content(chunk_size=1024):
            chunk += data
            if len(chunk) >= 4096:
                break
        resp.close()
        text = chunk.decode("latin-1", errors="replace")
        for pattern in [r"/CreationDate\s*\(D:(\d{8})", r"/ModDate\s*\(D:(\d{8})"]:
            m = re.search(pattern, text)
            if m:
                raw = m.group(1)
                try:
                    return datetime(
                        int(raw[0:4]), int(raw[4:6]), int(raw[6:8])
                    ).strftime("%Y-%m-%d")
                except (ValueError, IndexError):
                    pass
    except Exception:
        pass
    return None


def resolve_published_date(title: str, url: str) -> tuple[str | None, str]:
    """
    Applies the three-tier date hierarchy:
      1. Title pattern       (no HTTP)
      2. HTTP Last-Modified  (HEAD only)
      3. PDF binary header   (first 4 KB)

    Returns (date_str, source_label) or (None, "none").
    """
    date, source = extract_date_from_title(title)
    if date:
        return date, source
    date = extract_date_from_http_headers(url)
    if date:
        return date, "http:last_modified"
    date = extract_date_from_pdf_header(url)
    if date:
        return date, "pdf:metadata"
    return None, "none"


# ------------------------------------------------------------------
# Document classification (title only)
# ------------------------------------------------------------------

def classify_doc_type(text: str) -> str:
    t = text.lower()
    if "impact"                    in t: return "impact_study"
    if "exposure" in t and "draft" in t: return "exposure_draft"
    if "faq"                       in t: return "faq"
    if "memo" in t or "memorandum" in t: return "memo"
    if "report"                    in t: return "report"
    if "update"                    in t: return "update"
    if "study"                     in t: return "study"
    if "minutes"                   in t: return "minutes"
    if "survey"                    in t: return "survey"
    if "review"                    in t: return "review"
    if "materials"                 in t: return "materials"
    if "agenda"                    in t: return "agenda"
    return "other"


# ------------------------------------------------------------------
# Cache pruning
# ------------------------------------------------------------------

def prune_state(state: dict) -> dict:
    cutoff = (
        datetime.now(tz=timezone.utc).replace(tzinfo=None) - timedelta(days=NAIC_TTL_DAYS)
    )

    def parse(d: str | None) -> datetime | None:
        if not d:
            return None
        for fmt in ("%Y-%m-%d", "%Y%m"):
            try:
                return datetime.strptime(d, fmt)
            except ValueError:
                continue
        return None

    def best_date(v: dict) -> datetime | None:
        return parse(v.get("published_date")) or parse(v.get("retrieved_date"))

    pruned = {k: v for k, v in state.items() if not (best_date(v) and best_date(v) < cutoff)}

    if len(pruned) > NAIC_MAX_ITEMS:
        items = sorted(
            pruned.items(),
            key=lambda x: best_date(x[1]) or datetime.min,
            reverse=True,
        )
        pruned = dict(items[:NAIC_MAX_ITEMS])

    return pruned


# ------------------------------------------------------------------
# Main fetcher
# ------------------------------------------------------------------

def fetch_naic_latf(days_back: int = 5) -> list[dict]:
    """
    Scrapes the NAIC LATF index page for document file links.

    Only accepts URLs ending in a document extension (.pdf, .docx, etc).
    This single filter eliminates all navigation noise — topic pages,
    consumer tools, and committee overview pages all link to HTML.

    Date filtering (days_back):
      - published_date known and within window  → included
      - published_date known and outside window → excluded (not news)
      - published_date unknown                  → included (can't determine
        age; cache ensures we only see each document once)

    Both published_date and retrieved_date are stored so the feed can
    distinguish when a document was published vs. first discovered.
    """
    old_state  = load_naic_cache()
    new_state  = {}
    new_items  = []
    retrieved  = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

    # Pre-compute the cutoff date string for fast comparison (YYYY-MM-DD sorts lexically)
    cutoff = (
        datetime.now(tz=timezone.utc).replace(tzinfo=None) - timedelta(days=days_back)
    ).strftime("%Y-%m-%d")

    try:
        resp = requests.get(INDEX_URL, headers=BROWSER_HEADERS, timeout=20)
        resp.raise_for_status()

        soup      = BeautifulSoup(resp.text, "lxml")
        seen_urls = set()

        for a in soup.select("a[href]"):
            text = (a.get_text(strip=True) or "").strip()
            href = (a.get("href") or "").strip()

            if len(text) < 6:
                continue

            if href.startswith("/"):
                url = BASE_URL + href
            elif href.startswith("http"):
                url = href
            else:
                continue

            # Only document file downloads — all nav noise is HTML (no extension)
            if not any(url.lower().endswith(ext) for ext in DOCUMENT_EXTS):
                continue

            doc_id = make_id(url)

            # Already cached → carry forward, skip all processing
            if doc_id in old_state:
                new_state[doc_id] = old_state[doc_id]
                continue

            # Duplicate link on same page
            if doc_id in new_state or url in seen_urls:
                continue
            seen_urls.add(url)

            doc_type = classify_doc_type(text)
            if doc_type == "other":
                continue

            published_date, date_source = resolve_published_date(text, url)
            display_date = published_date or retrieved

            record = {
                "id":             doc_id,
                "title":          text,
                "doc_type":       doc_type,
                "committee":      "LATF",
                "published_date": published_date,
                "retrieved_date": retrieved,
                "date_source":    date_source,
                "date":           display_date,
                "url":            url,
                "source":         "NAIC LATF",
                "snippet":        text,
            }

            new_state[doc_id] = record
            new_items.append(record)

        # ----------------------------------------------------------
        # Date window filter
        # Keep:   published_date within days_back, OR date unknown
        # Drop:   published_date known and older than days_back
        #
        # "Date unknown" items are kept because the cache guarantees we
        # only see each document once — if it's not in old_state, it
        # genuinely just appeared on the page.
        # ----------------------------------------------------------
        before_filter = len(new_items)
        new_items = [
            i for i in new_items
            if i.get("published_date") is None          # unknown age → keep
            or i["published_date"] >= cutoff            # within window → keep
        ]
        excluded = before_filter - len(new_items)

        merged = prune_state({**old_state, **new_state})
        save_naic_cache(merged)

        dated = sum(1 for i in new_items if i.get("published_date"))
        print(
            f"    NAIC LATF: {len(new_items)} returned | "
            f"{excluded} outside {days_back}-day window | "
            f"{len(merged)} cached | "
            f"{dated}/{len(new_items)} with published dates"
        )
        return new_items

    except Exception as e:
        print(f"    NAIC LATF error: {e}")
        return []


# ------------------------------------------------------------------
# Change log for LLM prompt
# ------------------------------------------------------------------

def build_naic_change_log(regulatory_articles: list[dict]) -> str:
    """Formats new NAIC LATF documents for the LLM prompt."""
    latf_items = [i for i in regulatory_articles if "doc_type" in i]

    if not latf_items:
        return "No new NAIC LATF documents."

    grouped: dict[str, list] = {}
    for item in latf_items:
        grouped.setdefault(item["doc_type"], []).append(item)

    lines = ["NAIC LATF Documents (new since last run):"]
    for doc_type, items in grouped.items():
        lines.append(f"\n[{doc_type.upper()}]")
        for i in items[:10]:
            pub      = i.get("published_date", "")
            date_str = f"  [{pub}]" if pub else ""
            lines.append(f"- {i['title']}{date_str}")

    return "\n".join(lines)
