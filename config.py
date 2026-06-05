import os

def env(name, default=None, required=False):
    v = os.getenv(name, default)
    if required and not v:
        raise ValueError(f"Missing env var: {name}")
    return v


GROQ_API_KEY = env("GROQ_API_KEY", required=True)
NEWSAPI_KEY  = env("NEWSAPI_KEY")

GMAIL_USER = env("GMAIL_USER", required=True)
GMAIL_PASS = env("GMAIL_APP_PASSWORD", required=True)
TO_EMAIL   = env("RECIPIENT_EMAIL", GMAIL_USER)

DAYS_BACK = 3

DB_PATH = "digest.db"

MAX_ARTICLES = 500
EMBED_BATCH_SIZE = 20
SIMILARITY_THRESHOLD = 0.88

# ----------------------------
# Intelligence / scoring config
# ----------------------------

NOISE_PHRASES = [
    "press release",
    "sponsored",
    "advertisement",
    "subscribe",
    "sign up",
    "newsletter",
]

SOURCE_MIN_SCORES = {
    "soa": 0.6,
    "thinkadvisor": 0.6,
    "limra": 0.65,
    "google_news": 0.5,
    "rss": 0.55,
}
