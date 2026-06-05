import re
import requests
import xml.etree.ElementTree as ET

from datetime import datetime, timedelta
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
    HTML_SCRAPE_TARGETS,
)
from market_data import generate_market_narrative

# ---------------------------------------------------------------------
# NAIC LATF Scraper
# ---------------------------------------------------------------------

LATF_URL = "https://content.naic.org/cmte_a_latf.htm"

def fetch_naic_latf():
    articles = []
    headers  = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; ActuarialIntelligence/1.0; "
            f"+{config.GMAIL_USER})"
        )
    }
    try:
        response = requests.get(LATF_URL, headers=headers, timeout=20)
        response.raise_for_status()
        html = response.text

        pattern = re.compile(
            r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
            re.IGNORECASE | re.DOTALL,
        )
        seen_urls = set()

        for match in pattern.finditer(html):
            href = match.group(1).strip()
            text = re.sub(r"<[^>]+>", "", match.group(2)).strip()

            if not any(ext in href.lower() for ext in
                       [".pdf", ".docx", ".doc", ".htm", ".html"]):
                continue
            if len(text) < 10:
                continue
            if href in seen_urls:
                continue
            seen_urls.add(href)

            if href.startswith("/"):
                href = "https://content.naic.org" + href
            elif not href.startswith("http"):
                continue

            text_lower = text.lower()
            if any(kw in text_lower for kw in [
                "exposure draft", "draft", "proposed", "agenda", "minutes",
                "adopted", "model", "actuarial guideline", "vm-", "vm20",
                "vm22", "pbr", "reserve", "annuity", "life", "latf",
                "task force",
            ]):
                articles.append({
                    "title":   f"[NAIC LATF] {text}",
                    "url":     href,
                    "source":  "NAIC LATF",
                    "date":    datetime.utcnow().strftime("%b %d, %Y"),
                    "snippet": f"Document on NAIC LATF page: {text}",
                    "category": "Regulatory",
                })

        print(f"    NAIC LATF: {len(articles)} documents found")

    except Exception as e:
        print(f"    NAIC LATF error: {e}")

    return articles

# ---------------------------------------------------------------------
# RSS Feed Parser
# ---------------------------------------------------------------------

def parse_rss_feed(content, source_name=""):
    articles = []
    cutoff   = datetime.utcnow() - timedelta(days=config.DAYS_BACK)

    try:
        root    = ET.fromstring(content)
        channel = root.find("channel")
        items   = (
            channel.findall("item")
            if channel is not None
            else root.findall(".//item")
        )

        for item in items[:config.MAX_ARTICLES_PER_QUERY]:
            title    = item.findtext("title",       "").strip()
            link     = item.findtext("link",        "").strip()
            desc     = item.findtext("description", "").strip()
            pub_date = item.findtext("pubDate",     "").strip()

            try:
                dt = parsedate_to_datetime(pub_date).replace(tzinfo=None)
                if dt < cutoff:
                    continue
                date_string = dt.strftime("%b %d, %Y")
            except Exception:
                date_string = pub_date

            articles.append({
                "title":   title,
                "url":     link,
                "source":  source_name,
                "date":    date_string,
                "snippet": re.sub(r"<[^>]+>", "", desc)[:400],
            })

    except Exception as e:
        print(f"    RSS parse error ({source_name}): {e}")

    return articles

# ---------------------------------------------------------------------
# Google News
# ---------------------------------------------------------------------

def fetch_google_news(query):
    url = (
        "https://news.google.com/rss/search?"
        f"q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
    )
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return parse_rss_feed(response.content, "Google News")
    except Exception as e:
        print(f"    Google News error [{query[:50]}]: {e}")
        return []

# ---------------------------------------------------------------------
# Direct RSS
# ---------------------------------------------------------------------

def fetch_direct_rss(url, source_name):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return parse_rss_feed(response.content, source_name)
    except Exception as e:
        print(f"    RSS error [{source_name}]: {e}")
        return []

# ---------------------------------------------------------------------
# HTML Scraping Fallback
# ---------------------------------------------------------------------

def fetch_heuristic_html(url, source_name):
    articles = []
    headers  = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup      = BeautifulSoup(response.text, "lxml")
        seen_urls = set()

        for a in soup.find_all("a"):
            text = a.get_text(strip=True)
            href = a.get("href")

            if not href or len(text) < 30 or len(text.split()) < 5:
                continue

            full_url = urljoin(url, href)
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)

            if any(x in full_url.lower() for x in
                   ["/contact", "/about", "/login", "/subscribe",
                    "policy", "/author/"]):
                continue

            articles.append({
                "title":   text,
                "url":     full_url,
                "source":  source_name,
                "date":    datetime.utcnow().strftime("%b %d, %Y"),
                "snippet": f"Recently published on {source_name}.",
            })

            if len(articles) >= config.MAX_ARTICLES_PER_QUERY:
                break

    except Exception as e:
        print(f"    HTML scrape error [{source_name}]: {e}")

    return articles

# ---------------------------------------------------------------------
# SEC EDGAR
# ---------------------------------------------------------------------

LIFE_KEYWORDS = [
    "life insurance", "annuity", "reinsurance",
    "life insurer", "insurance holding", "long term care",
]

def fetch_edgar_filings():
    articles = []
    url      = (
        "https://www.sec.gov/cgi-bin/browse-edgar"
        "?action=getcurrent&type=8-K&output=atom&count=100"
    )
    try:
        headers  = {"User-Agent": f"Actuarial Intelligence {config.GMAIL_USER}"}
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        ns   = {"atom": "http://www.w3.org/2005/Atom"}

        for entry in root.findall("atom:entry", ns):
            title   = entry.findtext("atom:title",   "", ns)
            summary = entry.findtext("atom:summary", "", ns)
            text    = (title + " " + summary).lower()

            if not any(kw in text for kw in LIFE_KEYWORDS):
                continue

            link = entry.find("atom:link", ns)
            articles.append({
                "title":   title,
                "url":     link.get("href") if link is not None else "",
                "source":  "SEC EDGAR",
                "date":    datetime.utcnow().strftime("%b %d, %Y"),
                "snippet": summary[:400],
                "category": "SEC Filings",
            })

    except Exception as e:
        print(f"    EDGAR error: {e}")

    return articles

# ---------------------------------------------------------------------
# Collect All News
# ---------------------------------------------------------------------

def collect_news():
    raw_articles  = []
    source_health = {}

    def add(category, items, label):
        source_health[label] = len(items)
        for a in items:
            a.setdefault("category", category)
            raw_articles.append(a)

    print("  NAIC LATF...")
    add("Regulatory", fetch_naic_latf(), "NAIC LATF")

    print("  SEC EDGAR...")
    add("SEC Filings", fetch_edgar_filings(), "SEC EDGAR")

    print("  Direct RSS feeds...")
    for category, source, url in DIRECT_RSS_FEEDS:
        items = fetch_direct_rss(url, source)
        add(category, items, source)

    print("  Google News (industry queries)...")
    for category, query in SEARCH_QUERIES:
        items = fetch_google_news(query)
        add(category, items, f"GNews:{query[:40]}")

    print("  Google News (carrier watchlist)...")
    for category, query in CARRIER_SEARCH_QUERIES:
        items = fetch_google_news(query)
        add(category, items, f"Carrier:{query[:40]}")

    print("  HTML scraping (fallback sources)...")
    for category, source, url in HTML_SCRAPE_TARGETS:
        items = fetch_heuristic_html(url, source)
        add(category, items, source)

    # Report dead sources
    dead = [s for s, n in source_health.items() if n == 0]
    if dead:
        print(f"  ⚠ {len(dead)} dead sources: {', '.join(dead[:8])}")

    total = sum(source_health.values())
    print(f"  Total raw articles: {total} from {len(source_health)} sources")

    return raw_articles

# ---------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------

def deduplicate_articles(articles):
    seen   = set()
    unique = []
    for a in articles:
        key = re.sub(r"[^a-zA-Z0-9]", "", a["title"].lower())[:80]
        if key in seen or a.get("url", "") in seen:
            continue
        seen.add(key)
        if a.get("url"):
            seen.add(a["url"])
        unique.append(a)
    print(f"  Deduplicated: {len(articles)} → {len(unique)}")
    return unique

# ---------------------------------------------------------------------
# Noise Filter
# ---------------------------------------------------------------------

def filter_noise(articles):
    filtered = []
    dropped  = 0

    for a in articles:
        text = (a["title"] + " " + a.get("snippet", "")).lower()

        # Content-based noise
        if any(phrase in text for phrase in NOISE_PHRASES):
            dropped += 1
            continue

        # Source-level minimum keyword hit
        min_score = SOURCE_MIN_SCORES.get(a.get("source", ""), 0)
        if min_score > 0:
            hits = sum(
                1 for kw in [
                    "life insurance", "annuity", "actuari",
                    "reserve", "valuation", "reinsurance", "rbc",
                    "ldti", "vm-20", "vm-22", "pbr", "mortality",
                    "fia", "rila", "iul", "alm", "capital",
                    "hedging", "policyholder",
                ]
                if kw in text
            )
            if hits == 0:
                dropped += 1
                continue

        filtered.append(a)

    print(f"  Noise filter: dropped {dropped}, kept {len(filtered)}")
    return filtered

# ---------------------------------------------------------------------
# Score and Tag
# ---------------------------------------------------------------------

def score_and_tag(articles):
    category_buckets = {}

    for a in articles:
        text = (a["title"] + " " + a.get("snippet", "")).lower()

        score = 0
        tags  = set()

        for kw, weight in config.ACTUARIAL_KEYWORDS.items():
            if kw in text:
                score += weight

        for kw, assigned_tags in config.FUNCTION_TAGS.items():
            if kw in text:
                tags.update(assigned_tags)

        # Source boosts
        if a.get("source") == "NAIC LATF":
            score += 20
            tags.update(["REGULATORY", "VALUATION"])

        if a.get("source") in (
            "SOA News", "SOA Research",
            "American Academy of Actuaries",
            "NAIC Newsroom", "LIMRA",
            "AM Best Ratings", "AM Best News",
        ):
            score += 5

        if a.get("category") == "Carrier Intelligence":
            tags.add("CARRIER")

        if not tags:
            tags.add("GENERAL")

        a["score"]  = score
        a["tags"]   = sorted(tags)
        a["impact"] = (
            "HIGH"   if score >= config.HIGH_IMPACT_THRESHOLD   else
            "MEDIUM" if score >= config.MEDIUM_IMPACT_THRESHOLD else
            "LOW"
        )

        cat = a.get("category", "Other")
        category_buckets.setdefault(cat, []).append(a)

    # Sort each bucket by score descending
    for cat in category_buckets:
        category_buckets[cat].sort(key=lambda x: x["score"], reverse=True)

    return category_buckets

# ---------------------------------------------------------------------
# Groq Summarization
# ---------------------------------------------------------------------

def summarize_with_groq(category_buckets, market_snapshot):
    client           = Groq(api_key=config.GROQ_API_KEY)
    market_narrative = generate_market_narrative(market_snapshot)

    # Build article context — high/medium impact only, top 6 per category
    context_lines = []
    for cat, articles in category_buckets.items():
        top = [
            a for a in articles
            if a["impact"] in ("HIGH", "MEDIUM")
            and a.get("score", 0) >= 5
        ][:6]
        if top:
            context_lines.append(f"\n[{cat}]")
            for a in top:
                tags_str = ", ".join(a.get("tags", []))
                context_lines.append(
                    f"- [{tags_str}] {a['title']} ({a['source']})"
                )

    news_context = (
        "\n".join(context_lines)
        if context_lines
        else "No major developments today."
    )

    prompt = f"""
You are a senior life and annuity actuarial consultant at Actuarial Resources
Corporation (ARC), a Springline company. ARC provides actuarial consulting
to life insurance and annuity carriers, primarily mid-size companies, with
strong relationships at Kansas City-area insurers including Ameritas, Securian,
Kansas City Life, Country Financial, BMI, Midland National, and North American.

Your specialties: valuation (VM-20/VM-22/PBR), LDTI/ASC 944, reinsurance,
experience studies, RBC, ALM, and life/annuity product development.

AUDIENCE: This is your personal daily briefing before client calls.
Be direct and specific. Skip anything with no consulting angle.
Do not repeat the same development across sections.

FILTER OUT completely: P&C, health, employee benefits, auto insurance,
consumer personal finance, sports, unrelated PR, offshore wind, general macro
unless it directly affects life/annuity reserves, pricing, capital, or reinsurance.

MARKET DATA:
{market_narrative}

TOP DEVELOPMENTS:
{news_context}

Write the following sections using **Section Name** as headers.
If a section has nothing material, write one sentence saying so.

**Market Pulse**
3-4 sentences. Translate rates, OAS spreads (note: IG ~77 bps and HY ~283 bps
are near post-crisis tights), VIX, and curve into specific actuarial
implications for new-money rates, FIA/RILA hedging costs, ALM positioning,
and cash flow testing discount rates.

**This Week's Key Themes**
3-5 bullets. Each: one sentence on what happened + one sentence on why it
matters to an ARC consultant. Must be specific to this week.

**High Impact Developments**
Near-term implications for reserving, capital, or regulatory compliance only.
For each: (1) what happened, (2) which carrier types are affected,
(3) what ARC should prepare.

**Valuation & Reserving** [VALUATION]
VM-20, VM-22, PBR, asset adequacy, LDTI. Flag LATF documents and deadlines.

**Regulatory Developments** [REGULATORY]
LATF, NAIC, IRS/DOL, actuarial guidelines. Flag comment deadlines.

**Accounting & LDTI** [ACCOUNTING]
ASC 944 issues, restatements, FASB guidance.

**Mortality & Experience Studies** [EXPERIENCE]
SOA/AAA studies, GLP-1 mortality implications, assumption triggers.

**Reinsurance Market** [REINSURANCE]
Transactions, Bermuda activity, PE-backed reinsurers, treaty pricing shifts.
Include any M&A involving life/annuity carriers or reinsurers.

**Capital & Risk** [CAPITAL]
RBC, rating agency actions on watchlist carriers. Flag downgrades or outlooks.

**Annuity Market** [PRICING / ALM]
FIA, RILA, MYGA trends. LIMRA data. Translate to pricing and ALM implications.

**Life Product Developments** [PRICING]
IUL, term pricing, AG 49 issues, new product launches by watchlist carriers.

**Investments & ALM** [ALM]
Private credit, structured assets, duration. Flag if rate/spread moves
should trigger cash flow testing or ALM review.

**Industry Trends**
AI adoption in life/annuity, PE consolidation, distribution shifts,
demographic/mortality trends (GLP-1, longevity). What should ARC clients
be thinking about 12-24 months out?

**Carrier Intelligence**
News on: Ameritas, Securian, Kansas City Life, Country Financial, BMI,
Midland National, North American, Pacific Life, Equitable, AIG Life,
Brighthouse, CNO/Bankers Life, Global Atlantic, Protective Life,
Lincoln Financial, Transamerica, Sammons, Mutual of Omaha,
26NorthRe, Independent Life, ARC, Springline.
One sentence each: what happened + actuarial implication.
Omit carriers with no news rather than saying "no news."

**SOA / AAA Research**
New publications and their impact on actuarial practice.

**Conversation Starters for Client Calls This Week**
5 items. Format EXACTLY as:
- TOPIC: [specific topic]
  WHAT TO SAY: [1-2 sentences in plain spoken language]
  WHY NOW: [specific trigger this week]
  RELEVANT TO: [functions and carrier types]

Only include starters you could NOT have used last week.

**Action Items for This Week**
3-6 numbered, time-sensitive, specific items.
Good: "Review 26NorthRe/Independent Life deal structure before Thursday reinsurance call."
Bad: "Monitor regulatory developments."

**Consulting Opportunities Surfaced This Week**
For each: (1) specific trigger, (2) carrier type most affected,
(3) what the engagement looks like — be specific.
Skip opportunities that apply every week.

**Key Takeaway**
One paragraph. Most important thing for an ARC consultant this week
and one concrete action to take.
"""

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=4000,
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"    Groq API error: {e}")
        return "Executive briefing unavailable due to a generation error."
