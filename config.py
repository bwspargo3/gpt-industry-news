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
    "2Y":  "DGS2",
    "5Y":  "DGS5",
    "10Y": "DGS10",
    "30Y": "DGS30",
}

# -----------------------------------------------------------------------------
# Actuarial Function Tags
# Used to tag each article for the relevant actuarial audience
# -----------------------------------------------------------------------------

FUNCTION_TAGS = {

    # Valuation / Reserving
    "vm-20":                    ["VALUATION"],
    "vm20":                     ["VALUATION"],
    "vm-22":                    ["VALUATION"],
    "vm22":                     ["VALUATION"],
    "principle based reserving":["VALUATION"],
    "pbr":                      ["VALUATION"],
    "asset adequacy":           ["VALUATION"],
    "cash flow testing":        ["VALUATION"],
    "ag 38":                    ["VALUATION"],
    "latf":                     ["VALUATION", "REGULATORY"],
    "life actuarial task force": ["VALUATION", "REGULATORY"],
    "ldti":                     ["VALUATION", "ACCOUNTING"],
    "asc 944":                  ["ACCOUNTING"],
    "reserve":                  ["VALUATION"],
    "reserving":                ["VALUATION"],
    "valuation":                ["VALUATION"],

    # Pricing / Product
    "pricing":                  ["PRICING"],
    "product development":      ["PRICING"],
    "indexed universal life":   ["PRICING"],
    "iul":                      ["PRICING"],
    "term insurance":           ["PRICING"],
    "term life":                ["PRICING"],
    "fia":                      ["PRICING", "ALM"],
    "fixed indexed annuity":    ["PRICING", "ALM"],
    "rila":                     ["PRICING", "ALM"],

    # ALM / Investments
    "asset liability":          ["ALM"],
    "alm":                      ["ALM"],
    "hedging":                  ["ALM"],
    "private credit":           ["ALM"],
    "spread":                   ["ALM"],
    "duration":                 ["ALM"],
    "interest rate":            ["ALM"],

    # Reinsurance
    "reinsurance":              ["REINSURANCE"],
    "coinsurance":              ["REINSURANCE"],
    "funds withheld":           ["REINSURANCE"],
    "modco":                    ["REINSURANCE"],
    "yrt":                      ["REINSURANCE"],
    "asset intensive":          ["REINSURANCE"],
    "bermuda":                  ["REINSURANCE"],

    # Capital
    "rbc":                      ["CAPITAL"],
    "risk based capital":       ["CAPITAL"],
    "economic capital":         ["CAPITAL"],
    "capital adequacy":         ["CAPITAL"],
    "c3 phase":                 ["CAPITAL"],

    # Mortality / Experience
    "mortality":                ["EXPERIENCE"],
    "experience study":         ["EXPERIENCE"],
    "lapse":                    ["EXPERIENCE"],
    "policyholder behavior":    ["EXPERIENCE"],
    "morbidity":                ["EXPERIENCE"],

    # Regulatory
    "naic":                     ["REGULATORY"],
    "actuarial guideline":      ["REGULATORY"],
    "model regulation":         ["REGULATORY"],
    "model law":                ["REGULATORY"],
}

# -----------------------------------------------------------------------------
# Relevance Scoring Keywords
# -----------------------------------------------------------------------------

ACTUARIAL_KEYWORDS = {

    "vm-20": 15, "vm20": 15,
    "vm-22": 15, "vm22": 15,
    "latf": 12, "life actuarial task force": 12,
    "principle based reserving": 12, "pbr": 12,
    "asset adequacy": 10, "cash flow testing": 10,
    "ldti": 12, "asc 944": 10,
    "reserve": 8, "reserving": 8, "valuation": 8,
    "rbc": 10, "risk based capital": 10,
    "mortality": 8, "experience study": 8, "lapse": 8,
    "reinsurance": 8, "coinsurance": 8, "funds withheld": 8,
    "annuity": 6, "fia": 6, "rila": 6, "iul": 6,
    "asset liability": 8, "alm": 8,
    "hedging": 6,
    "private credit": 7,
    "actuarial": 4, "actuary": 4,

    # Carrier names get relevance boost
    "kansas city life": 10,
    "ameritas": 10,
    "securian": 10,
    "country financial": 10,
    "business men's assurance": 10,
    "bmi": 6,
    "midland national": 10,
    "north american company": 10,
    "pacific life": 10,
    "equitable": 8,
    "brighthouse": 10,
    "cno financial": 10,
    "bankers life": 8,
    "global atlantic": 10,
    "protective life": 10,
    "lincoln financial": 8,
    "transamerica": 8,
    "sammons": 10,
    "mutual of omaha": 8,
    "aig life": 10,
}

# -----------------------------------------------------------------------------
# Impact Thresholds
# -----------------------------------------------------------------------------

HIGH_IMPACT_THRESHOLD   = 12
MEDIUM_IMPACT_THRESHOLD =  7

# -----------------------------------------------------------------------------
# Persistent Watch List (regulatory / topic tracking)
# -----------------------------------------------------------------------------

WATCH_LIST = [
    "VM-20", "VM-22", "Principle-Based Reserving", "LDTI",
    "Asset Adequacy Testing", "Cash Flow Testing",
    "RBC Modernization", "Life Reinsurance", "Bermuda Reinsurance",
    "FIA Sales", "RILA Sales", "Mortality Experience",
    "Policyholder Behavior", "Private Credit",
    "Asset Liability Management",
]
