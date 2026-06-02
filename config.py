import os
from datetime import datetime

# -----------------------------------------------------------------------------
# Environment Variables
# -----------------------------------------------------------------------------

GROQ_API_KEY = os.environ["GROQ_API_KEY"]

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]

RECIPIENT_EMAIL = os.environ.get(
    "RECIPIENT_EMAIL",
    GMAIL_USER
)

# -----------------------------------------------------------------------------
# Runtime Settings
# -----------------------------------------------------------------------------

IS_FRIDAY = datetime.utcnow().weekday() == 4

DAYS_BACK = 7 if IS_FRIDAY else 3

MAX_ARTICLES_PER_QUERY = 10

MAX_ARTICLES_PER_SECTION = 15

# -----------------------------------------------------------------------------
# Treasury Monitoring
# -----------------------------------------------------------------------------

TREASURY_SERIES = {
    "2Y": "DGS2",
    "5Y": "DGS5",
    "10Y": "DGS10",
    "30Y": "DGS30"
}

# -----------------------------------------------------------------------------
# Relevance Scoring Keywords
# -----------------------------------------------------------------------------

ACTUARIAL_KEYWORDS = {

    "vm-20": 15,
    "vm20": 15,

    "vm-22": 15,
    "vm22": 15,

    "latf": 12,
    "life actuarial task force": 12,

    "principle based reserving": 12,
    "pbr": 12,

    "asset adequacy": 10,
    "cash flow testing": 10,

    "ldti": 12,
    "asc 944": 10,

    "reserve": 8,
    "reserving": 8,
    "valuation": 8,

    "rbc": 10,
    "risk based capital": 10,

    "mortality": 8,
    "experience study": 8,
    "lapse": 8,

    "reinsurance": 8,
    "coinsurance": 8,
    "funds withheld": 8,

    "annuity": 6,
    "fia": 6,
    "rila": 6,
    "iul": 6,

    "asset liability": 8,
    "alm": 8,

    "hedging": 6,

    "actuarial": 4,
    "actuary": 4
}

# -----------------------------------------------------------------------------
# Impact Thresholds
# -----------------------------------------------------------------------------

HIGH_IMPACT_THRESHOLD = 12
MEDIUM_IMPACT_THRESHOLD = 7

# -----------------------------------------------------------------------------
# Persistent Watch List
# -----------------------------------------------------------------------------

WATCH_LIST = [

    "VM-20",
    "VM-22",
    "Principle-Based Reserving",
    "LDTI",

    "Asset Adequacy Testing",
    "Cash Flow Testing",

    "RBC Modernization",

    "Life Reinsurance",
    "Bermuda Reinsurance",

    "FIA Sales",
    "RILA Sales",

    "Mortality Experience",

    "Policyholder Behavior",

    "Private Credit",

    "Asset Liability Management"
]
