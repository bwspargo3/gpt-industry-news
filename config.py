import os

def env(name, default=None, required=False):
    value = os.getenv(name, default)

    if required and not value:
        raise ValueError(f"Missing env var: {name}")

    return value


# ------------------------------------------------------------------
# Environment
# ------------------------------------------------------------------

GROQ_API_KEY = env("GROQ_API_KEY", required=True)

# ------------------------------------------------------------------
# NewsAPI Key (ROBUST FIX)
# ------------------------------------------------------------------

NEWSAPI_KEY = (
    env("NEWSAPI_KEY")
    or env("NEWS_API_KEY")
    or env("NEWS_API")
)

if not NEWSAPI_KEY:
    print("⚠️ WARNING: NEWSAPI_KEY is not set. NewsAPI will be disabled.")

GMAIL_USER = env("GMAIL_USER", required=True)
GMAIL_PASS = env("GMAIL_APP_PASSWORD", required=True)

TO_EMAIL = env("RECIPIENT_EMAIL", GMAIL_USER)

# ------------------------------------------------------------------
# Collection
# ------------------------------------------------------------------

DAYS_BACK = 5

MAX_ARTICLES = 500
MAX_ARTICLES_PER_QUERY = 25
MAX_ARTICLES_PER_SECTION = 20

# ------------------------------------------------------------------
# Database
# ------------------------------------------------------------------

DB_PATH = "digest.db"

# ------------------------------------------------------------------
# Dedupe
# ------------------------------------------------------------------

EMBED_BATCH_SIZE = 20
SIMILARITY_THRESHOLD = 0.88

# ------------------------------------------------------------------
# Noise filtering
# ------------------------------------------------------------------

NOISE_PHRASES = [
    "press release",
    "advertisement",
    "sponsored",
    "subscribe",
    "newsletter",
]

SOURCE_MIN_SCORES = {
    "NAIC LATF": 0,
    "SEC EDGAR": 0,
    "Google News": 0,
}

# ------------------------------------------------------------------
# Scoring thresholds
# ------------------------------------------------------------------

HIGH_IMPACT_THRESHOLD = 15
MEDIUM_IMPACT_THRESHOLD = 8

LOW_IMPACT_MIN_SCORE = 3

LOW_IMPACT_ALLOWED_TAGS = [
    "REGULATORY",
    "VALUATION",
    "CAPITAL",
    "REINSURANCE",
    "ALM",
    "ACCOUNTING",
    "EXPERIENCE",
    "RESEARCH",
    "CARRIER",
]

# ------------------------------------------------------------------
# Actuarial keyword scoring
# ------------------------------------------------------------------

ACTUARIAL_KEYWORDS = {

    # Regulatory
    "naic": 6,
    "latf": 8,
    "regulation": 4,
    "actuarial guideline": 7,

    # Reserving
    "vm-20": 10,
    "vm-22": 10,
    "pbr": 8,
    "principle based reserving": 10,
    "reserve": 5,
    "valuation": 5,
    "cash flow testing": 6,
    "asset adequacy": 6,

    # Accounting
    "ldti": 8,
    "asc 944": 8,
    "fasb": 5,

    # Capital
    "risk based capital": 8,
    "rbc": 7,
    "rating agency": 5,

    # Reinsurance
    "reinsurance": 7,
    "bermuda": 4,

    # Mortality
    "mortality": 6,
    "experience study": 6,
    "longevity": 5,

    # Annuities
    "fia": 5,
    "fixed indexed annuity": 6,
    "rila": 6,
    "myga": 5,

    # Products
    "iul": 5,
    "indexed universal life": 6,
    "term insurance": 4,

    # Investments
    "private credit": 6,
    "asset liability management": 7,
    "alm": 7,

    # Research
    "society of actuaries": 5,
    "american academy of actuaries": 5,

    # Carrier
    "acquisition": 5,
    "transaction": 4,
}

# ------------------------------------------------------------------
# Tags
# ------------------------------------------------------------------

FUNCTION_TAGS = {

    "vm-20": ["VALUATION"],
    "vm-22": ["VALUATION"],
    "reserve": ["VALUATION"],

    "ldti": ["ACCOUNTING"],

    "naic": ["REGULATORY"],
    "latf": ["REGULATORY"],

    "mortality": ["EXPERIENCE"],
    "experience study": ["EXPERIENCE"],

    "reinsurance": ["REINSURANCE"],

    "rbc": ["CAPITAL"],
    "risk based capital": ["CAPITAL"],

    "alm": ["ALM"],
    "private credit": ["ALM"],

    "society of actuaries": ["RESEARCH"],
    "american academy of actuaries": ["RESEARCH"],
}
