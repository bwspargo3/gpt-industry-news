import re
import requests
import xml.etree.ElementTree as ET

from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus

from groq import Groq

from config import (
    DAYS_BACK,
    MAX_ARTICLES_PER_QUERY,
    ACTUARIAL_KEYWORDS,
    FUNCTION_TAGS,
    HIGH_IMPACT_THRESHOLD,
    MEDIUM_IMPACT_THRESHOLD,
    GROQ_API_KEY,
    GMAIL_USER,
    NOISE_PHRASES,
)

from data_sources import (
    SEARCH_QUERIES,
    CARRIER_SEARCH_QUERIES,
    DIRECT_RSS_FEEDS,
)

from market_data import generate_market_narrative

# ---------------------------------------------------------------------
# Noise Filter
# ---------------------------------------------------------------------

def is_noise(article):
    """
    Returns True if the article should be dropped entirely.
    Catches false positives from broad queries and PR wire pollution.
    """
    text = (
        article.get("title", "") + " " +
        article.get("snippet", "")
    ).lower()

    for phrase in NOISE_PHRASES:
        if phrase.lower() in text:
            return True

    return False

# ---------------------------------------------------------------------
# RSS Parsing
# ---------------------------------------------------------------------

def parse_rss_feed(content, source_name=""):

    articles = []
    cutoff   = datetime.utcnow() - timedelta(days=DAYS_BACK)

    try:
        root    = ET.fromstring(content)
        channel = root.find("channel")
        items   = (
            channel.findall("item")
            if channel is not None
            else root.findall(".//item")
        )

        for item in items[:MAX_ARTICLES_PER_QUERY]:

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
        f"q={quote_plus(query)}"
        "&hl=en-US&gl=US&ceid=US:en"
    )

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return parse_rss_feed(response.content, "Google News")
    except Exception as e:
        print(f"    Google News error [{query[:40]}]: {e}")
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
# NAIC LATF Scraper
# Scrapes the LATF committee page for new agenda documents,
# exposure drafts, and adopted changes.
# ---------------------------------------------------------------------

LATF_URL = "https://content.naic.org/cmte_a_latf.htm"

def fetch_naic_latf():
    """
    Scrapes the NAIC LATF page for document links published
    within DAYS_BACK days. Returns articles with source = 'NAIC LATF'.
    Falls back gracefully if the page structure changes.
    """
    articles = []
    cutoff   = datetime.utcnow() - timedelta(days=DAYS_BACK)

    try:
        headers  = {
            "User-Agent": (
                "Mozilla/5.0 (compatible; "
                "ActuarialIntelligence/1.0; "
                f"+{GMAIL_USER})"
            )
        }
        response = requests.get(LATF_URL, headers=headers, timeout=20)
        response.raise_for_status()

        html = response.text

        # Extract all anchor tags
        # Pattern: <a href="...">link text</a>
        pattern = re.compile(
            r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>'
            r'(.*?)</a>',
            re.IGNORECASE | re.DOTALL,
        )

        seen_urls = set()

        for match in pattern.finditer(html):

            href = match.group(1).strip()
            text = re.sub(r"<[^>]+>", "", match.group(2)).strip()

            # Only care about document links (PDF, DOCX, HTM agenda pages)
            if not any(
                ext in href.lower()
                for ext in [".pdf", ".docx", ".doc", ".htm", ".html"]
            ):
                continue

            # Skip navigation and generic links
            if len(text) < 10:
                continue

            if href in seen_urls:
                continue
            seen_urls.add(href)

            # Build absolute URL if relative
            if href.startswith("/"):
                href = "https://content.naic.org" + href
            elif not href.startswith("http"):
                continue

            # Classify document type from link text
            text_lower = text.lower()

            if any(
                kw in text_lower
                for kw in [
                    "exposure draft", "draft", "proposed",
                    "agenda", "minutes", "adopted", "model",
                    "actuarial guideline", "vm-", "vm20", "vm22",
                    "pbr", "reserve", "annuity", "life",
                    "latf", "task force",
                ]
            ):
                articles.append({
                    "title":   f"[NAIC LATF] {text}",
                    "url":     href,
                    "source":  "NAIC LATF",
                    "date":    datetime.utcnow().strftime("%b %d, %Y"),
                    "snippet": (
                        f"Document published on the NAIC Life Actuarial "
                        f"Task Force page: {text}"
                    ),
                })

        if articles:
            print(f"    NAIC LATF: {len(articles)} documents found")
        else:
            print("    NAIC LATF: no new documents matched filters")

    except Exception as e:
        print(f"    NAIC LATF error: {e}")

    return articles

# ---------------------------------------------------------------------
# SEC EDGAR — 8-K filings
# ---------------------------------------------------------------------

LIFE_KEYWORDS = [
    "life insurance", "annuity", "reinsurance",
    "life insurer", "insurance holding",
    "long term care", "ltc",
]

def fetch_edgar_filings():

    articles = []

    url = (
        "https://www.sec.gov/cgi-bin/browse-edgar"
        "?action=getcurrent&type=8-K&output=atom&count=100"
    )

    try:
        headers  = {
            "User-Agent": f"Actuarial Intelligence {GMAIL_USER}"
        }
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        ns   = {"atom": "http://www.w3.org/2005/Atom"}

        for entry in root.findall("atom:entry", ns):

            title   = entry.findtext("atom:title",   "", ns)
            summary = entry.findtext("atom:summary", "", ns)
            text    = (title + " " + summary).lower()

            if not any(x in text for x in LIFE_KEYWORDS):
                continue

            link = entry.find("atom:link", ns)

            articles.append({
                "title":   title,
                "url":     link.get("href") if link is not None else "",
                "source":  "SEC EDGAR",
                "date":    datetime.utcnow().strftime("%b %d, %Y"),
                "snippet": summary[:400],
            })

    except Exception as e:
        print(f"    EDGAR error: {e}")

    return articles

# ---------------------------------------------------------------------
# Collect All News
# ---------------------------------------------------------------------

def collect_news():

    buckets = {}

    def add(category, items):
        if items:
            buckets.setdefault(category, []).extend(items)

    print("  Google News (industry queries)...")
    for category, query in SEARCH_QUERIES:
        add(category, fetch_google_news(query))

    print("  Google News (carrier watchlist)...")
    for category, query in CARRIER_SEARCH_QUERIES:
        add(category, fetch_google_news(query))

    print("  Direct RSS feeds...")
    for category, source, url in DIRECT_RSS_FEEDS:
        add(category, fetch_direct_rss(url, source))

    print("  NAIC LATF...")
    add("Regulatory", fetch_naic_latf())

    print("  SEC EDGAR...")
    add("SEC Filings", fetch_edgar_filings())

    return buckets

# ---------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------

def deduplicate_articles(category_buckets):

    seen   = set()
    output = {}

    for category, articles in category_buckets.items():
        for article in articles:
            key = article["title"].lower().strip()[:100]
            if key in seen:
                continue
            seen.add(key)
            output.setdefault(category, []).append(article)

    return output

# ---------------------------------------------------------------------
# Noise Filtering (post-dedup)
# ---------------------------------------------------------------------

def filter_noise(category_buckets):
    """
    Removes articles matching NOISE_PHRASES before scoring.
    Runs after deduplication.
    """
    output  = {}
    dropped = 0

    for category, articles in category_buckets.items():
        clean = [a for a in articles if not is_noise(a)]
        dropped += len(articles) - len(clean)
        if clean:
            output[category] = clean

    print(f"    Noise filter dropped {dropped} articles")
    return output

# ---------------------------------------------------------------------
# Actuarial Function Tagging
# ---------------------------------------------------------------------

def tag_article(article):
    """
    Returns sorted list of actuarial function tags based on content.
    """
    text = (
        article["title"] + " " +
        article.get("snippet", "")
    ).lower()

    tags = set()

    for keyword, ktags in FUNCTION_TAGS.items():
        if keyword in text:
            tags.update(ktags)

    if article.get("category") == "Carrier Intelligence":
        tags.add("CARRIER")

    if article.get("source") == "NAIC LATF":
        tags.update(["REGULATORY", "VALUATION"])

    return sorted(tags) if tags else ["GENERAL"]

# ---------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------

def calculate_score(article):

    text = (
        article["title"] + " " +
        article.get("snippet", "")
    ).lower()

    score = 0
    for keyword, value in ACTUARIAL_KEYWORDS.items():
        if keyword in text:
            score += value

    # Boost NAIC LATF documents — always high relevance
    if article.get("source") == "NAIC LATF":
        score += 20

    # Boost primary sources
    if article.get("source") in (
        "SOA News", "SOA Research",
        "American Academy of Actuaries",
        "NAIC Newsroom", "LIMRA",
        "AM Best Ratings", "AM Best News",
    ):
        score += 5

    return score

def classify_impact(score):
    if score >= HIGH_IMPACT_THRESHOLD:
        return "HIGH"
    if score >= MEDIUM_IMPACT_THRESHOLD:
        return "MEDIUM"
    return "LOW"

def score_articles(category_buckets):

    for category, articles in category_buckets.items():
        for article in articles:
            article["category"] = category
            score               = calculate_score(article)
            article["score"]    = score
            article["impact"]   = classify_impact(score)
            article["tags"]     = tag_article(article)

    return category_buckets

# ---------------------------------------------------------------------
# Consulting Opportunity Detection
# ---------------------------------------------------------------------

def identify_consulting_opportunities(category_buckets):

    opportunities = set()

    trigger_map = {
        "vm-20":                     "VM-20 reserve implementation or gap assessment",
        "vm20":                      "VM-20 reserve implementation or gap assessment",
        "vm-22":                     "VM-22 annuity reserve analysis",
        "vm22":                      "VM-22 annuity reserve analysis",
        "ldti":                      "LDTI/ASC 944 reporting and transition support",
        "asc 944":                   "LDTI/ASC 944 reporting and transition support",
        "asset adequacy":            "Asset adequacy / cash flow testing engagement",
        "cash flow testing":         "Asset adequacy / cash flow testing engagement",
        "reinsurance":               "Reinsurance transaction actuarial support",
        "funds withheld":            "Funds withheld / modco reinsurance structure review",
        "bermuda":                   "Offshore reinsurance captive or Bermuda structure review",
        "rbc":                       "RBC capital adequacy study",
        "risk based capital":        "RBC capital adequacy study",
        "mortality":                 "Mortality or experience study",
        "experience study":          "Mortality or experience study",
        "lapse":                     "Policyholder behavior / lapse assumption study",
        "policyholder behavior":     "Policyholder behavior / lapse assumption study",
        "private credit":            "Investment strategy ALM review for alternative assets",
        "alm":                       "Asset-liability management review",
        "asset liability":           "Asset-liability management review",
        "iul":                       "IUL illustration actuarial support (AG 49)",
        "indexed universal life":    "IUL illustration actuarial support (AG 49)",
        "fia":                       "FIA hedging program or pricing review",
        "rila":                      "RILA product development or filing support",
        "myga":                      "MYGA product pricing or filing support",
        "pbr":                       "PBR implementation or model validation",
        "principle based reserving": "PBR implementation or model validation",
        "fiduciary":                 "DOL fiduciary rule compliance review",
        "actuarial guideline":       "Actuarial guideline compliance or implementation",
        "exposure draft":            "Regulatory comment letter or impact analysis",
    }

    for category, articles in category_buckets.items():
        for article in articles:
            text = (
                article["title"] + " " +
                article.get("snippet", "")
            ).lower()

            for keyword, opportunity in trigger_map.items():
                if keyword in text:
                    opportunities.add(opportunity)

    return sorted(opportunities)

# ---------------------------------------------------------------------
# Groq Summary — Consulting-Focused
# ---------------------------------------------------------------------

def summarize_with_groq(category_buckets, market_snapshot):

    client = Groq(api_key=GROQ_API_KEY)

    # Generate narrative market data string for the prompt
    market_narrative = generate_market_narrative(market_snapshot)

    # Build article digest — highest scoring first, skip pure noise
    article_text = ""
    counter      = 1

    for category, articles in category_buckets.items():

        sorted_articles = sorted(
            articles,
            key=lambda x: x.get("score", 0),
            reverse=True,
        )

        # Only send meaningful articles to the LLM
        filtered = [
            a for a in sorted_articles
            if a.get("score", 0) >= 4
            or a.get("source") in (
                "NAIC LATF", "SOA News", "SOA Research",
                "American Academy of Actuaries", "LIMRA",
                "AM Best Ratings", "AM Best News",
            )
        ]

        if not filtered:
            continue

        article_text += f"\n=== {category} ===\n"

        for article in filtered[:8]:

            tags_str = ", ".join(article.get("tags", ["GENERAL"]))

            article_text += f"""
[{counter}]
TITLE:    {article['title']}
SOURCE:   {article['source']}
DATE:     {article.get('date', '')}
TAGS:     {tags_str}
IMPACT:   {article['impact']}
SCORE:    {article.get('score', 0)}
SNIPPET:  {article['snippet']}
"""
            counter += 1

    prompt = f"""
You are a senior life and annuity actuarial consultant at Actuarial Resources
Corporation (ARC), a Springline company. ARC provides actuarial consulting to
life insurance and annuity carriers, primarily mid-size companies. You have
strong relationships with several Kansas City-area insurers including Ameritas,
Securian, Kansas City Life, Country Financial, Business Men's Assurance (BMI),
Midland National, and North American Company.

Your specialties: valuation (VM-20/VM-22/PBR), LDTI/ASC 944, reinsurance
structures, experience studies, RBC capital management, ALM, and life/annuity
product development (FIA, RILA, IUL, MYGA, term).

AUDIENCE: This briefing is for YOU — a working consultant preparing for a week
of client calls. Write like you're briefing yourself, not publishing a report.
Be direct. Be specific. If something has no consulting angle, skip it.

HARD FILTER: Ignore completely —
- Property/casualty, health, employee benefits, surety
- Auto insurance rate changes
- General macroeconomics unless it directly impacts life/annuity reserves,
  pricing, capital, or reinsurance
- Consumer personal finance stories
- Sports, lifestyle, PR announcements unrelated to our carrier watchlist

MARKET DATA (as of today):
{market_narrative}

ARTICLES:
{article_text}

---

Write the following sections exactly. Use **Section Name** as the header.
If a section has nothing material, write one sentence saying so — do not pad.
Do not repeat the same development across multiple sections.
Each development should appear in exactly one section.

**Market Pulse**
3-4 sentences. Translate rates, spreads, VIX, and credit OAS directly into
actuarial implications: new-money rates, reserve discount rates, FIA/RILA
hedging costs, ALM positioning for spread products. Reference specific numbers
from the market data. This should read like something you'd say to a CFO
in the first 30 seconds of a call.

**This Week's Key Themes**
3-5 bullets. Each bullet: one sentence on what happened + one sentence on why
it matters to a life actuarial consultant at ARC. No vague observations.
These should be things that are specific to THIS week, not evergreen statements.

**High Impact Developments**
Only items with direct, near-term implications for reserving, capital, or
regulatory compliance. For each: (1) what happened, (2) which carrier types
or clients are affected, (3) what ARC should prepare or offer.

**Valuation & Reserving** [VALUATION]
VM-20, VM-22, PBR, asset adequacy, LDTI. Flag NAIC LATF documents, exposure
draft comment deadlines, or adoption votes.

**Regulatory Developments** [REGULATORY]
LATF, NAIC committees, actuarial guidelines, Federal Register (IRS/DOL).
Flag anything with a comment period or upcoming vote.

**Accounting & LDTI** [ACCOUNTING]
ASC 944 implementation issues, restatements, FASB guidance.

**Mortality & Experience Studies** [EXPERIENCE]
New SOA/AAA studies, assumption update triggers. Note if findings should
prompt clients to review their own assumptions before year-end.

**Reinsurance Market** [REINSURANCE]
Transactions, treaty structures, Bermuda activity, regulatory scrutiny.
Flag deals that signal market pricing shifts affecting our clients.

**Capital & Risk** [CAPITAL]
RBC developments, rating agency actions. Flag watchlist additions or
outlook changes for carriers on our watchlist.

**Annuity Market** [PRICING / ALM]
FIA, RILA, MYGA sales trends. Translate LIMRA data into what it means for
pricing actuaries and ALM teams at mid-size carriers.

**Life Product Developments** [PRICING]
IUL, term, whole life pricing or filing activity. AG 49 illustration issues.

**Investments & ALM** [ALM]
Private credit, structured assets, duration positioning. Note if credit
spread or rate moves should trigger a cash flow testing review.

**Carrier Intelligence**
Summarize news specifically about: Ameritas, Securian, Kansas City Life,
Country Financial, BMI / Business Men's Assurance, Midland National,
North American Company, Pacific Life, Equitable, AIG Life, Brighthouse,
CNO Financial / Bankers Life, Global Atlantic, Protective Life, Lincoln
Financial, Transamerica, Sammons Financial, Mutual of Omaha,
Actuarial Resources Corporation, Springline.
For each carrier with news: one sentence on what happened, one sentence
on the actuarial implication or ARC opportunity.
If nothing surfaced for a carrier, omit it rather than saying "no news."
If nothing surfaced for any carrier, say so in one sentence.

**SOA / AAA Research**
New publications, exposure drafts, or research. Note which actuarial
function is most affected and whether clients should be briefed.

**Conversation Starters for Client Calls This Week**
5 specific, ready-to-use talking points. Format EXACTLY as:
- TOPIC: [one-line topic — specific, not generic]
  WHAT TO SAY: [1-2 sentences you would actually say to a client, in plain spoken language — not consultant jargon]
  WHY NOW: [the specific article, data point, or deadline that makes this timely THIS week]
  RELEVANT TO: [which actuarial functions and which carrier types]

These must be things you could not have said last week. If you can't find
5 genuinely timely starters, write fewer — do not pad with generic ones.

**Action Items for This Week**
Numbered list, 3-6 items. Time-sensitive and specific only.
Good example: "Pull Lincoln Financial Q1 10-Q and review LDTI assumption rollforward before Thursday call."
Bad example: "Monitor regulatory developments."
If there are no time-sensitive actions, say so.

**Consulting Opportunities Surfaced This Week**
For each opportunity: (1) what triggered it this week specifically,
(2) which carrier type is most likely to need help,
(3) what the engagement would look like at a high level — be specific,
not just "reinsurance support."
Skip opportunities that would apply any week of any year.

**Key Takeaway**
One paragraph. The single most important thing for an ARC consultant to
know this week, and one concrete action to take because of it.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content.strip()
