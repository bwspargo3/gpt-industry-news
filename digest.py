import config
from intelligence import (
    collect_news,
    deduplicate_articles,
    filter_noise,
    score_and_tag,
    summarize_with_groq
)
from email_template import build_email_html
from market_data import build_market_snapshot
import email_sender

def run_digest():
    print("Starting daily intelligence digest...")
    raw = collect_news()
    unique = deduplicate_articles(raw)
    filtered = filter_noise(unique)
    category_buckets = score_and_tag(filtered)
    market = build_market_snapshot() 
    summary = summarize_with_groq(category_buckets, market)
    html = build_email_html(market, category_buckets, summary)
    email_sender.send_email(html)
    print("Digest successfully sent.")

if __name__ == "__main__":
    run_digest()
