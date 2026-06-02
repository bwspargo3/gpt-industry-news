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
    HIGH_IMPACT_THRESHOLD,
    MEDIUM_IMPACT_THRESHOLD,
    GROQ_API_KEY,
)

from data_sources import (
    SEARCH_QUERIES,
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

            title = item.findtext("title", "").strip()

            link = item.findtext("link", "").strip()

            desc = item.findtext(
                "description",
                ""
            ).strip()

            pub_date = item.findtext(
                "pubDate",
                ""
            ).strip()

            try:

                dt = parsedate_to_datetime(
                    pub_date
                ).replace(
                    tzinfo=None
                )

                if dt < cutoff:
                    continue

                date_string = dt.strftime(
                    "%b %d, %Y"
                )

            except Exception:

                date_string = pub_date

            articles.append({

                "title": title,

                "url": link,

                "source": source_name,

                "date": date_string,

                "snippet": re.sub(
                    r"<[^>]+>",
                    "",
                    desc
                )[:400]

            })

    except Exception as e:

        print(
            f"RSS parse error: {e}"
        )

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

        response = requests.get(
            url,
            timeout=15
        )

        response.raise_for_status()

        return parse_rss_feed(
            response.content,
            "Google News"
        )

    except Exception as e:

        print(
            f"Google News error: {query}: {e}"
        )

        return []

# ---------------------------------------------------------------------
# Direct RSS
# ---------------------------------------------------------------------

def fetch_direct_rss(
    url,
    source_name
):

    try:

        response = requests.get(
            url,
            timeout=15
        )

        response.raise_for_status()

        return parse_rss_feed(
            response.content,
            source_name
        )

    except Exception as e:

        print(
            f"RSS error {source_name}: {e}"
        )

        return []

# ---------------------------------------------------------------------
# SEC EDGAR
# ---------------------------------------------------------------------

LIFE_KEYWORDS = [

    "life insurance",

    "annuity",

    "reinsurance",

    "life insurer",

    "insurance holding",

    "long term care",

    "ltc"
]

def fetch_edgar_filings():

    articles = []

    url = (
        "https://www.sec.gov/"
        "cgi-bin/browse-edgar"
        "?action=getcurrent"
        "&type=8-K"
        "&output=atom"
        "&count=100"
    )

    try:

        headers = {
            "User-Agent":
            "Actuarial Intelligence"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

        root = ET.fromstring(
            response.content
        )

        ns = {
            "atom":
            "http://www.w3.org/2005/Atom"
        }

        for entry in root.findall(
            "atom:entry",
            ns
        ):

            title = entry.findtext(
                "atom:title",
                "",
                ns
            )

            summary = entry.findtext(
                "atom:summary",
                "",
                ns
            )

            text = (
                title +
                " " +
                summary
            ).lower()

            if not any(
                x in text
                for x in LIFE_KEYWORDS
            ):
                continue

            link = entry.find(
                "atom:link",
                ns
            )

            articles.append({

                "title": title,

                "url": (
                    link.get("href")
                    if link is not None
                    else ""
                ),

                "source":
                "SEC EDGAR",

                "date":
                datetime.utcnow().strftime(
                    "%b %d, %Y"
                ),

                "snippet":
                summary[:400]

            })

    except Exception as e:

        print(
            f"EDGAR error: {e}"
        )

    return articles

# ---------------------------------------------------------------------
# Collect News
# ---------------------------------------------------------------------

def collect_news():

    buckets = {}

    def add(category, items):

        if not items:
            return

        buckets.setdefault(
            category,
            []
        ).extend(items)

    print("Google News...")

    for category, query in SEARCH_QUERIES:

        add(
            category,
            fetch_google_news(
                query
            )
        )

    print("RSS Feeds...")

    for (
        category,
        source,
        url
    ) in DIRECT_RSS_FEEDS:

        add(
            category,
            fetch_direct_rss(
                url,
                source
            )
        )

    print("SEC EDGAR...")

    add(
        "SEC Filings",
        fetch_edgar_filings()
    )

    return buckets

# ---------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------

def deduplicate_articles(
    category_buckets
):

    seen = set()

    output = {}

    for category, articles in category_buckets.items():

        for article in articles:

            key = (
                article["title"]
                .lower()
                .strip()
            )[:100]

            if key in seen:
                continue

            seen.add(key)

            output.setdefault(
                category,
                []
            ).append(article)

    return output

# ---------------------------------------------------------------------
# Actuarial Relevance Score
# ---------------------------------------------------------------------

def calculate_score(article):

    text = (

        article["title"]

        + " "

        + article.get(
            "snippet",
            ""
        )

    ).lower()

    score = 0

    for keyword, value in ACTUARIAL_KEYWORDS.items():

        if keyword in text:

            score += value

    return score

# ---------------------------------------------------------------------
# Impact Classification
# ---------------------------------------------------------------------

def classify_impact(score):

    if score >= HIGH_IMPACT_THRESHOLD:

        return "HIGH"

    if score >= MEDIUM_IMPACT_THRESHOLD:

        return "MEDIUM"

    return "LOW"

# ---------------------------------------------------------------------
# Score Articles
# ---------------------------------------------------------------------

def score_articles(
    category_buckets
):

    for category, articles in category_buckets.items():

        for article in articles:

            score = calculate_score(
                article
            )

            article["score"] = score

            article[
                "impact"
            ] = classify_impact(
                score
            )

    return category_buckets

# ---------------------------------------------------------------------
# Consulting Opportunity Detection
# ---------------------------------------------------------------------

def identify_consulting_opportunities(
    category_buckets
):

    opportunities = []

    for category, articles in category_buckets.items():

        for article in articles:

            text = (
                article["title"]
                .lower()
            )

            if (
                "vm-20" in text
                or "vm20" in text
            ):

                opportunities.append(
                    "VM-20 reserve implementation support"
                )

            if (
                "vm-22" in text
                or "vm22" in text
            ):

                opportunities.append(
                    "VM-22 annuity reserve analysis"
                )

            if "ldti" in text:

                opportunities.append(
                    "LDTI reporting support"
                )

            if "reinsurance" in text:

                opportunities.append(
                    "Reinsurance transaction support"
                )

            if "rbc" in text:

                opportunities.append(
                    "Capital management studies"
                )

            if (
                "mortality"
                in text
            ):

                opportunities.append(
                    "Experience study work"
                )

    return sorted(
        list(
            set(
                opportunities
            )
        )
    )

# ---------------------------------------------------------------------
# Groq Summary
# ---------------------------------------------------------------------

def summarize_with_groq(
    category_buckets,
    market_snapshot
):

    client = Groq(
        api_key=GROQ_API_KEY
    )

    article_text = ""

    counter = 1

    for category, articles in category_buckets.items():

        article_text += (
            f"\n=== {category} ===\n"
        )

        articles = sorted(

            articles,

            key=lambda x:
            x.get(
                "score",
                0
            ),

            reverse=True

        )

        for article in articles:

            article_text += f"""
[{counter}]
TITLE: {article['title']}
SOURCE: {article['source']}
IMPACT: {article['impact']}
SCORE: {article['score']}
SUMMARY: {article['snippet']}
"""

            counter += 1

    prompt = f"""
You are a senior life and annuity actuarial consultant.

Write a professional executive briefing.

Focus ONLY on topics relevant to:

- Reserving
- Valuation
- VM-20
- VM-22
- LATF
- LDTI
- RBC
- Reinsurance
- Mortality
- FIA
- RILA
- ALM
- Capital Management

Market Data:

{market_snapshot}

Articles:

{article_text}

Create these sections:

Market Pulse

Today's Key Themes

High Impact Developments

Valuation & Reserving

Regulatory Developments

Accounting & LDTI

Mortality & Experience Studies

Reinsurance Market

Capital & Risk

Annuity Market

Life Product Developments

Investments & ALM

SOA / AAA Research

Action Items for Actuaries

Consulting Opportunities

Key Takeaway

Be concise.

Explain WHY each item matters to life actuaries.
"""

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        temperature=0.2,

        max_tokens=3500,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return (
        response
        .choices[0]
        .message
        .content
        .strip()
    )
