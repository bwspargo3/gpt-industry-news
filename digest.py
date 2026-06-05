import config
from intelligence import (
    collect_news,
    deduplicate_articles,
    filter_noise,
    score_and_tag,
    summarize_with_groq,
)
from email_template import build_email_html
from market_data import build_market_snapshot
import email_sender


def run_digest():
    print("\n=== Life & Annuity Actuarial Intelligence — ARC | Springline ===\n")

    print("[1] Building market snapshot...")
    market = build_market_snapshot()

    print("[2] Collecting news...")
    raw = collect_news()

    print("[3] Deduplicating...")
    unique = deduplicate_articles(raw)

    print("[4] Filtering noise...")
    filtered = filter_noise(unique)

    print("[5] Scoring and tagging...")
    category_buckets = score_and_tag(filtered)
    total = sum(len(v) for v in category_buckets.values())
    print(f"  {total} articles across {len(category_buckets)} categories")

    print("[6] Generating executive briefing...")
    summary = summarize_with_groq(category_buckets, market)

    print("[7] Building email...")
    html = build_email_html(market, category_buckets, summary)

    print("[8] Sending email...")
    email_sender.send_email(html)

    print("\n✓ Complete\n")


if __name__ == "__main__":
    run_digest()
