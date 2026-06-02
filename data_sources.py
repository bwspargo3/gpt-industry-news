# -----------------------------------------------------------------------------
# Google News Search Queries — high-signal industry queries
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
    ("Rating Agency Actions", "Moodys Fitch life insurance outlook downgrade"),
]

# -----------------------------------------------------------------------------
# Carrier Watchlist — specific enough to avoid false positives
# (category, query)
# -----------------------------------------------------------------------------

CARRIER_SEARCH_QUERIES = [

    # Kansas City / Midwest
    ("Carrier Intelligence", "Kansas City Life Insurance company"),
    ("Carrier Intelligence", "Ameritas Life Partners insurance annuity"),
    ("Carrier Intelligence", "Securian Financial life insurance annuity"),
    ("Carrier Intelligence", "Country Financial life insurance annuity"),
    ("Carrier Intelligence", "Business Men's Assurance life insurance"),
    ("Carrier Intelligence", "Midland National Life Insurance annuity"),
    ("Carrier Intelligence", "North American Company Life Annuity Sammons"),

    # Large Nationals
    ("Carrier Intelligence", "Pacific Life Insurance annuity"),
    ("Carrier Intelligence", "Equitable Holdings life insurance annuity"),
    ("Carrier Intelligence", "AIG life insurance annuity division"),
    ("Carrier Intelligence", "Brighthouse Financial annuity life"),
    ("Carrier Intelligence", "CNO Financial Bankers Life insurance"),
    ("Carrier Intelligence", "Global Atlantic life reinsurance"),
    ("Carrier Intelligence", "Protective Life Insurance annuity"),
    ("Carrier Intelligence", "Lincoln Financial life annuity"),
    ("Carrier Intelligence", "Transamerica life insurance annuity"),
    ("Carrier Intelligence", "Mutual of Omaha life insurance"),

    # Firm self-monitoring
    ("Carrier Intelligence", "Actuarial Resources Corporation ARC actuarial"),
    ("Carrier Intelligence", "Springline advisory actuarial consulting"),
]

# -----------------------------------------------------------------------------
# Direct RSS Feeds — primary sources only, no Google News intermediary
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

    # AM Best — actual ratings feed, not PR wire
    (
        "Rating Agency Actions",
        "AM Best Ratings",
        "https://www.ambest.com/rss/ratings.rss"
    ),
    (
        "Rating Agency Actions",
        "AM Best News",
        "https://www.ambest.com/rss/latestnews.rss"
    ),

    # Insurance Journal — life/annuity content filtered by scoring
    (
        "Life Product Developments",
        "Insurance Journal",
        "https://www.insurancejournal.com/feed/"
    ),

    # Federal Register — IRS and DOL guidance affecting life/annuity
    (
        "Regulatory",
        "Federal Register (IRS)",
        "https://www.federalregister.gov/api/v1/articles.rss"
        "?agencies[]=internal-revenue-service"
        "&topics[]=life-insurance"
    ),
    (
        "Regulatory",
        "Federal Register (DOL)",
        "https://www.federalregister.gov/api/v1/articles.rss"
        "?agencies[]=employee-benefits-security-administration"
    ),
]
