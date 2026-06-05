import aiosqlite
import hashlib
from datetime import datetime
import config


CREATE_SQL = """
CREATE TABLE IF NOT EXISTS articles (
    id TEXT PRIMARY KEY,
    title TEXT,
    url TEXT,
    source TEXT,
    snippet TEXT,
    score REAL,
    impact TEXT,
    tags TEXT,
    created_at TEXT
);
"""


def make_id(title, url):
    return hashlib.md5((title + url).encode()).hexdigest()


async def init_db():
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(CREATE_SQL)
        await db.commit()


async def insert_articles(articles):
    async with aiosqlite.connect(config.DB_PATH) as db:
        for a in articles:
            await db.execute("""
                INSERT OR IGNORE INTO articles
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                a["id"],
                a["title"],
                a["url"],
                a["source"],
                a["snippet"],
                a.get("score", 0),
                a.get("impact", "LOW"),
                ",".join(a.get("tags", [])),
                datetime.utcnow().isoformat(),
            ))
        await db.commit()


async def fetch_all_articles():
    async with aiosqlite.connect(config.DB_PATH) as db:
        cursor = await db.execute("SELECT * FROM articles")
        rows = await cursor.fetchall()
        return rows
