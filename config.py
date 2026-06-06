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

ACTUARIAL_KEYWORDS = {
    # Regulatory
    "naic": 6, "latf": 8, "regulation": 4, "actuarial guideline": 7,

    # Reserving
    "vm-20": 10, "vm-22": 10, "pbr": 8,
    "principle based reserving": 10,
    "reserve": 5, "valuation": 5,
    "cash flow testing": 6, "asset adequacy": 6,

    # Accounting
    "ldti": 8, "asc 944": 8, "fasb": 5,

    # Capital
    "risk based capital": 8, "rbc": 7, "rating agency": 5,

    # Reinsurance
    "reinsurance": 7, "bermuda": 4,

    # Mortality
    "mortality": 6, "experience study": 6, "longevity": 5,

    # Annuities
    "fia": 5, "fixed indexed annuity": 6, "rila": 6, "myga": 5,

    # Products
    "iul": 5, "indexed universal life": 6, "term insurance": 4,

    # Investments
    "private credit": 6, "asset liability management": 7, "alm": 7,

    # Research
    "society of actuaries": 5, "american academy of actuaries": 5,

    # Transactions
    "acquisition": 5, "transaction": 4,

    # Watchlist carriers
    "kansas city life": 10, "ameritas": 10, "securian": 10,
    "midland national": 10, "north american company": 8,
    "pacific life": 10, "brighthouse": 10, "cno financial": 10,
    "global atlantic": 10, "protective life": 10, "lincoln financial": 8,
    "transamerica": 8, "mutual of omaha": 8, "jackson national": 8,
    "26north": 10, "independent life": 8, "principal financial": 8,
    "nassau financial": 10, "athene": 8,
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
