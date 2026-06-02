{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import smtplib\
\
from email.mime.multipart import MIMEMultipart\
from email.mime.text import MIMEText\
\
from config import (\
    GMAIL_USER,\
    GMAIL_APP_PASSWORD,\
    RECIPIENT_EMAIL\
)\
\
from intelligence import (\
    collect_news,\
    deduplicate_articles,\
    score_articles,\
    identify_consulting_opportunities,\
    summarize_with_groq\
)\
\
from market_data import (\
    build_market_snapshot\
)\
\
from email_template import (\
    build_email_html\
)\
\
# ---------------------------------------------------------------------\
# Email\
# ---------------------------------------------------------------------\
\
def send_email(subject, html_body):\
\
    msg = MIMEMultipart("alternative")\
\
    msg["Subject"] = subject\
    msg["From"] = GMAIL_USER\
    msg["To"] = RECIPIENT_EMAIL\
\
    msg.attach(\
        MIMEText(\
            html_body,\
            "html"\
        )\
    )\
\
    with smtplib.SMTP_SSL(\
        "smtp.gmail.com",\
        465\
    ) as server:\
\
        server.login(\
            GMAIL_USER,\
            GMAIL_APP_PASSWORD\
        )\
\
        server.sendmail(\
            GMAIL_USER,\
            RECIPIENT_EMAIL,\
            msg.as_string()\
        )\
\
# ---------------------------------------------------------------------\
# Main\
# ---------------------------------------------------------------------\
\
def main():\
\
    print(\
        "\\n=== LIFE & ANNUITY ACTUARIAL INTELLIGENCE ===\\n"\
    )\
\
    print(\
        "[1] Building market snapshot..."\
    )\
\
    market = build_market_snapshot()\
\
    print(\
        "[2] Collecting news..."\
    )\
\
    category_buckets = collect_news()\
\
    print(\
        "[3] Deduplicating..."\
    )\
\
    category_buckets = (\
        deduplicate_articles(\
            category_buckets\
        )\
    )\
\
    print(\
        "[4] Scoring articles..."\
    )\
\
    category_buckets = (\
        score_articles(\
            category_buckets\
        )\
    )\
\
    total_articles = sum(\
        len(x)\
        for x\
        in category_buckets.values()\
    )\
\
    print(\
        f"    \{total_articles\} relevant articles"\
    )\
\
    print(\
        "[5] Consulting opportunities..."\
    )\
\
    consulting_opportunities = (\
        identify_consulting_opportunities(\
            category_buckets\
        )\
    )\
\
    print(\
        "[6] Generating executive briefing..."\
    )\
\
    summary = summarize_with_groq(\
        category_buckets,\
        market\
    )\
\
    print(\
        "[7] Building HTML email..."\
    )\
\
    html = build_email_html(\
        summary,\
        market,\
        category_buckets,\
        consulting_opportunities\
    )\
\
    print(\
        "[8] Sending email..."\
    )\
\
    send_email(\
        "Life & Annuity Actuarial Intelligence",\
        html\
    )\
\
    print(\
        "\\n\uc0\u10003  Complete\\n"\
    )\
\
if __name__ == "__main__":\
    main()}