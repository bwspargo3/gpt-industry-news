import os

def env(name, default=None, required=False):
    value = os.getenv(name, default)
    if required and not value:
        raise ValueError(f"Missing env var: {name}")
    return value

# ------------------------------------------------------------------
# Environment
# ------------------------------------------------------------------

# Gemini replaces Groq for summarization.
# Get a free key in ~2 minutes at https://aistudio.google.com/apikey
GEMINI_API_KEY = env("GEMINI_API_KEY", required=True)

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

DAYS_BACK                = 7    # Collect 7 days; 24h display filter handles freshness
MAX_ARTICLES             = 500
MAX_ARTICLES_PER_QUERY   = 30
MAX_ARTICLES_PER_SECTION = 25

# ------------------------------------------------------------------
# Noise filtering
# ------------------------------------------------------------------

NOISE_PHRASES = [
    # Sports / entertainment
    "police dog", "kyle busch", "pga tournament", "world cup",
    "worker focus", "worker attendance", "sporting event",

    # P&C / non-life lines
    "homeowners insurance", "flood insurance", "auto insurance rate",
    "auto rates", "hurricane season", "workers compensation",
    "workers' compensation", "workers' comp", "property casualty",
    "commercial lines", "surety bond", "crop insurance", "pet insurance",
    "travel insurance", "casualty treaty", "casualty actuarial society",
    "offshore wind farm", "parametric", "catastrophe bond",
    "cat bond", "nat cat", "natural catastrophe",

    # Automotive / safety
    "seat belt", "highway safety", "vehicle recall", "commercial vehicle",
    "pickup truck", "ford recall", "iihs", "nhtsa",

    # Personnel appointments at non-life-actuarial firms
    # (reinsurance brokers, P&C specialty, international ops)
    "global markets, australia", "commercial claims",
    "large personal property", "specialty reinsurance",
    "corporate solutions france", "directeur général",
    "demo day", "retail agent", "retail agents",

    # Consumer / personal finance noise
    "white coat investor", "personal finance blog",
    "when i was sold", "kids' activities",

    # International / irrelevant regulatory
    "uzbekistan", "lie detector", "medicaid mandates",
    "south koreans' annual", "poland aims", "nami statement",
    "privacy act of 1974", "system of records", "postal service",
    "highway contract route",

    # Environmental / federal non-insurance
    "earthquake", "anadromous fish", "endangered species", "migratory bird",
    "wetlands", "pesticide", "food safety", "aviation", "railroad",
    "coast guard", "nuclear", "veterans", "tribal",
    "forestry", "mining", "osha", "occupational safety",

    # Low-quality / off-topic sources
    "ritholtz.com", "mib:", "barry ritholtz", "bloomberg masters",
    "yahoo entertainment", "stockstory", "seeking alpha",
    "nba finals", "jalen brunson", "wembanyama", "knicks",
    "sports & entertainment", "sports entertainment",

    # Junk / low-signal
    "compounding pharmac", "great place to work",
    "zymo research", "stream realty", "recess expands",
    "stablecoin", "crypto etf", "venture funding",
    "crore", "rs 2,000", "rs 5,000", "lakh",
    "agriculture platform senior", "commercial underwriter",
    "workplace well-being", "cyber crime", "cyber problem",
    "suzlon", "wind player", "general services administration", "gsa", "gsar",
    "fema", "hseep", "homeland security exercise", "after action report/improvement",
]

# Whitelist overrides: if any of these phrases appear in the article,
# the noise filter will NOT drop it even if a noise phrase also matches.
# Protects legitimate life/annuity articles that brush against noise terms.
NOISE_WHITELIST = [
    "private credit", "asset liability", "annuity portfolio",
    "insurance holding", "life insurer", "life reinsurance",
    "asset intensive", "funded reinsurance", "block reinsurance",
    "vm-20", "vm-22", "pbr", "ldti", "rbc", "iul", "myga", "fia", "rila",
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
        "reinsurance", "coinsurance", "funded reinsurance",
        "ceded", "assumption transaction", "block transaction", "risk transfer",
        "asset-intensive", "funded reinsurance",
    ],
    "EARNINGS": [
        "quarterly results", "earnings", "financial results",
        "reported results", "q1", "q2", "q3", "q4",
    ],
    "PRODUCT": [
        "myga", "fixed indexed annuity", "fia", "rila",
        "indexed universal life", "iul", "personal income annuity", "pia",
        "new product", "product launch",
    ],
    "CAPITAL": [
        "risk based capital", "rbc", "capital management", "surplus", "solvency",
    ],
    "REGULATORY": [
        "naic", "latf", "vm-20", "vm-21", "vm-22", "pbr",
        "principle based reserving", "actuarial guideline",
    ],
    "RATINGS": [
        "am best", "fitch", "moodys", "s&p", "outlook revised", "credit rating",
    ],
    "MNA": [
        "acquisition", "merger", "acquire", "purchase", "transaction",
    ],
    "RESEARCH": [
        "society of actuaries", "american academy of actuaries",
        "milliman", "research report", "experience study",
    ],
    "COMMUNITY": [
        "charity", "community", "volunteer", "foundation",
        "scholarship", "award", "best workplace", "top employer",
    ],
}

EVENT_SCORES = {
    "REINSURANCE": 20, "CAPITAL": 18, "REGULATORY": 18, "RATINGS": 16,
    "EARNINGS": 12, "MNA": 15, "PRODUCT": 12, "RESEARCH": 15, "COMMUNITY": -25,
}

FUNCTION_TAGS = {
    "vm-20": ["VALUATION"], "vm-22": ["VALUATION"],
    "goes": ["VALUATION"], "generator of economic scenarios": ["VALUATION"],
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
    "pia": ["PRICING"], "personal income annuity": ["PRICING"],
}

# ------------------------------------------------------------------
# Consulting opportunity signals
# Articles matching these patterns get flagged in a dedicated
# "Opportunity Signals" section — the core business-development layer.
# ------------------------------------------------------------------

CONSULTING_SIGNALS = {
    "Reinsurance Transaction": [
        "assumption reinsurance", "block transaction", "ceded block",
        "coinsurance transaction", "funded reinsurance", "risk transfer",
        "assumption transaction",
    ],
    "Reserve Strengthening": [
        "reserve strengthening", "reserve increase", "restatement",
        "material weakness", "unlocking", "assumption update",
        "reserve review",
    ],
    "Regulatory Response Needed": [
        "consent order", "market conduct examination", "regulatory action",
        "corrective action", "cease and desist", "enforcement action",
    ],
    "New Product / Filing": [
        "product launch", "new product", "product filing",
        "filing approved", "rate filing", "form filing",
    ],
    "M&A Integration": [
        "acquisition closed", "merger complete", "integration",
        "post-acquisition", "combined company",
    ],
    "Actuarial Guideline Change": [
        "actuarial guideline", "ag 49", "ag 43", "vm-20", "vm-22",
        "pbr implementation", "principle based",
    ],
    "Rating Review": [
        "rating review", "placed under review", "creditwatch",
        "outlook negative", "downgrade", "upgrade",
    ],
}
