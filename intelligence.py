import os
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
from groq import Groq

import config
from data_sources import SEARCH_QUERIES, CARRIER_SEARCH_QUERIES, HTML_SCRAPE_TARGETS

# ---------------------------------------------------------------------
# Fetch Utilities
# ---------------------------------------------------------------------

def fetch_google_news(query):
    """
    Fetches articles from Google News RSS based on a search query.
    """
    articles = []
    try:
        url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        cutoff_date = datetime.utcnow() - timedelta(days=config.DAYS_BACK)

        for item in root.findall('.//item'):
            title = item.find('title').text if item.find('title') is not None else ""
            link = item.find('link').text if item.find('link') is not None else ""
            pubDate_str = item.find('pubDate').text if item.find('pubDate') is not None else ""
            source = item.find('source').text if item.find('source') is not None else "Google News"
            
            try:
                # pubDate format: 'Wed, 02 Jun 2026 12:00:00 GMT'
                pubDate = datetime.strptime(pubDate_str, "%a, %d %b %Y %H:%M:%S %Z")
                if pubDate < cutoff_date:
                    continue
            except ValueError:
                pass # Fallback to include if date parsing fails
            
            articles.append({
                "title": title,
                "url": link,
                "source": source,
                "date": pubDate_str,
                "snippet": "Discovered via Google News alert.",
            })

            if len(articles) >= config.MAX_ARTICLES_PER_QUERY:
                break
    except Exception as e:
        print(f"    Google News error [{query}]: {e}")
        
    return articles

def fetch_heuristic_html(url, source_name):
    """
    Simulates a web browser to scrape article headlines directly from the HTML 
    of a webpage, bypassing abandoned RSS feeds and basic firewall blocks.
    """
    articles = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        seen_urls = set()

        for a in soup.find_all("a"):
            text = a.get_text(strip=True)
            href = a.get("href")

            # Heuristic filter: Real article headlines usually contain at least 5 words 
            # and are longer than 30 characters.
            if not href or len(text) < 30 or len(text.split()) < 5:
                continue

            full_url = urljoin(url, href)

            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)

            if any(x in full_url.lower() for x in ["/contact", "/about", "/login", "/subscribe", "policy", "/author/"]):
                continue

            articles.append({
                "title": text,
                "url": full_url,
                "source": source_name,
                "date": datetime.utcnow().strftime("%b %d, %Y"),
                "snippet": f"Recently published article or report discovered on {source_name}.",
            })

            if len(articles) >= config.MAX_ARTICLES_PER_QUERY:
                break

    except Exception as e:
        print(f"    HTML Scrape error [{source_name}]: {e}")

    return articles

# ---------------------------------------------------------------------
# Pipeline Functions
# ---------------------------------------------------------------------

def collect_news():
    """
    Executes all data gathering targets and categorizes the raw results.
    """
    raw_articles = []
    
    print("  Google News (industry queries)...")
    for category, query in SEARCH_QUERIES:
        for article in fetch_google_news(query):
            article["category"] = category
            raw_articles.append(article)
            
    print("  Google News (carrier watchlist)...")
    for category, query in CARRIER_SEARCH_QUERIES:
        for article in fetch_google_news(query):
            article["category"] = category
            raw_articles.append(article)
            
    print("  Direct HTML scraping...")
    for category, source, url in HTML_SCRAPE_TARGETS:
        for article in fetch_heuristic_html(url, source):
            article["category"] = category
            raw_articles.append(article)
            
    return raw_articles

def deduplicate_articles(articles):
    """
    Removes duplicate articles based on normalized titles or URLs.
    """
    seen = set()
    unique_articles = []
    for a in articles:
        normalized_title = re.sub(r'[^a-zA-Z0-9]', '', a["title"].lower())
        if normalized_title not in seen and a["url"] not in seen:
            seen.add(normalized_title)
            seen.add(a["url"])
            unique_articles.append(a)
    return unique_articles

def filter_noise(articles):
    """
    Drops articles matching predefined noise phrases.
    """
    filtered = []
    dropped_count = 0
    for a in articles:
        text_to_check = (a["title"] + " " + a["snippet"]).lower()
        if any(noise in text_to_check for noise in config.NOISE_PHRASES):
            dropped_count += 1
            continue
        filtered.append(a)
    print(f"    Noise filter dropped {dropped_count} articles")
    return filtered

def score_and_tag(articles):
    """
    Scores each article based on keyword weights and maps it to a category bucket.
    """
    category_buckets = {}
    
    for a in articles:
        text_block = (a["title"] + " " + a["snippet"]).lower()
        score = 0
        tags = set()
        
        for kw, weight in config.ACTUARIAL_KEYWORDS.items():
            if kw in text_block:
                score += weight
                
        for key, assigned_tags in config.FUNCTION_TAGS.items():
            if key in text_block:
                for t in assigned_tags:
                    tags.add(t)
                    
        if not tags:
            tags.add("GENERAL")
            
        a["score"] = score
        a["tags"] = list(tags)
        
        # Determine Impact Level
        if score >= config.HIGH_IMPACT_THRESHOLD:
            a["impact"] = "HIGH"
        elif score >= config.MEDIUM_IMPACT_THRESHOLD:
            a["impact"] = "MEDIUM"
        else:
            a["impact"] = "LOW"
            
        cat = a.get("category", "Other")
        if cat not in category_buckets:
            category_buckets[cat] = []
        category_buckets[cat].append(a)
        
    # Sort buckets by score descending
    for cat in category_buckets:
        category_buckets[cat].sort(key=lambda x: x["score"], reverse=True)
        
    return category_buckets

def summarize_with_groq(category_buckets, market_snapshot):
    """
    Passes top articles and market context to the Groq LLM to generate 
    an executive briefing and actionable consulting opportunities.
    """
    client = Groq(api_key=config.GROQ_API_KEY)
    
    # Format the market narrative
    t = market_snapshot.get("treasuries", {})
    add = market_snapshot.get("additional", {})
    
    market_narrative = f"""
    Treasury Yields:
    - 2Y: {t.get('2Y', {}).get('value', 'N/A')}%
    - 5Y: {t.get('5Y', {}).get('value', 'N/A')}%
    - 10Y: {t.get('10Y', {}).get('value', 'N/A')}%
    - 30Y: {t.get('30Y', {}).get('value', 'N/A')}%
    - SOFR: {market_snapshot.get('sofr', {}).get('value', 'N/A')}%
    
    Credit Spreads & Volatility:
    - IG OAS: {add.get('IG_OAS', {}).get('value', 'N/A')}
    - HY OAS: {add.get('HY_OAS', {}).get('value', 'N/A')}
    - 10Y Breakeven Inflation: {add.get('BREAKEVEN_10Y', {}).get('value', 'N/A')}%
    - VIX: {add.get('VIX', {}).get('value', 'N/A')}
    """
    
    # Compile top articles for context
    context_lines = []
    for cat, articles in category_buckets.items():
        top = [a for a in articles if a["impact"] in ("HIGH", "MEDIUM")]
        if top:
            context_lines.append(f"\n[{cat}]")
            for a in top[:5]:
                context_lines.append(f"- {a['title']} ({a['source']})")
                
    news_context = "\n".join(context_lines) if context_lines else "No major news today."
    
    prompt = f"""
    You are an expert Chief Actuary reviewing the daily market and news digest.
    
    CURRENT MARKET DATA:
    {market_narrative}
    
    TOP NEWS DEVELOPMENTS:
    {news_context}
    
    Generate a concise executive briefing (max 4 paragraphs). Include a section called "Consulting Opportunities" detailing how these developments might create advisory needs (e.g., reserving updates, ALM shifts, PBR filings) for an actuarial consulting firm. Use basic Markdown styling (headers, bolding, bullet points).
    """
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            temperature=0.3,
            max_tokens=800,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"    Groq API Error: {e}")
        return "Executive briefing unavailable due to an LLM generation error."
