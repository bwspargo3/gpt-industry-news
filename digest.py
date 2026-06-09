import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config
from intelligence import (
    collect_news,
    deduplicate_articles,
    filter_already_seen,
    filter_noise,
    score_and_tag,
    summarize_with_gemini,
    extract_opportunity_signals,
)
from email_template import build_email_html
from market_data import build_market_snapshot


def send_email(html_body):
    msg            = MIMEMultipart("alternative")
    msg["Subject"] = "Life & Annuity Actuarial Intelligence"
    msg["From"]    = config.GMAIL_USER
    msg["To"]      = config.TO_EMAIL
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(config.GMAIL_USER, config.GMAIL_PASS)
        server.sendmail(config.GMAIL_USER, config.TO_EMAIL, msg.as_string())
    print("    Email sent.")


def main():
    print("\n=== Life & Annuity Actuarial Intelligence ===\n")

    print("[1] Market data...")
    market = build_market_snapshot()

    print("[2] Collecting news...")
    raw = collect_news()

    print("[3] Deduplicating (within-run)...")
    unique = deduplicate_articles(raw)

    print("[4] Filtering noise...")
    filtered = filter_noise(unique)

    print("[5] Filtering already-seen articles (cross-day)...")
    fresh, suppressed = filter_already_seen(filtered)
    print(f"    {suppressed} articles suppressed (already delivered). "
          f"{len(fresh)} new articles proceeding.")

    print("[6] Scoring and tagging...")
    buckets = score_and_tag(fresh)
    total   = sum(len(v) for v in buckets.values())
    print(f"    {total} articles across {len(buckets)} categories")

    print("[7] Extracting opportunity signals...")
    signals = extract_opportunity_signals(buckets)
    print(f"    {len(signals)} consulting opportunity signals flagged")

    print("[8] Generating briefing with Gemini...")
    summary = summarize_with_gemini(buckets, market)

    print("[9] Building email...")
    html = build_email_html(market, buckets, summary, signals)

    print("[10] Sending...")
    send_email(html)

    print("\n✓ Done\n")


if __name__ == "__main__":
    main()
