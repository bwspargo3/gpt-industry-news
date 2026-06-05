import asyncio

from ingest import ingest_all
from scoring import score_articles
from dedupe import dedupe_semantic
from llm import summarize
from emailer import send_email
from db import init_db, insert_articles, make_id


SOURCES = [
    {"type": "rss", "url": "https://www.insurancejournal.com/rss/lifehealth/"},
    {"type": "google", "query": "VM-20 life insurance"},
]


async def main():
    await init_db()

    print("Ingesting...")
    articles = await ingest_all(SOURCES)

    print("Scoring...")
    articles = score_articles(articles)

    print("Deduping (semantic)...")
    articles = dedupe_semantic(articles)

    print("Saving...")
    for a in articles:
        a["id"] = make_id(a["title"], a["url"])

    await insert_articles(articles)

    print("Summarizing...")
    summary = summarize(articles)

    print("Sending email...")
    send_email(summary)

    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
