import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import GMAIL_USER, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL

from intelligence import (
    collect_news,
    deduplicate_articles,
    filter_noise,
    score_articles,
    identify_consulting_opportunities,
    summarize_with_groq,
)

from market_data import build_market_snapshot

from email_template import build_email_html

# ---------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------

def send_email(subject, html_body):

    msg            = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_USER
    msg["To"]      = RECIPIENT_EMAIL

    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, RECIPIENT_EMAIL, msg.as_string())

# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():

    print("\n=== LIFE & ANNUITY ACTUARIAL INTELLIGENCE (ARC | Springline) ===\n")

    print("[1] Building market snapshot...")
    market = build_market_snapshot()

    print("[2] Collecting news...")
    category_buckets = collect_news()

    print("[3] Deduplicating...")
    category_buckets = deduplicate_articles(category_buckets)

    print("[4] Filtering noise...")
    category_buckets = filter_noise(category_buckets)

    print("[5] Scoring and tagging articles...")
    category_buckets = score_articles(category_buckets)

    total = sum(len(v) for v in category_buckets.values())
    print(f"    {total} articles after filtering")

    print("[6] Identifying consulting opportunities...")
    consulting_opportunities = identify_consulting_opportunities(category_buckets)

    print("[7] Generating executive briefing...")
    summary = summarize_with_groq(category_buckets, market)

    print("[8] Building HTML email...")
    html = build_email_html(
        summary,
        market,
        category_buckets,
        consulting_opportunities,
    )

    print("[9] Sending email...")
    send_email("Life & Annuity Actuarial Intelligence | ARC", html)

    print("\n✓ Complete\n")

if __name__ == "__main__":
    main()
