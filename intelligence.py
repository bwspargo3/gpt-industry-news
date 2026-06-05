import re
import requests
import xml.etree.ElementTree as ET

from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus

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

BROWSER_HEADERS = {
    "User-Agent": "ActuarialIntelligence/1.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}

# ------------------------------------------------------------------
# NAIC LATF scraper (Kept intact - specialized regulatory structure)
# ------------------------------------------------------------------

def fetch_naic_latf():
    articles = []
    try:
        resp = requests.get(
            "https://content.naic.org/cmte_a_latf.htm",
            headers=BROWSER_HEADERS, timeout=20,
        )
        resp.raise_for_status()
        pattern   = re.compile(
            r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
            re.IGNORECASE | re.DOTALL,
        )
        seen = set()
        for m in pattern.finditer(resp.text):
            href = m.group(1).strip()
            text = re.sub(r"<[^>]+>", "", m.group(2)).strip()
            if not any(ext in href.lower() for ext in
                       [".pdf", ".docx", ".doc", ".htm", ".html"]):
                continue
            if len(text) < 10 or href in seen:
                continue
            seen.add(href)
            if href.startswith("/"):
                href = "https://content.naic.org" + href
            elif not href.startswith("http"):
                continue
            if any(kw in text.lower() for kw in [
                "exposure draft", "draft", "proposed", "agenda",
                "minutes", "adopted", "model", "actuarial guideline",
                "vm-", "pbr", "reserve", "annuity", "life",
                "latf", "task force",
            ]):
                articles.append({
                    "title":    f"[NAIC LATF] {text}",
                    "url":      href,
                    "source":   "NAIC LATF",
                    "date":     datetime.utcnow().strftime("%b %d, %Y"),
                    "snippet":  f"Document on NAIC LATF page: {text}",
                    "category": "Regulatory",
                })
        print(f"    NAIC LATF: {len(articles)} documents")
    except Exception as e:
        print(f"    NAIC LATF error: {e}")
    return articles

# ------------------------------------------------------------------
# NewsAPI Fetcher (The primary replacement for HTML scraping)
# ------------------------------------------------------------------

def fetch_newsapi(query, source_name="NewsAPI"):
    if not config.NEWSAPI_KEY:
        return []
    
    articles = []
    from_date = (datetime.utcnow() - timedelta(days=config.DAYS_BACK)).strftime("%Y-%m-%d")
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "from": from_date,
        "apiKey": config.NEWSAPI_KEY,
        "pageSize": config.MAX_ARTICLES_PER_QUERY
    }
    
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("status") == "ok":
            for item in data.get("articles", []):
                title = item.get("title", "")
                url_link = item.get("url", "")
                desc = item.get("description", "") or ""
                source = item.get("source", {}).get("name", source_name)
                pub_date = item.get("publishedAt", "")
                
                try:
                    dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00")).replace(tzinfo=None)
                    date_str = dt.strftime("%b %d, %Y")
                except Exception:
                    date_str = pub_date[:10]
                    
                articles.append({
                    "title": title.strip(),
                    "url": url_link,
                    "source": source,
                    "date": date_str,
                    "snippet": re.sub(r"<[^>]+>", "", desc)[:400],
                })
    except Exception as e:
        print(f"    NewsAPI error [{query[:30]}]: {e}")
        
    return articles

# ------------------------------------------------------------------
# RSS parser
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
                    "snippet": re.sub(r"<[^>]+>", "", desc)[:400],
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
            "snippet": re.sub(r"<[^>]+>", "", desc)[:400],
        })
    return articles

def fetch_direct_rss(url, source_name):
    try:
        resp = requests.get(url, headers=BROWSER_HEADERS, timeout=15)
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
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return parse_rss_feed(resp.content, "Google News")
    except Exception as e:
        print(f"    Google News error [{query[:50]}]: {e}")
        return []

# ------------------------------------------------------------------
# SEC EDGAR (Kept intact - specialized regulatory structure)
# ------------------------------------------------------------------

LIFE_KEYWORDS = [
    "life insurance", "annuity", "reinsurance",
    "life insurer", "insurance holding", "long term care",
]

def fetch_edgar_filings():
    articles = []
    try:
        resp = requests.get(
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
                "snippet":  summary[:400],
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

    print("  NewsAPI...")
    for category, query in NEWSAPI_QUERIES:
        add(category, fetch_newsapi(query), f"NewsAPI:{query[:40]}")

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
        key = re.sub(r"[^a-zA-Z0-9]", "", a["title"].lower())[:80]
        url = a.get("url", "")
        if key in seen or (url and url in seen):
            continue
        seen.add(key)
        if url:
            seen.add(url)
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
        "hedging", "policyholder", "myga", "solvency", "pension",
        "retirement income",
    ]
    for a in articles:
        text = (a["title"] + " " + a.get("snippet", "")).lower()
        if any(phrase in text for phrase in NOISE_PHRASES):
            dropped += 1
            continue
        min_hits = SOURCE_MIN_SCORES.get(a.get("source", ""), 0)
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
        text  = (a["title"] + " " + a.get("snippet", "")).lower()
        score = 0
        tags  = set()

        for kw, weight in config.ACTUARIAL_KEYWORDS.items():
            if kw in text:
                score += weight

        for kw, assigned_tags in config.FUNCTION_TAGS.items():
            if kw in text:
                tags.update(assigned_tags)

        if a.get("source") == "NAIC LATF":
            score += 20
            tags.update(["REGULATORY", "VALUATION"])

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
        top = [a for a in articles if a.get("score", 0) >= 5][:8]
        if not top:
            continue
        context_lines.append(f"\n[{cat}]")
        for a in top:
            tags_str = ", ".join(a.get("tags", []))
            snippet  = a.get("snippet", "")[:200]
            context_lines.append(
                f"- [{tags_str}] {a['title']} ({a['source']})"
                + (f"\n  {snippet}" if snippet else "")
            )

    news_context = (
        "\n".join(context_lines) if context_lines
        else "No significant developments today."
    )

    prompt = f"""
You are writing a daily intelligence briefing for life and annuity actuaries.
This is a news digest — factual summaries only.

RULES:
- Write 1-2 sentences per development summarizing what happened.
- Factual only. No opinions, no recommendations, no consulting framing.
- No phrases like "this matters because", "should consider", "it is important".
- If a section has no relevant articles, write "No significant developments."
- Filter out P&C, health, employee benefits, auto insurance, sports,
  general consumer finance, and unrelated PR.

MARKET DATA:
{market_narrative}

ARTICLES:
{news_context}

Write sections with **Section Name** as the header.

**Market Pulse**
2-3 sentences on today's rate and spread levels. State the numbers plainly.

**Valuation & Reserving**
VM-20, VM-22, PBR, asset adequacy, LDTI, actuarial guidelines.

**Regulatory Developments**
NAIC, LATF, state departments, IRS/DOL. For LATF documents, name the document.

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
                "exposure draft", "draft", "proposed", "agenda",
                "minutes", "adopted", "model", "actuarial guideline",
                "vm-", "pbr", "reserve", "annuity", "life",
                "latf", "task force",
            ]):
                articles.append({
                    "title":    f"[NAIC LATF] {text}",
                    "url":      href,
                    "source":   "NAIC LATF",
                    "date":     datetime.utcnow().strftime("%b %d, %Y"),
                    "snippet":  f"Document on NAIC LATF page: {text}",
                    "category": "Regulatory",
                })
        print(f"    NAIC LATF: {len(articles)} documents")
    except Exception as e:
        print(f"    NAIC LATF error: {e}")
    return articles

# ------------------------------------------------------------------
# RSS parser — tolerant of malformed XML
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
                    "snippet": re.sub(r"<[^>]+>", "", desc)[:400],
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
            "snippet": re.sub(r"<[^>]+>", "", desc)[:400],
        })
    return articles


def fetch_direct_rss(url, source_name):
    try:
        resp = requests.get(url, headers=BROWSER_HEADERS, timeout=15)
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
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return parse_rss_feed(resp.content, "Google News")
    except Exception as e:
        print(f"    Google News error [{query[:50]}]: {e}")
        return []

# ------------------------------------------------------------------
# HTML scrapers
# ------------------------------------------------------------------

def _get_soup(url):
    resp = requests.get(url, headers=BROWSER_HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "lxml")


def _make_article(title, url, source, snippet=""):
    return {
        "title":   title.strip(),
        "url":     url,
        "source":  source,
        "date":    datetime.utcnow().strftime("%b %d, %Y"),
        "snippet": snippet.strip()[:400],
    }


def _generic_scraper(url, source_name, path_keywords, base_url,
                     min_words=4, min_chars=20, life_filter=True):
    life_kws = [
        "life", "annuity", "mortality", "reserve", "valuation",
        "actuari", "reinsurance", "fia", "rila", "iul", "myga",
        "ldti", "pbr", "vm-20", "vm-22", "capital", "alm",
        "insurance", "pension", "retirement",
    ]
    articles = []
    try:
        soup = _get_soup(url)
        seen = set()
        for a in soup.select("a[href]"):
            text = a.get_text(strip=True)
            href = a.get("href", "")
            if len(text) < min_chars or len(text.split()) < min_words:
                continue
            if href in seen:
                continue
            if path_keywords and not any(kw in href for kw in path_keywords):
                continue
            if life_filter and not any(kw in text.lower() for kw in life_kws):
                continue
            full = urljoin(base_url, href) if not href.startswith("http") else href
            if not full.startswith("http"):
                continue
            # Skip nav/utility links
            if any(x in full.lower() for x in
                   ["/author/", "/tag/", "/category/", "/login",
                    "/subscribe", "/contact", "/about", "?s="]):
                continue
            seen.add(href)
            articles.append(_make_article(text, full, source_name,
                                          f"{source_name}: {text}"))
            if len(articles) >= config.MAX_ARTICLES_PER_QUERY:
                break
        print(f"    {source_name}: {len(articles)} items")
    except Exception as e:
        print(f"    {source_name} error: {e}")
    return articles


def scrape_soa_research(url, source_name):
    return _generic_scraper(
        url, source_name,
        path_keywords=["/research/", "/resources/", "/pub/", "/studies/"],
        base_url="https://www.soa.org",
        life_filter=False,  # All SOA content is relevant
    )


def scrape_soa_news(url, source_name):
    return _generic_scraper(
        url, source_name,
        path_keywords=["/news/", "/publications/", "/newsletter/"],
        base_url="https://www.soa.org",
        life_filter=False,
    )


def scrape_naic_newsroom(url, source_name):
    return _generic_scraper(
        url, source_name,
        path_keywords=["/article/", "/news/", "/press/", "/cipr/", "/media/"],
        base_url="https://content.naic.org",
        life_filter=False,
    )


def scrape_limra(url, source_name):
    return _generic_scraper(
        url, source_name,
        path_keywords=["/newsroom/", "/research/", "/press-releases/", "/en/"],
        base_url="https://www.limra.com",
        min_words=3, min_chars=15,
    )


def scrape_thinkadvisor(url, source_name):
    return _generic_scraper(
        url, source_name,
        path_keywords=["/life-health/", "/annuity/", "/insurance/",
                       "/retirement-planning/", "/regulation-compliance/"],
        base_url="https://www.thinkadvisor.com",
        min_words=5, min_chars=25,
    )


def scrape_milliman(url, source_name):
    return _generic_scraper(
        url, source_name,
        path_keywords=["/insight/", "/research/", "/article/", "/upload/",
                       "/publications/"],
        base_url="https://www.milliman.com",
        life_filter=False,  # Milliman content filtered by scoring
    )


def scrape_insurancenewsnet(url, source_name):
    return _generic_scraper(
        url, source_name,
        path_keywords=["/oarticle/", "/article/", "/innarticle/"],
        base_url="https://insurancenewsnet.com",
        min_words=5, min_chars=25,
    )


def scrape_aaa_publications(url, source_name):
    return _generic_scraper(
        url, source_name,
        path_keywords=["/content/", "/publications/", "/issues/",
                       "/reports/", "/practice-notes/"],
        base_url="https://www.actuary.org",
        life_filter=False,
    )


def scrape_ambest_news(url, source_name):
    return _generic_scraper(
        url, source_name,
        path_keywords=["/news/", "/article/", "/research/", "/bestweek/"],
        base_url="https://www.ambest.com",
        life_filter=False,  # AM Best content is inherently relevant
    )


SCRAPERS = {
    "soa_research":     scrape_soa_research,
    "soa_news":         scrape_soa_news,
    "naic_newsroom":    scrape_naic_newsroom,
    "limra_newsroom":   scrape_limra,
    "thinkadvisor":     scrape_thinkadvisor,
    "milliman":         scrape_milliman,
    "insurancenewsnet": scrape_insurancenewsnet,
    "aaa_publications": scrape_aaa_publications,
    "ambest_news":      scrape_ambest_news,
}


def fetch_html_source(url, source_name, scraper_id):
    fn = SCRAPERS.get(scraper_id)
    if not fn:
        print(f"    No scraper for '{scraper_id}'")
        return []
    return fn(url, source_name)

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
        resp = requests.get(
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
                "snippet":  summary[:400],
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

    print("  HTML scrapers...")
    for category, source, url, scraper_id in HTML_SCRAPE_TARGETS:
        add(category, fetch_html_source(url, source, scraper_id), source)

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
        key = re.sub(r"[^a-zA-Z0-9]", "", a["title"].lower())[:80]
        url = a.get("url", "")
        if key in seen or (url and url in seen):
            continue
        seen.add(key)
        if url:
            seen.add(url)
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
        "hedging", "policyholder", "myga", "solvency", "pension",
        "retirement income",
    ]
    for a in articles:
        text = (a["title"] + " " + a.get("snippet", "")).lower()
        if any(phrase in text for phrase in NOISE_PHRASES):
            dropped += 1
            continue
        min_hits = SOURCE_MIN_SCORES.get(a.get("source", ""), 0)
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
        text  = (a["title"] + " " + a.get("snippet", "")).lower()
        score = 0
        tags  = set()

        for kw, weight in config.ACTUARIAL_KEYWORDS.items():
            if kw in text:
                score += weight

        for kw, assigned_tags in config.FUNCTION_TAGS.items():
            if kw in text:
                tags.update(assigned_tags)

        if a.get("source") == "NAIC LATF":
            score += 20
            tags.update(["REGULATORY", "VALUATION"])

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
        top = [a for a in articles if a.get("score", 0) >= 5][:8]
        if not top:
            continue
        context_lines.append(f"\n[{cat}]")
        for a in top:
            tags_str = ", ".join(a.get("tags", []))
            snippet  = a.get("snippet", "")[:200]
            context_lines.append(
                f"- [{tags_str}] {a['title']} ({a['source']})"
                + (f"\n  {snippet}" if snippet else "")
            )

    news_context = (
        "\n".join(context_lines) if context_lines
        else "No significant developments today."
    )

    prompt = f"""
You are writing a daily intelligence briefing for life and annuity actuaries.
This is a news digest — factual summaries only.

RULES:
- Write 1-2 sentences per development summarizing what happened.
- Factual only. No opinions, no recommendations, no consulting framing.
- No phrases like "this matters because", "should consider", "it is important".
- If a section has no relevant articles, write "No significant developments."
- Filter out P&C, health, employee benefits, auto insurance, sports,
  general consumer finance, and unrelated PR.

MARKET DATA:
{market_narrative}

ARTICLES:
{news_context}

Write sections with **Section Name** as the header.

**Market Pulse**
2-3 sentences on today's rate and spread levels. State the numbers plainly.

**Valuation & Reserving**
VM-20, VM-22, PBR, asset adequacy, LDTI, actuarial guidelines.

**Regulatory Developments**
NAIC, LATF, state departments, IRS/DOL. For LATF documents, name the document.

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
