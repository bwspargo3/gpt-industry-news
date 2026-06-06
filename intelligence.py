import re
import requests
import xml.etree.ElementTree as ET
import html as html_lib

from datetime import datetime, timedelta
from collections import defaultdict
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus, urljoin

from bs4 import BeautifulSoup
from groq import Groq

import config
from config import NOISE_PHRASES, SOURCE_MIN_SCORES
from data_sources import (
    SEARCH_QUERIES,
    CARRIER_SEARCH_QUERIES,
    DIRECT_RSS_FEEDS,
    NEWSAPI_QUERIES,
)
from market_data import generate_market_narrative
from naic_latf import fetch_naic_latf, build_naic_change_log


SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "ActuarialIntelligence/1.0"})

BROWSER_HEADERS = {
    "User-Agent": "ActuarialIntelligence/1.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}


# ------------------------------------------------------------------
# Snippet cleaning
# ------------------------------------------------------------------

def clean_snippet(text: str) -> str:
    """
    Strips HTML tags, unescapes HTML entities (&nbsp; etc.),
    removes non-breaking spaces, normalizes whitespace.
    """
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_lib.unescape(text)
    text = text.replace("\xa0", " ").replace("\u200b", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ------------------------------------------------------------------
# NewsAPI
# ------------------------------------------------------------------

def fetch_newsapi_bulk(queries):
    if not config.NEWSAPI_KEY:
        return []

    cutoff    = datetime.utcnow() - timedelta(days=config.DAYS_BACK)
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

                # Client-side date filter — NewsAPI free tier sometimes
                # returns articles older than the `from` param
                pub_date = item.get("publishedAt") or ""
                try:
                    dt = datetime.fromisoformat(
                        pub_date.replace("Z", "+00:00")
                    ).replace(tzinfo=None)
                    if dt < cutoff:
                        continue
                    date_str = dt.strftime("%b %d, %Y")
                except Exception:
                    # If we can't parse the date, skip — avoids stale content
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


# ------------------------------------------------------------------
# RSS parser — tolerant of malformed XML, cleans snippets
# ------------------------------------------------------------------

def parse_rss_feed(content, source_name=""):
    cutoff   = datetime.utcnow() - timedelta(days=config.DAYS_BACK)
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
            soup   = BeautifulSoup(content, "lxml-xml")
            items  = soup.find_all("item")
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
        articles.append({
            "title":   title,
            "url":     link,
            "source":  source_name,
            "date":    date_str,
            "snippet": clean_snippet(desc)[:400],  # FIXED: was missing unescape
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


def fetch_google_news(query):
    url = (
        "https://news.google.com/rss/search?"
        f"q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
    )
    try:
        resp = SESSION.get(url, timeout=15)
        resp.raise_for_status()
        return parse_rss_feed(resp.content, "Google News")
    except Exception as e:
        print(f"    Google News error [{query[:50]}]: {e}")
        return []


# ------------------------------------------------------------------
# SEC EDGAR
# ------------------------------------------------------------------

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
                "date":     datetime.utcnow().strftime("%b %d, %Y"),
                "snippet":  clean_snippet(summary)[:400],
                "category": "SEC Filings",
            })
    except Exception as e:
        print(f"    EDGAR error: {e}")
    return articles


# ------------------------------------------------------------------
# Collect all news
# ------------------------------------------------------------------

def collect_news():
    raw          = []
    source_health = {}

    def add(category, items, label):
        source_health[label] = len(items)
        for a in items:
            a.setdefault("category", category)
            raw.append(a)

    print("  NAIC LATF...")
    add("Regulatory", fetch_naic_latf(), "NAIC LATF")

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
# Deduplication
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
# Noise filter
# ------------------------------------------------------------------

def filter_noise(articles):
    filtered = []
    dropped  = 0

    life_kws = [
        "life insurance", "annuity", "actuari", "reserve", "valuation",
        "reinsurance", "rbc", "ldti", "vm-20", "vm-22", "pbr",
        "mortality", "fia", "rila", "iul", "alm", "capital",
        "hedging", "policyholder", "myga", "solvency",
        "life insurer", "life reinsurance",
    ]

    for a in articles:
        a["snippet"] = clean_snippet(a.get("snippet") or "")

        text = ((a.get("title") or "") + " " + a["snippet"]).lower()

        if any(phrase in text for phrase in NOISE_PHRASES):
            dropped += 1
            continue

        min_hits = SOURCE_MIN_SCORES.get(a.get("source") or "", 0)
        if min_hits > 0:
            if not any(kw in text for kw in life_kws):
                dropped += 1
                continue

        filtered.append(a)

    print(f"  Noise filter: dropped {dropped}, kept {len(filtered)}")
    return filtered


# ------------------------------------------------------------------
# Score and tag
# ------------------------------------------------------------------

def score_and_tag(articles):
    category_buckets = {}

    for a in articles:
        text  = ((a.get("title") or "") + " " + (a.get("snippet") or "")).lower()
        score = 0
        tags  = set()

        for kw, weight in config.ACTUARIAL_KEYWORDS.items():
            if kw in text:
                score += weight

        for kw, assigned_tags in config.FUNCTION_TAGS.items():
            if kw in text:
                tags.update(assigned_tags)

        if a.get("source") == "NAIC LATF":
            # source field now correctly set in naic_latf.py
            if any(k in text for k in [
                "report", "faq", "study", "memo", "update", "impact",
                "exposure", "draft",
            ]):
                score += 20
                tags.update(["REGULATORY", "VALUATION"])
            else:
                score += 8
                tags.add("REGULATORY")

        if a.get("source") in (
            "SOA Research Institute", "SOA News", "The Actuary Magazine",
            "American Academy of Actuaries", "NAIC Newsroom",
            "LIMRA Newsroom", "AM Best News", "Milliman Insights",
        ):
            score += 5

        if a.get("category") == "Carrier Intelligence":
            tags.add("CARRIER")

        a["score"]  = score
        a["tags"]   = sorted(tags) if tags else ["GENERAL"]
        a["impact"] = (
            "HIGH"   if score >= config.HIGH_IMPACT_THRESHOLD   else
            "MEDIUM" if score >= config.MEDIUM_IMPACT_THRESHOLD else
            "LOW"
        )
        cat = a.get("category", "Other")
        category_buckets.setdefault(cat, []).append(a)

    for cat in category_buckets:
        category_buckets[cat].sort(key=lambda x: x["score"], reverse=True)

    return category_buckets


# ------------------------------------------------------------------
# Groq summary
# ------------------------------------------------------------------

def summarize_with_groq(category_buckets, market_snapshot):
    client           = Groq(api_key=config.GROQ_API_KEY)
    market_narrative = generate_market_narrative(market_snapshot)

    context_lines = []

    for cat, articles in category_buckets.items():
        # FIXED: exclude NAIC LATF from article context — they are already
        # covered by the NAIC_LATF_DELTA section below. Including them here
        # caused the LLM to echo "PDF document: X" snippets verbatim.
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
                f"- [{tags_str}] {a.get('title', '')} ({source})"
                + (f"\n  {snippet}" if snippet else "")
            )

    news_context = (
        "\n".join(context_lines) if context_lines
        else "No significant developments today."
    )

    naic_delta = build_naic_change_log(
        category_buckets.get("Regulatory", [])
    )

    prompt = f"""
You are writing a daily intelligence briefing for life and annuity actuaries.
This is a news digest — factual summaries only.

RULES:
- Write 1-2 sentences per development summarizing what happened.
- Factual only. No opinions, no recommendations, no consulting framing.
- Do NOT echo the article titles or context format back verbatim.
- Do NOT use section headers like [INDUSTRY], [LIFE], [COMPANY] — use
  only the section names listed below.
- If a section has no relevant articles, write "No significant developments."
- Filter out P&C, health, auto insurance, sports, consumer personal finance,
  and international news not relevant to US life/annuity markets.
- Only include developments from the ARTICLES and NAIC_LATF sections below.
  Do not add information from your training data.

MARKET DATA:
{market_narrative}

NAIC LATF NEW DOCUMENTS:
{naic_delta}

ARTICLES:
{news_context}

Write sections using **Section Name** as the header.

**Market Pulse**
2-3 sentences on today's rate and spread levels. State the numbers plainly.

**Valuation & Reserving**
VM-20, VM-22, PBR, asset adequacy, LDTI, actuarial guidelines.
Include any new NAIC LATF documents from the section above.

**Regulatory Developments**
NAIC, LATF, state departments, IRS/DOL.

**Accounting & LDTI**
ASC 944, FASB, LDTI implementation.

**Mortality & Experience Studies**
SOA/AAA research, mortality, experience studies, GLP-1 implications.

**Reinsurance Market**
Transactions, Bermuda, M&A involving reinsurers or life carriers.

**Capital & Risk**
RBC, rating agency actions on life/annuity carriers.

**Annuity Market**
FIA, RILA, MYGA sales data, product news, hedging developments.

**Life Product Developments**
IUL, term, whole life pricing, filings, AG 49.

**Investments & ALM**
Private credit, structured assets, insurer investment and ALM news.

**Industry Trends**
AI in insurance, PE consolidation, distribution shifts, longevity trends.

**Carrier Intelligence**
Named carrier news only. One sentence per carrier. Omit carriers with no news.

**SOA / AAA Research**
New publications and research releases.

**Consulting & Research**
Reports from Milliman, Oliver Wyman, Deloitte, EY, PwC, KPMG, WTW.
"""

    try:
        resp = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_tokens=3000,
        )
        return resp.choices[0].message.content
    except Exception as e:
        print(f"    Groq error: {e}")
        return "Briefing unavailable."
