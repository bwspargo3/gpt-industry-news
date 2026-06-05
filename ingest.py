import aiohttp
import asyncio
import feedparser
from datetime import datetime, timedelta
import config


HEADERS = {"User-Agent": "ActuarialDigest/2.0"}


async def fetch_rss(session, url):
    try:
        async with session.get(url, headers=HEADERS, timeout=15) as r:
            text = await r.text()
            feed = feedparser.parse(text)

            out = []
            for e in feed.entries[:20]:
                out.append({
                    "title": e.get("title", ""),
                    "url": e.get("link", ""),
                    "snippet": e.get("summary", ""),
                    "source": "RSS",
                })
            return out
    except:
        return []


async def fetch_google(session, query):
    url = f"https://news.google.com/rss/search?q={query}"
    return await fetch_rss(session, url)


async def ingest_all(sources):
    async with aiohttp.ClientSession() as session:
        tasks = []

        for s in sources:
            if s["type"] == "rss":
                tasks.append(fetch_rss(session, s["url"]))
            else:
                tasks.append(fetch_google(session, s["query"]))

        results = await asyncio.gather(*tasks)

    flat = []
    for r in results:
        flat.extend(r)

    return flat
