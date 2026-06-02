# -----------------------------------------------------------------------------
# Google News Search Queries — trimmed to high-signal only
# (category, query)
# -----------------------------------------------------------------------------

SEARCH_QUERIES = [

    # Reserving / Valuation
    ("Valuation & Reserving", "VM-20 life insurance reserve"),
    ("Valuation & Reserving", "VM-22 annuity reserve"),
    ("Valuation & Reserving", "principle based reserving NAIC"),
    ("Valuation & Reserving", "asset adequacy testing life insurance"),
    ("Valuation & Reserving", "AG 38 life insurance"),

    # Regulatory
    ("Regulatory", "NAIC Life Actuarial Task Force LATF"),
    ("Regulatory", "NAIC life insurance actuarial guideline"),
    ("Regulatory", "NAIC model regulation life insurance"),

    # Accounting
    ("Accounting & LDTI", "LDTI long duration insurance"),
    ("Accounting & LDTI", "ASC 944 insurance accounting FASB"),

    # Experience Studies
    ("Mortality & Experience", "SOA mortality experience study"),
    ("Mortality & Experience", "life insurance lapse policyholder behavior"),

    # Reinsurance
    ("Reinsurance", "life reinsurance transaction bermuda"),
    ("Reinsurance", "asset intensive reinsurance funds withheld"),
    ("Reinsurance", "YRT coinsurance life reinsurance"),

    # Capital
    ("Capital & Risk", "life insurance RBC risk based capital"),
    ("Capital & Risk", "economic capital life insurer solvency"),

    # Annuities
    ("Annuity Market", "fixed indexed annuity FIA sales LIMRA"),
    ("Annuity Market", "RILA registered index linked annuity"),
    ("Annuity Market", "annuity hedging interest rate"),

    # Product
    ("Life Product Developments", "indexed universal life insurance IUL"),
    ("Life Product Developments", "term life insurance pricing"),

    # Investments / ALM
    ("Investments & ALM", "private credit life insurance portfolio"),
    ("Investments & ALM", "asset liability management annuity insurer"),
    ("Investments & ALM", "interest rate life insurance reserve impact"),

    # Rating Agencies
    ("Rating Agency Actions", "AM Best life insurer rating action"),
    ("Rating Agency Actions", "Moodys Fitch life insurance outlook"),
]

# -----------------------------------------------------------------------------
# Carrier Watchlist Queries
# Kansas City insurers + major national carriers
# -----------------------------------------------------------------------------

CARRIER_WATCHLIST = [

    # Kansas City / Midwest
    "Kansas City Life Insurance",
    "Protective Life",          # Birmingham but major regional presence
    "Ameritas Life",
    "Securian Financial",
    "Country Financial",
    "Business Men's Assurance BMI",
    "Midland National Life",
    "North American Company Life",

    # Large Nationals
    "Pacific Life Insurance",
    "Equitable Life insurance",
    "AIG life insurance annuity",
    "Brighthouse Financial",
    "CNO Financial Bankers Life",
    "Global Atlantic reinsurance",
    "Lincoln Financial Group",
    "Transamerica life insurance",
    "Sammons Financial",
    "Mutual of Omaha life",
]

CARRIER_SEARCH_QUERIES = [
    ("Carrier Intelligence", carrier)
    for carrier in CARRIER_WATCHLIST
]

# -----------------------------------------------------------------------------
# Direct RSS Feeds — primary sources, no Google News intermediary
# (category, source_name, url)
# -----------------------------------------------------------------------------

DIRECT_RSS_FEEDS = [

    # SOA
    (
        "SOA / AAA Research",
        "SOA News",
        "https://www.soa.org/rss/news/"
    ),
    (
        "SOA / AAA Research",
        "SOA Research",
        "https://www.soa.org/rss/research/"
    ),

    # American Academy of Actuaries
    (
        "SOA / AAA Research",
        "American Academy of Actuaries",
        "https://www.actuary.org/feed"
    ),

    # NAIC
    (
        "Regulatory",
        "NAIC Newsroom",
        "https://content.naic.org/rss.xml"
    ),

    # LIMRA
    (
        "Annuity Market",
        "LIMRA",
        "https://www.limra.com/rss/"
    ),

    # ThinkAdvisor
    (
        "Annuity Market",
        "ThinkAdvisor",
        "https://www.thinkadvisor.com/feed/"
    ),

    # Life Annuity Specialist
    (
        "Annuity Market",
        "Life Annuity Specialist",
        "https://lifeannuityspecialist.com/feed/"
    ),

    # Insurance News Net
    (
        "Life Product Developments",
        "Insurance News Net",
        "https://insurancenewsnet.com/rss"
    ),

    # AM Best
    (
        "Rating Agency Actions",
        "AM Best",
        "https://www.prnewswire.com/rss/news-releases-list.rss?company=am-best"
    ),

    # Insurance Journal (life/annuity filter applied in scoring)
    (
        "Life Product Developments",
        "Insurance Journal",
        "https://www.insurancejournal.com/feed/"
    ),
]
