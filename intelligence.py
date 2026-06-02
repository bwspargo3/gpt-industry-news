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
)

from data_sources import (
    SEARCH_QUERIES,
    CARRIER_SEARCH_QUERIES,
    DIRECT_RSS_FEEDS,
)

# ---------------------------------------------------------------------
# RSS Parsing
# ---------------------------------------------------------------------

def parse_rss_feed(content, source_name=""):

    articles = []
    cutoff = datetime.utcnow() - timedelta(days=DAYS_BACK)

    try:
        root = ET.fromstring(content)
        channel = root.find("channel")
        items = (
            channel.findall("item")
            if channel is not None
            else root.findall(".//item")
        )

        for item in items[:MAX_ARTICLES_PER_QUERY]:

            title    = item.findtext("title", "").strip()
            link     = item.findtext("link",  "").strip()
            desc     = item.findtext("description", "").strip()
            pub_date = item.findtext("pubDate", "").strip()

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
        print(f"RSS parse error ({source_name}): {e}")

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
        print(f"Google News error [{query}]: {e}")
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
        print(f"RSS error [{source_name}]: {e}")
        return []

# ---------------------------------------------------------------------
# SEC EDGAR — 8-K filings for life/annuity carriers
# ---------------------------------------------------------------------

LIFE_KEYWORDS = [
    "life insurance", "annuity", "reinsurance",
    "life insurer", "insurance holding", "long term care", "ltc",
]

def fetch_edgar_filings():

    articles = []

    url = (
        "https://www.sec.gov/cgi-bin/browse-edgar"
        "?action=getcurrent&type=8-K&output=atom&count=100"
    )

    try:
        headers = {"User-Agent": f"Actuarial Intelligence {GMAIL_USER}"}
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

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
        print(f"EDGAR error: {e}")

    return articles

# ---------------------------------------------------------------------
# Collect News
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
# Actuarial Function Tagging
# ---------------------------------------------------------------------

def tag_article(article):
    """
    Returns a sorted list of actuarial function tags
    e.g. ["ALM", "VALUATION"] based on title + snippet content.
    """
    text = (
        article["title"] + " " + article.get("snippet", "")
    ).lower()

    tags = set()

    for keyword, ktags in FUNCTION_TAGS.items():
        if keyword in text:
            tags.update(ktags)

    # Carrier intelligence always gets its own tag
    if article.get("category") == "Carrier Intelligence":
        tags.add("CARRIER")

    return sorted(tags) if tags else ["GENERAL"]

# ---------------------------------------------------------------------
# Relevance Scoring
# ---------------------------------------------------------------------

def calculate_score(article):

    text = (
        article["title"] + " " + article.get("snippet", "")
    ).lower()

    score = 0
    for keyword, value in ACTUARIAL_KEYWORDS.items():
        if keyword in text:
            score += value

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
            score = calculate_score(article)
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
        "vm-20":                "VM-20 reserve implementation or gap assessment",
        "vm20":                 "VM-20 reserve implementation or gap assessment",
        "vm-22":                "VM-22 annuity reserve analysis",
        "vm22":                 "VM-22 annuity reserve analysis",
        "ldti":                 "LDTI/ASC 944 reporting and transition support",
        "asc 944":              "LDTI/ASC 944 reporting and transition support",
        "asset adequacy":       "Asset adequacy / cash flow testing engagement",
        "cash flow testing":    "Asset adequacy / cash flow testing engagement",
        "reinsurance":          "Reinsurance transaction actuarial support",
        "funds withheld":       "Funds withheld / modco reinsurance structure review",
        "bermuda":              "Bermuda reinsurance captive or offshore structure review",
        "rbc":                  "RBC capital adequacy study",
        "risk based capital":   "RBC capital adequacy study",
        "mortality":            "Mortality or experience study",
        "experience study":     "Mortality or experience study",
        "lapse":                "Policyholder behavior / lapse assumption study",
        "policyholder behavior":"Policyholder behavior / lapse assumption study",
        "private credit":       "Investment strategy ALM review for alternative assets",
        "alm":                  "Asset-liability management review",
        "asset liability":      "Asset-liability management review",
        "iul":                  "IUL illustration actuarial support (AG 49)",
        "indexed universal life":"IUL illustration actuarial support (AG 49)",
        "fia":                  "FIA hedging program or pricing review",
        "rila":                 "RILA product development or filing support",
        "pbr":                  "PBR implementation or model validation",
        "principle based reserving": "PBR implementation or model validation",
    }

    for category, articles in category_buckets.items():
        for article in articles:
            text = (
                article["title"] + " " + article.get("snippet", "")
            ).lower()

            for keyword, opportunity in trigger_map.items():
                if keyword in text:
                    opportunities.add(opportunity)

    return sorted(opportunities)

# ---------------------------------------------------------------------
# Groq Summary — Consulting-Focused Prompt
# ---------------------------------------------------------------------

def summarize_with_groq(category_buckets, market_snapshot):

    client = Groq(api_key=GROQ_API_KEY)

    # Build article digest, highest-scoring first within each category
    article_text = ""
    counter = 1

    for category, articles in category_buckets.items():

        sorted_articles = sorted(
            articles,
            key=lambda x: x.get("score", 0),
            reverse=True
        )

        article_text += f"\n=== {category} ===\n"

        for article in sorted_articles[:8]:

            tags_str = ", ".join(article.get("tags", ["GENERAL"]))

            article_text += f"""
[{counter}]
TITLE:    {article['title']}
SOURCE:   {article['source']}
DATE:     {article.get('date', '')}
TAGS:     {tags_str}
IMPACT:   {article['impact']}
SNIPPET:  {article['snippet']}
"""
            counter += 1

    prompt = f"""
You are a senior life and annuity actuarial consultant at a boutique consulting firm.
Your clients are life insurance and annuity companies, primarily mid-size carriers.
You have a strong client relationship with several Kansas City-area insurers.
Your specialties: valuation (VM-20/VM-22/PBR), LDTI, reinsurance, experience studies,
capital management (RBC), ALM, and life/annuity product development.

AUDIENCE: This briefing is for YOU — a working consultant — not a general audience.
Write like you're briefing yourself before a week of client calls.
Be direct. Be specific. Skip anything that doesn't affect your work or your clients.

FILTER: Ignore property/casualty, health, employee benefits, and general
macroeconomic news unless it has a direct, specific impact on life/annuity
reserves, pricing, capital, or reinsurance structures.

---

MARKET DATA:
{market_snapshot}

ARTICLES:
{article_text}

---

Write the following sections. Use **Section Name** as headers.
If a section has nothing material to report, write one sentence saying so — do not pad it.

**Market Pulse**
2-3 sentences on rates, spreads, and yield curve. Translate directly to actuarial impact:
what does this mean for new-money rates, reserve discount rates, FIA/RILA hedging costs,
or ALM positioning? Be specific about direction and magnitude where possible.

**This Week's Key Themes**
3-5 bullet points. Each bullet: one sentence on what happened, one sentence on
why it matters to a life actuarial consultant. No vague observations.

**High Impact Developments**
Only items with direct, near-term implications for reserving, capital, or regulatory
compliance. For each item, state: (1) what happened, (2) which clients or carrier
types are affected, (3) what action a consultant should take or prepare for.

**Valuation & Reserving** [VALUATION]
Developments affecting VM-20, VM-22, PBR, asset adequacy, or LDTI.
Note any NAIC exposure drafts, comment deadlines, or adopted changes.

**Regulatory Developments** [REGULATORY]
LATF, NAIC committees, actuarial guidelines. Flag anything with a comment period
deadline or upcoming adoption vote.

**Accounting & LDTI** [ACCOUNTING]
ASC 944 / LDTI. Focus on implementation issues, restatements, or FASB guidance.

**Mortality & Experience Studies** [EXPERIENCE]
New SOA studies, industry experience results, assumption update triggers.
Note if any findings should prompt clients to review their own assumptions.

**Reinsurance Market** [REINSURANCE]
Transactions, treaty structures, Bermuda activity, regulatory scrutiny of
offshore arrangements. Flag deals that signal market pricing shifts.

**Capital & Risk** [CAPITAL]
RBC developments, rating agency actions on life/annuity carriers, capital
adequacy trends. Flag any watchlist additions or outlook changes.

**Annuity Market** [PRICING / ALM]
FIA and RILA sales trends, hedging costs, carrier product moves.
Translate LIMRA data into what it means for pricing actuaries and ALM teams.

**Life Product Developments** [PRICING]
IUL, term, whole life pricing or filing activity. AG 49 illustration issues.

**Investments & ALM** [ALM]
Private credit, structured assets, duration positioning. Flag anything
that affects investment strategy assumptions used in cash flow testing.

**Carrier Intelligence**
Summarize any news specifically about: Kansas City Life, Ameritas, Securian,
Country Financial, Business Men's Assurance (BMI), Midland National,
North American Company, Pacific Life, Equitable, AIG Life, Brighthouse,
CNO Financial / Bankers Life, Global Atlantic, Protective Life, Lincoln Financial,
Transamerica, Sammons Financial, or Mutual of Omaha.
For each carrier mentioned: state what happened and the actuarial implication.
If nothing surfaced this period, say so briefly.

**SOA / AAA Research**
New publications, exposure drafts, or research releases. Note the actuarial
function most affected (valuation, pricing, experience, capital).

**Conversation Starters for Client Calls This Week**
3-5 specific, ready-to-use talking points for client conversations.
Format each as:
- TOPIC: [one-line topic]
  WHAT TO SAY: [1-2 sentences you could say to a client, in plain language]
  WHY NOW: [what triggered this — specific article, data point, or deadline]
  RELEVANT TO: [which actuarial functions or carrier types]

These should be things a consultant would actually bring up unprompted to demonstrate
awareness. Avoid anything generic enough to say any week of any year.

**Action Items for This Week**
Numbered list. Specific, time-sensitive actions only.
Examples of the right level: "Review LATF June draft on AG 48 before July 15 comment deadline"
or "Pull Q1 10-Q for Brighthouse and check LDTI assumption rollforward disclosures."
No standing reminders that apply every week.

**Consulting Opportunities Surfaced This Week**
For each opportunity: (1) what triggered it, (2) which carrier type is most likely
to need help, (3) what the engagement would look like at a high level.
Be specific — not "reinsurance support" but "offshore reinsurance captive review
for mid-size carriers following NAIC's updated collateral guidance."

**Key Takeaway**
One paragraph. The single most important thing for a life actuarial consultant
to know this week, and what to do about it.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()
