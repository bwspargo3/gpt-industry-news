import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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


def send_email(html_body):
    msg            = MIMEMultipart("alternative")
    msg["Subject"] = "Life & Annuity Actuarial Intelligence"
    msg["From"]    = config.GMAIL_USER
    msg["To"]      = config.RECIPIENT_EMAIL
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(config.GMAIL_USER, config.GMAIL_APP_PASSWORD)
        server.sendmail(
            config.GMAIL_USER, config.RECIPIENT_EMAIL, msg.as_string()
        )
    print("    Email sent.")


def main():
    print("\n=== Life & Annuity Actuarial Intelligence ===\n")

    print("[1] Market data...")
    market = build_market_snapshot()

    print("[2] Collecting news...")
    raw = collect_news()

    print("[3] Deduplicating...")
    unique = deduplicate_articles(raw)

    print("[4] Filtering noise...")
    filtered = filter_noise(unique)

    print("[5] Scoring and tagging...")
    buckets = score_and_tag(filtered)
    total   = sum(len(v) for v in buckets.values())
    print(f"    {total} articles across {len(buckets)} categories")

    print("[6] Generating briefing...")
    summary = summarize_with_groq(buckets, market)

    print("[7] Building email...")
    html = build_email_html(market, buckets, summary)

    print("[8] Sending...")
    send_email(html)

    print("\n✓ Done\n")


if __name__ == "__main__":
    main()
