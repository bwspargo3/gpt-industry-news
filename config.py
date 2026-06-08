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

NEWSAPI_KEY = (
    env("NEWSAPI_KEY")
    or env("NEWS_API_KEY")
    or env("NEWS_API")
)

if not NEWSAPI_KEY:
    print("⚠️  WARNING: NEWSAPI_KEY not set. NewsAPI disabled.")

GMAIL_USER = env("GMAIL_USER", required=True)
GMAIL_PASS = env("GMAIL_APP_PASSWORD", required=True)
TO_EMAIL   = env("RECIPIENT_EMAIL", GMAIL_USER)

# ------------------------------------------------------------------
# Collection settings
# ------------------------------------------------------------------

DAYS_BACK               = 5
MAX_ARTICLES            = 500
MAX_ARTICLES_PER_QUERY  = 25
MAX_ARTICLES_PER_SECTION = 20

# ------------------------------------------------------------------
# Noise filtering
# ------------------------------------------------------------------

NOISE_PHRASES = [
    # Generic
    "press release", "advertisement", "sponsored", "subscribe",
    # Sports / celebrity
    "police dog", "kyle busch", "pga tournament",
    # P&C / unrelated insurance
    "offshore wind farm", "homeowners insurance", "flood insurance",
    "auto insurance rate", "auto rates", "hurricane season",
    "workers compensation", "workers' compensation", "workers' comp",
    "property casualty", "commercial lines", "surety bond",
    "crop insurance", "pet insurance", "travel insurance",
    "casualty treaty", "casualty actuarial society",
    # Non-insurance business
    "compounding pharmac", "kids' activities", "great place to work",
    "zymo research", "real estate", "stream realty",
    "venture funding", "recess expands", "stablecoin", "crypto etf",
    # Political / regulatory noise
    "uzbekistan", "lie detector", "medicaid mandates",
    "south koreans' annual", "poland aims", "nami statement",
    "earthquake",
    # Federal Register false positives
    "anadromous fish", "endangered species", "migratory bird",
    "wetlands", "pesticide", "food safety", "aviation", "railroad",
    "coast guard", "nuclear", "veterans", "tribal",
    "forestry", "mining", "osha", "occupational safety",
    "privacy act of 1974",      # USPS/Federal Register noise
    "system of records",        # USPS/Federal Register noise
    "postal service",           # USPS
    "highway contract route",   # USPS
    # Consumer personal finance blogs
    "when i was sold",          # White Coat Investor IUL article
    "white coat investor",
    "personal finance blog",
    # International noise (non-US markets)
    "crore",                    # Indian currency unit
    "rs 2,000", "rs 5,000",    # Indian rupees
    "lakh",                     # Indian unit
    # People moves for non-life roles
    "agriculture platform senior",
    "commercial underwriter",
    "workplace well-being",
    # Cyber (non-insurance)
    "cyber crime", "cyber problem",
]

SOURCE_MIN_SCORES = {
    "NAIC LATF": 0,
    "SEC EDGAR": 0,
    "Google News": 0,
}

# ------------------------------------------------------------------
# Impact thresholds
# ------------------------------------------------------------------

HIGH_IMPACT_THRESHOLD   = 15
MEDIUM_IMPACT_THRESHOLD =  8
LOW_IMPACT_MIN_SCORE    =  3

LOW_IMPACT_ALLOWED_TAGS = [
    "REGULATORY", "VALUATION", "CAPITAL", "REINSURANCE",
    "ALM", "ACCOUNTING", "EXPERIENCE", "RESEARCH", "CARRIER",
]

# ------------------------------------------------------------------
# Actuarial keyword scoring
# ------------------------------------------------------------------

EVENT_PATTERNS = {
    "REINSURANCE": [
        "reinsurance",
        "coinsurance",
        "funded reinsurance",
        "ceded",
        "assumption transaction",
        "block transaction",
        "risk transfer",
    ],

    "EARNINGS": [
        "quarterly results",
        "earnings",
        "financial results",
        "reported results",
        "q1",
        "q2",
        "q3",
        "q4",
    ],

    "PRODUCT": [
        "myga",
        "fixed indexed annuity",
        "fia",
        "rila",
        "indexed universal life",
        "iul",
        "new product",
        "product launch",
    ],

    "CAPITAL": [
        "risk based capital",
        "rbc",
        "capital management",
        "surplus",
        "solvency",
    ],

    "REGULATORY": [
        "naic",
        "latf",
        "vm-20",
        "vm-21",
        "vm-22",
        "pbr",
        "principle based reserving",
        "actuarial guideline",
    ],

    "RATINGS": [
        "am best",
        "fitch",
        "moodys",
        "s&p",
        "outlook revised",
        "credit rating",
    ],

    "MNA": [
        "acquisition",
        "merger",
        "acquire",
        "purchase",
        "transaction",
    ],

    "RESEARCH": [
        "society of actuaries",
        "american academy of actuaries",
        "milliman",
        "research report",
        "experience study",
    ],

    "COMMUNITY": [
        "charity",
        "community",
        "volunteer",
        "foundation",
        "scholarship",
        "award",
        "best workplace",
        "top employer",
    ],
}

EVENT_SCORES = {
    "REINSURANCE": 20,
    "CAPITAL": 18,
    "REGULATORY": 18,
    "RATINGS": 16,
    "EARNINGS": 15,
    "MNA": 15,
    "PRODUCT": 12,
    "RESEARCH": 10,
    "COMMUNITY": -25,
}

# ------------------------------------------------------------------
# Function tags
# ------------------------------------------------------------------

FUNCTION_TAGS = {
    "vm-20": ["VALUATION"], "vm-22": ["VALUATION"],
    "reserve": ["VALUATION"], "valuation": ["VALUATION"],
    "pbr": ["VALUATION"], "principle based reserving": ["VALUATION"],
    "ldti": ["ACCOUNTING"], "asc 944": ["ACCOUNTING"],
    "naic": ["REGULATORY"], "latf": ["REGULATORY"],
    "actuarial guideline": ["REGULATORY"],
    "mortality": ["EXPERIENCE"], "experience study": ["EXPERIENCE"],
    "reinsurance": ["REINSURANCE"],
    "rbc": ["CAPITAL"], "risk based capital": ["CAPITAL"],
    "alm": ["ALM"], "private credit": ["ALM"],
    "asset liability management": ["ALM"],
    "society of actuaries": ["RESEARCH"],
    "american academy of actuaries": ["RESEARCH"],
    "fia": ["PRICING", "ALM"], "fixed indexed annuity": ["PRICING", "ALM"],
    "rila": ["PRICING", "ALM"], "myga": ["PRICING"],
    "iul": ["PRICING"], "indexed universal life": ["PRICING"],
}
