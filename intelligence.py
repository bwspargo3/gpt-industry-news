import re
import json
import time
import functools
import random
import requests
import xml.etree.ElementTree as ET
import html as html_lib

from datetime import datetime, timedelta, timezone
from collections import defaultdict
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

import config
from config import NOISE_PHRASES, NOISE_WHITELIST, SOURCE_MIN_SCORES
from data_sources import (
    SEARCH_QUERIES,
    CARRIER_SEARCH_QUERIES,
    FIRM_SEARCH_QUERIES,
    DIRECT_RSS_FEEDS,
    NEWSAPI_QUERIES,
)
from market_data import generate_market_narrative
from naic_latf import fetch_naic_latf, build_naic_change_log

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "ActuarialIntelligence/1.0"})

BROWSER_HEADERS = {
    "User-Agent":      "ActuarialIntelligence/1.0",
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection":      "keep-alive",
}

GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models"
    "/gemini-2.5-flash-lite:generateContent"
)


# ------------------------------------------------------------------
# 24-hour freshness filter
# Only keeps articles published within the last 24 hours.
# Simple, reliable, and matches how every professional newsletter works.
# No cross-run cache needed — the article date is the single source of truth.
# ------------------------------------------------------------------

def _article_key(article: dict) -> str:
    title = (article.get("title") or "").lower()
    url   = (article.get("url")   or "").lower()
    return re.sub(r"[^a-z0-9]", "", title + url)[:140]


_DATE_FORMATS = [
    "%b %d, %Y",   # Jun 09, 2026  — our standard output format
    "%Y-%m-%d",    # 2026-06-09
    "%B %d, %Y",   # June 09, 2026
]


def _parse_article_date(date_str: str):
    """Returns a date object or None."""
    if not date_str:
        return None
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    return None


def filter_last_24h(articles: list[dict]) -> tuple[list[dict], int]:
    """
    Keeps articles from the last 48 hours (today + 2 prior days).
    Using 48h rather than 24h because:
    - The digest runs at noon CT; yesterday-afternoon articles are 18-30h old
    - UTC date math can make same-day articles appear "yesterday"
    - Articles with unparseable dates are always kept
    Returns (kept, dropped_count).
    """
    today   = datetime.now(timezone.utc).date()
    cutoff  = today - timedelta(days=2)
    kept    = []
    dropped = 0

    for a in articles:
        pub = _parse_article_date(a.get("date") or "")
        if pub is None or pub >= cutoff:
            kept.append(a)
        else:
            dropped += 1

    return kept, dropped


# ------------------------------------------------------------------
# Text utilities
# ------------------------------------------------------------------

def clean_snippet(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_lib.unescape(text)
    text = text.replace("\xa0", " ").replace("\u200b", "")
    return re.sub(r"\s+", " ", text).strip()


# ------------------------------------------------------------------
# Data collection
# ------------------------------------------------------------------

def fetch_newsapi_bulk(queries):
    if not config.NEWSAPI_KEY:
        return []

    cutoff    = datetime.now(timezone.utc) - timedelta(days=config.DAYS_BACK)
    from_date = cutoff.strftime("%Y-%m-%d")
    url       = "https://newsapi.org/v2/everything"

    query_map = defaultdict(list)
    for category, query in queries:
        query_map[query].append(category)

    all_articles = []
    seen         = set()

    for query, categories in query_map.items():
        params = {
            "q":        query,
            "language": "en",
            "sortBy":   "publishedAt",
            "from":     from_date,
            "apiKey":   config.NEWSAPI_KEY,
            "pageSize": 25,
        }
        try:
            resp = SESSION.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            for item in data.get("articles", []):
                title    = (item.get("title") or "").strip()
                url_link = item.get("url") or ""
                if not title:
                    continue

                pub_date = item.get("publishedAt") or ""
                try:
                    dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                    if dt < cutoff:
                        continue
                    date_str = dt.strftime("%b %d, %Y")
                except Exception:
                    continue

                key = re.sub(r"[^a-zA-Z0-9]", "", (title + url_link).lower())[:120]
                if key in seen:
                    continue
                seen.add(key)

                snippet = clean_snippet(item.get("description") or "")[:400]

                for cat in categories:
                    all_articles.append({
                        "title":    title,
                        "url":      url_link,
                        "source":   item.get("source", {}).get("name") or "NewsAPI",
                        "date":     date_str,
                        "snippet":  snippet,
                        "category": cat,
                    })

        except Exception as e:
            print(f"    NewsAPI error [{query[:40]}]: {e}")

    return all_articles


def parse_rss_feed(content, source_name=""):
    cutoff   = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=config.DAYS_BACK)
    articles = []

    try:
        root    = ET.fromstring(content)
        channel = root.find("channel")
        items   = (
            channel.findall("item") if channel is not None
            else root.findall(".//item")
        )
    except ET.ParseError:
        try:
            soup  = BeautifulSoup(content, "lxml-xml")
            items = soup.find_all("item")
            result = []
            for item in items[:config.MAX_ARTICLES_PER_QUERY]:
                t  = item.find("title")
                l  = item.find("link")
                d  = item.find("description")
                p  = item.find("pubDate")
                title    = t.get_text() if t else ""
                link     = l.get_text() if l else ""
                desc     = d.get_text() if d else ""
                pub_date = p.get_text() if p else ""
                try:
                    dt = parsedate_to_datetime(pub_date).replace(tzinfo=None)
                    if dt < cutoff:
                        continue
                    date_str = dt.strftime("%b %d, %Y")
                except Exception:
                    date_str = pub_date
                result.append({
                    "title":   title.strip(),
                    "url":     link.strip(),
                    "source":  source_name,
                    "date":    date_str,
                    "snippet": clean_snippet(desc)[:400],
                })
            return result
        except Exception as e2:
            print(f"    RSS fallback error ({source_name}): {e2}")
            return []

    for item in items[:config.MAX_ARTICLES_PER_QUERY]:
        title    = item.findtext("title",       "").strip()
        link     = item.findtext("link",        "").strip()
        desc     = item.findtext("description", "").strip()
        pub_date = item.findtext("pubDate",     "").strip()
        try:
            dt = parsedate_to_datetime(pub_date).replace(tzinfo=None)
            if dt < cutoff:
                continue
            date_str = dt.strftime("%b %d, %Y")
        except Exception:
            date_str = pub_date

        # Google News RSS descriptions are just "Title - Source" in an <a> tag.
        # Use the cleaner to strip that; fall back to empty rather than repeating title.
        if source_name == "Google News":
            # Strip trailing " - Source Name" from titles
            # e.g. "Pacific Life Re inks deal - Reinsurance News" -> "Pacific Life Re inks deal"
            title = re.sub(r"\s+-\s+[A-Z][A-Za-z &.']+$", "", title).strip()
            snippet = _clean_gnews_description(desc)
            if snippet.lower().strip() == title.lower().strip():
                snippet = ""
        else:
            snippet = clean_snippet(desc)[:400]

        articles.append({
            "title":   title,
            "url":     link,
            "source":  source_name,
            "date":    date_str,
            "snippet": snippet,
        })
    return articles


def fetch_direct_rss(url, source_name):
    try:
        resp = SESSION.get(url, headers=BROWSER_HEADERS, timeout=15)
        resp.raise_for_status()
        return parse_rss_feed(resp.content, source_name)
    except Exception as e:
        print(f"    RSS error [{source_name}]: {e}")
        return []


# Google News RSS blocks generic user-agents with 429/403 when hammered
# in rapid succession from CI IPs. We rotate agents and add a small
# random delay between requests to stay under the rate limit.
_GNEWS_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
]


def _clean_gnews_description(raw: str) -> str:
    """
    Google News RSS description is an HTML anchor containing:
      "Article Title Source Name"  or  "Article Title - Source Name"
    Strip HTML, remove the trailing source attribution (with or without dash),
    and return empty string if the result is just the title repeated.
    """
    if not raw:
        return ""
    text = re.sub(r"<[^>]+>", " ", raw)
    text = re.sub(r"\s+", " ", text).strip()
    # Remove trailing source name — may appear with dash or just space-separated
    # Pattern: optional " - " then 1-4 capitalized words at the end
    text = re.sub(r"\s*-?\s+([A-Z][a-zA-Z&.]+\s*){1,4}$", "", text).strip()
    return text[:400]


def fetch_google_news(query: str, retries: int = 2) -> list[dict]:
    url = (
        "https://news.google.com/rss/search?"
        f"q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
    )
    headers = {
        "User-Agent":      random.choice(_GNEWS_AGENTS),
        "Accept":          "application/rss+xml, application/xml, text/xml, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection":      "keep-alive",
        "Cache-Control":   "no-cache",
    }

    for attempt in range(retries + 1):
        try:
            # Random delay: CI runner IPs share rate limits
            time.sleep(random.uniform(0.5, 1.5))
            resp = SESSION.get(url, headers=headers, timeout=15)

            # 429 — back off and retry with a different agent
            if resp.status_code == 429:
                wait = 5 * (attempt + 1)
                print(f"    Google News 429 [{query[:40]}] — waiting {wait}s")
                time.sleep(wait)
                headers["User-Agent"] = random.choice(_GNEWS_AGENTS)
                continue

            resp.raise_for_status()
            results = parse_rss_feed(resp.content, "Google News")

            # Empty feed from a valid response usually means the query
            # returned no results in the date window — not a dead source
            return results

        except Exception as e:
            if attempt < retries:
                time.sleep(3 * (attempt + 1))
            else:
                print(f"    Google News error [{query[:50]}]: {e}")

    return []


LIFE_KEYWORDS = [
    "life insurance", "annuity", "reinsurance",
    "life insurer", "insurance holding", "long term care",
]


def fetch_edgar_filings():
    articles = []
    try:
        resp = SESSION.get(
            "https://www.sec.gov/cgi-bin/browse-edgar"
            "?action=getcurrent&type=8-K&output=atom&count=100",
            headers={"User-Agent": f"ActuarialIntelligence {config.GMAIL_USER}"},
            timeout=20,
        )
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        ns   = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("atom:entry", ns):
            title   = entry.findtext("atom:title",   "", ns)
            summary = entry.findtext("atom:summary", "", ns)
            if not any(kw in (title + summary).lower() for kw in LIFE_KEYWORDS):
                continue
            link = entry.find("atom:link", ns)
            articles.append({
                "title":    title,
                "url":      link.get("href") if link is not None else "",
                "source":   "SEC EDGAR",
                "date":     datetime.now(timezone.utc).strftime("%b %d, %Y"),
                "snippet":  clean_snippet(summary)[:400],
                "category": "SEC Filings",
            })
    except Exception as e:
        print(f"    EDGAR error: {e}")
    return articles


def collect_news():
    raw           = []
    source_health = {}

    def add(category, items, label):
        source_health[label] = len(items)
        for a in items:
            a.setdefault("category", category)
            raw.append(a)

    print("  NAIC LATF...")
    add("Regulatory", fetch_naic_latf(days_back=config.DAYS_BACK), "NAIC LATF")

    print("  SEC EDGAR...")
    add("SEC Filings", fetch_edgar_filings(), "SEC EDGAR")

    print("  Direct RSS feeds...")
    for category, source, url in DIRECT_RSS_FEEDS:
        add(category, fetch_direct_rss(url, source), source)

    print("  NewsAPI (bulk)...")
    newsapi_articles = fetch_newsapi_bulk(NEWSAPI_QUERIES)
    for a in newsapi_articles:
        a.setdefault("category", "NewsAPI")
        raw.append(a)

    print("  Google News (industry)...")
    for category, query in SEARCH_QUERIES:
        add(category, fetch_google_news(query), f"GNews:{query[:40]}")

    print("  Google News (firms)...")
    for category, query in FIRM_SEARCH_QUERIES:
        add(category, fetch_google_news(query), f"Firm:{query[:40]}")

    print("  Google News (carriers)...")
    for category, query in CARRIER_SEARCH_QUERIES:
        add(category, fetch_google_news(query), f"Carrier:{query[:40]}")

    dead  = [s for s, n in source_health.items() if n == 0]
    total = sum(source_health.values())
    if dead:
        print(f"  ⚠ {len(dead)} dead sources")
    print(f"  Total raw: {total} from {len(source_health)} sources")
    return raw


# ------------------------------------------------------------------
# Deduplication (within-run)
# ------------------------------------------------------------------

def deduplicate_articles(articles):
    seen   = set()
    unique = []
    for a in articles:
        title = (a.get("title") or "").lower()
        url   = (a.get("url")   or "").lower()
        key   = re.sub(r"[^a-z0-9]", "", title + url)[:140]
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(a)
    print(f"  Deduplicated: {len(articles)} → {len(unique)}")
    return unique


# ------------------------------------------------------------------
# Noise filter — now with whitelist override
# ------------------------------------------------------------------

# Sources that publish heavily in P&C/international.
# Standard gate: requires any life/annuity keyword.
LIFE_GATED_SOURCES = {
    "Insurance Journal",
    "Carrier Management",
    "ThinkAdvisor",
    "Pensions & Investments",
    "Federal Register (IRS Life)",
    "Google News",
    "NewsAPI",
}

# Stricter gate for Reinsurance News: the word "reinsurance" alone is
# not sufficient since they cover P&C brokers, specialty, and international
# extensively. Require a *paired* life/annuity term.
REINSURANCE_NEWS_KWS = [
    "life insurance", "life insurer", "life reinsurer",
    "annuity", "asset intensive", "asset-intensive",
    "funded reinsurance", "block reinsurance", "block transaction",
    "pension risk transfer", "longevity reinsurance",
    "life retrocession", "life & annuity", "life and annuity",
    "iul", "myga", "fia", "rila", "pbr", "vm-20", "vm-22", "ldti",
    "mortality", "actuarial", "actuary", "actuaries",
]

@functools.lru_cache(maxsize=512)
def _compile_regex(phrase):
    return re.compile(rf"\b{re.escape(phrase)}\b")

def filter_noise(articles):
    filtered = []
    dropped  = 0
    life_kws = [
        "life insurance", "annuity", "actuarial", "actuary", "actuaries",
        "reserve", "valuation",
        "life reinsurance", "rbc", "ldti", "vm-20", "vm-22", "pbr",
        "mortality", "fia", "rila", "iul", "alm",
        "hedging", "policyholder", "myga", "solvency",
        "life insurer", "pia", "personal income annuity",
        "asset intensive", "asset-intensive", "funded re", "block transaction",
        "pension risk transfer", "longevity", "universal life", "pension",
        "retirement", "insurance holding",
    ]

    for a in articles:
        a["snippet"] = clean_snippet(a.get("snippet") or "")
        text = ((a.get("title") or "") + " " + a["snippet"]).lower()

        # Whitelist check: if any override phrase present, never drop
        # Using word boundaries to avoid false positives
        if not any(_compile_regex(phrase).search(text) for phrase in NOISE_WHITELIST):
            if any(_compile_regex(phrase).search(text) for phrase in NOISE_PHRASES):
                dropped += 1
                continue

        min_hits = SOURCE_MIN_SCORES.get(a.get("source") or "", 0)
        if min_hits > 0:
            if not any(_compile_regex(kw).search(text) for kw in life_kws):
                dropped += 1
                continue

        # Strict gate for Reinsurance News — must mention life/annuity explicitly
        if a.get("source") == "Reinsurance News":
            if not any(_compile_regex(kw).search(text) for kw in REINSURANCE_NEWS_KWS):
                dropped += 1
                continue

        # Standard gate for other high-volume mixed sources
        if a.get("source") in LIFE_GATED_SOURCES:
            if not any(_compile_regex(kw).search(text) for kw in life_kws):
                dropped += 1
                continue

        filtered.append(a)

    print(f"  Noise filter: dropped {dropped}, kept {len(filtered)}")
    return filtered


# ------------------------------------------------------------------
# Scoring and tagging
# ------------------------------------------------------------------

def classify_event(text: str) -> str:
    text = text.lower()
    best_event = "OTHER"
    best_hits  = 0
    for event_type, patterns in config.EVENT_PATTERNS.items():
        hits = sum(1 for p in patterns if p in text)
        if hits > best_hits:
            best_hits  = hits
            best_event = event_type
    return best_event


SOURCE_WEIGHTS = {
    "NAIC LATF":                    12,
    "AM Best News":                 10,
    "SEC EDGAR":                    10,
    "SOA Research Institute":        8,
    "American Academy of Actuaries": 8,
    "LIMRA Newsroom":                8,
    "Reinsurance News":              8,
    "Carrier Management":            6,
    "Life Annuity Specialist":       8,
    "Federal Register (IRS Life)":   7,
    "Federal Register (Treasury)":   6,
    "Moody's":                      10,
    "Mayer Brown":                  10,
    "PwC":                          10,
    "Deloitte":                     10,
    "EY":                           10,
    "Skadden":                      10,
    "Munich Re":                    10,
    "SCOR":                         10,
    "Wink":                         10,
    "Conning":                      10,
}

# Carrier names that get a score boost when they appear in article text.
# These are the carriers most relevant to consulting and market intelligence.
HIGH_VALUE_CARRIERS = [
    "athene", "global atlantic", "corebridge", "brighthouse",
    "lincoln financial", "equitable", "jackson national",
    "fortitude re", "resolution life", "pacific life re",
    "f&g", "fidelity & guaranty", "american equity",
    "talcott", "somerset re", "american national",
]

# High-value consulting, law, and research firms.
HIGH_VALUE_FIRMS = [
    "moody's", "mayer brown", "pwc", "deloitte", "ey", "kpmg",
    "skadden", "munich re", "scor", "wink", "conning",
    "milliman", "oliver wyman", "willis towers watson", "wtw",
]


def _detect_consulting_signals(text: str) -> list[str]:
    """Returns a list of matched consulting signal labels for display."""
    text   = text.lower()
    hits   = []
    for label, patterns in config.CONSULTING_SIGNALS.items():
        if any(p in text for p in patterns):
            hits.append(label)
    return hits


def score_and_tag(articles):
    category_buckets = {}

    for a in articles:
        text = ((a.get("title") or "") + " " + (a.get("snippet") or "")).lower()

        event_type = classify_event(text)
        score      = config.EVENT_SCORES.get(event_type, 0)
        tags       = {event_type}

        score += SOURCE_WEIGHTS.get(a.get("source"), 0)

        for kw, assigned_tags in config.FUNCTION_TAGS.items():
            if kw in text:
                tags.update(assigned_tags)

        if a.get("source") == "NAIC LATF":
            if any(k in text for k in ["report", "faq", "study", "memo", "update",
                                        "impact", "exposure", "draft", "survey", "review"]):
                score += 20
                tags.update(["REGULATORY", "VALUATION"])
                if event_type == "COMMUNITY":
                    a["score"]             = -999
                    a["tags"]              = ["COMMUNITY"]
                    a["impact"]            = "LOW"
                    a["consulting_signals"] = []
                    category_buckets.setdefault(a.get("category", "Other"), []).append(a)
                    continue
            else:
                score += 8
                tags.add("REGULATORY")

        if a.get("source") in (
            "SOA Research Institute", "SOA News", "The Actuary Magazine",
            "American Academy of Actuaries", "NAIC Newsroom",
            "LIMRA Newsroom", "AM Best News", "Milliman Insights",
        ):
            score += 5
            if event_type == "COMMUNITY":
                a["score"]             = -999
                a["tags"]              = ["COMMUNITY"]
                a["impact"]            = "LOW"
                a["consulting_signals"] = []
                category_buckets.setdefault(a.get("category", "Other"), []).append(a)
                continue

        if a.get("category") == "Carrier Intelligence":
            tags.add("CARRIER")

        if "OTHER" in tags and len(tags) > 1:
            tags.discard("OTHER")

        # Boost score for articles mentioning high-value carriers or firms
        # Using word boundaries to avoid false positives (e.g. "ey" in "they")
        if any(_compile_regex(c).search(text) for c in HIGH_VALUE_CARRIERS):
            score += 4
        if any(_compile_regex(f).search(text) for f in HIGH_VALUE_FIRMS):
            score += 5

        # Detect and attach consulting opportunity signals
        signals = _detect_consulting_signals(text)
        if signals:
            score += 3  # Small boost — signals are high-quality articles

        a["score"]             = score
        a["tags"]              = sorted(list(tags)) if tags else ["GENERAL"]
        a["consulting_signals"] = signals
        a["impact"]            = (
            "HIGH"   if score >= config.HIGH_IMPACT_THRESHOLD   else
            "MEDIUM" if score >= config.MEDIUM_IMPACT_THRESHOLD else
            "LOW"
        )

        category_buckets.setdefault(a.get("category", "Other"), []).append(a)

    for cat in category_buckets:
        category_buckets[cat].sort(key=lambda x: x["score"], reverse=True)

    return category_buckets


# ------------------------------------------------------------------
# Consulting signals extraction (for email template)
# ------------------------------------------------------------------

def extract_opportunity_signals(category_buckets: dict) -> list[dict]:
    """
    Returns a flat list of high-signal articles sorted by score,
    for the dedicated Opportunity Signals section in the email.
    De-duplicated — each article appears at most once here.
    """
    seen = set()
    hits = []
    for articles in category_buckets.values():
        for a in articles:
            if not a.get("consulting_signals"):
                continue
            key = _article_key(a)
            if key in seen:
                continue
            seen.add(key)
            hits.append(a)
    hits.sort(key=lambda x: x.get("score", 0), reverse=True)
    return hits[:15]  # Cap at 15 to keep the section tight


# ------------------------------------------------------------------
# Gemini summarization
# ------------------------------------------------------------------

def summarize_with_gemini(category_buckets: dict, market_snapshot: dict) -> str:
    """
    Calls Gemini 2.0 Flash via the REST API (no SDK required).
    Falls back to a plain-text digest if the API call fails.
    """
    market_narrative = generate_market_narrative(market_snapshot)
    naic_delta       = build_naic_change_log(category_buckets.get("Regulatory", []))

    # Build numbered article list so the model can cite sources
    context_lines = []
    article_index = 1

    for cat, articles in category_buckets.items():
        top = [
            a for a in articles
            if a.get("score", 0) >= 5
            and a.get("source") != "NAIC LATF"
        ][:8]
        if not top:
            continue
        context_lines.append(f"\n[{cat}]")
        for a in top:
            tags_str = ", ".join(a.get("tags", []))
            snippet  = (a.get("snippet") or "")[:200]
            source   = a.get("source") or "Unknown"
            context_lines.append(
                f"[{article_index}] [{tags_str}] {a.get('title', '')} ({source})"
                + (f"\n    {snippet}" if snippet else "")
            )
            article_index += 1

    news_context = "\n".join(context_lines) if context_lines else "No significant developments today."

    prompt = f"""You are writing a daily intelligence briefing for senior life and annuity actuaries
and insurance executives.

STRICT RULES — follow every one exactly:
1. One to two sentences per development. State facts only.
2. Never invent, infer, or extrapolate beyond what the articles say.
3. If you reference a specific fact, note the article number in brackets, e.g. [3].
4. Do NOT echo article titles verbatim. Restate in plain professional language.
5. Omit any section with no relevant articles — write "No significant developments."
6. Exclude P&C, health, auto insurance, sports, consumer personal finance,
   and non-US market news unless directly relevant to US life/annuity actuaries.
7. Use **Section Name** markdown for headers. No other markdown.

MARKET DATA (authoritative — always include exact numbers):
{market_narrative}

NAIC LATF NEW DOCUMENTS (include all in Valuation & Reserving):
{naic_delta}

ARTICLES (cite by number):
{news_context}

---
Write the following sections in order. Skip any section with no content.

**Market Pulse**
State today's Treasury yield levels, SOFR, 2Y/10Y spread, and any notable
spread or volatility context relevant to life/annuity pricing and ALM.

**Today's Lead**
One paragraph. The single most important development of the day for a CRO
or CFO of a mid-size US life carrier. Why it matters in plain language.

**Valuation & Reserving**
VM-20, VM-22, PBR, asset adequacy, LDTI, actuarial guidelines.
Include all new NAIC LATF documents listed above.

**Regulatory Developments**
NAIC, LATF, state departments, IRS/DOL rulings.

**Accounting & LDTI**
ASC 944, FASB, LDTI implementation updates.

**Mortality & Experience Studies**
SOA/AAA research, mortality trends, experience studies, GLP-1 developments.

**Reinsurance Market**
Transactions, Bermuda activity, block deals, M&A involving reinsurers.

**Capital & Risk**
RBC actions, rating agency decisions on life/annuity carriers.

**Annuity Market**
FIA, RILA, MYGA sales data, product news, hedging activity.

**Life Product Developments**
IUL, term, whole life pricing, regulatory filings, AG 49.

**Investments & ALM**
Private credit, structured assets, insurer portfolio and ALM news.

**Industry Trends**
AI in insurance, PE consolidation, distribution shifts, longevity trends.

**Carrier Intelligence**
One sentence per named carrier only. Omit carriers with no news today.

**SOA / AAA Research**
New publications and research releases.

**Consulting & Research**
Reports from Milliman, Oliver Wyman, Deloitte, EY, PwC, KPMG, WTW.
"""

    # Retry with exponential backoff — handles free-tier 429s
    max_attempts = 4
    for attempt in range(max_attempts):
        try:
            resp = requests.post(
                GEMINI_ENDPOINT,
                params={"key": config.GEMINI_API_KEY},
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature":     0.1,
                        "maxOutputTokens": 4096,
                    },
                },
                timeout=60,
            )

            if resp.status_code == 429:
                wait = 15 * (2 ** attempt)   # 15s, 30s, 60s, 120s
                print(f"    Gemini 429 — waiting {wait}s (attempt {attempt+1}/{max_attempts})")
                time.sleep(wait)
                continue

            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

        except Exception as e:
            if attempt < max_attempts - 1:
                wait = 10 * (attempt + 1)
                print(f"    Gemini error (attempt {attempt+1}): {e} — retrying in {wait}s")
                time.sleep(wait)
            else:
                print(f"    Gemini error (final attempt): {e}")
                return _fallback_briefing(market_narrative, naic_delta)

    return _fallback_briefing(market_narrative, naic_delta)


def _fallback_briefing(market_narrative: str, naic_delta: str) -> str:
    """Minimal plain-text briefing used if Gemini is unavailable."""
    return (
        "**Market Pulse**\n"
        f"{market_narrative}\n\n"
        "**NAIC LATF**\n"
        f"{naic_delta}\n\n"
        "_Full AI briefing unavailable — Gemini API call failed. "
        "Article feed below contains all collected developments._"
    )
