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

    # Consulting Firm Research
    ("Consulting & Research", "Milliman life insurance actuarial report"),
    ("Consulting & Research", "Oliver Wyman life insurance annuity report"),
    ("Consulting & Research", "Deloitte life insurance LDTI regulatory"),
    ("Consulting & Research", "EY life insurance actuarial report"),
    ("Consulting & Research", "PwC life insurance capital reserving"),
    ("Consulting & Research", "KPMG life insurance regulatory update"),
    ("Consulting & Research", "WTW Willis Towers Watson life insurance report"),
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
    # In DIRECT_RSS_FEEDS, REPLACE the two Federal Register entries with:

    # Federal Register — tighter topic filter applied in scoring
    (
        "Regulatory",
        "Federal Register (IRS Life)",
        "https://www.federalregister.gov/api/v1/articles.rss"
        "?agencies[]=internal-revenue-service"
        "&topics[]=life-insurance"
    ),
    # Note: removed the broad DOL EBSA feed — too noisy

    # Consulting Firm Research
    (
        "Consulting & Research",
        "Milliman Insights",
        "https://www.milliman.com/en/insight/rss"
    ),
    (
        "Consulting & Research",
        "Oliver Wyman Insurance",
        "https://www.oliverwyman.com/our-expertise/industries/"
        "financial-services/insurance.rss"
    ),
    (
        "Consulting & Research",
        "Deloitte Insurance",
        "https://www2.deloitte.com/us/en/pages/financial-services/"
        "topics/insurance.rss"
    ),
    (
        "Consulting & Research",
        "EY Insurance",
        "https://www.ey.com/en_us/industries/insurance.rss"
    ),
    (
        "Consulting & Research",
        "WTW Insurance Research",
        "https://www.wtwco.com/en-us/insights/rss?practice=insurance"
    ),
    (
        "Consulting & Research",
        "KPMG Insurance",
        "https://kpmg.com/us/en/articles/insurance.rss"
    ),
    # Add to DIRECT_RSS_FEEDS in data_sources.py

# Best's Review / AM Best editorial (different from their PR wire)
(
    "Trade Press",
    "Best's Review",
    "https://www.ambest.com/rss/bestreview.rss"
),

# National Underwriter Life & Health
(
    "Trade Press",
    "National Underwriter Life & Health",
    "https://www.lifehealthpro.com/feed"
),

# Insurance Forums / Carrier Management
(
    "Trade Press",
    "Carrier Management",
    "https://www.carriermanagement.com/feed/"
),

# Reinsurance News
(
    "Reinsurance",
    "Reinsurance News",
    "https://www.reinsurancene.ws/feed/"
),

# Intelligent Insurer (already surfacing in your results via Google News)
(
    "Trade Press",
    "Intelligent Insurer",
    "https://www.intelligentinsurer.com/rss"
),

# The Actuary Magazine (SOA publication)
(
    "SOA / AAA Research",
    "The Actuary Magazine",
    "https://www.theactuary.com/rss"
),

# Insurance Asset Management
(
    "Investments & ALM",
    "Insurance Asset Management",
    "https://insuranceassetmanagement.net/feed/"
),

# Global Reinsurance
(
    "Reinsurance",
    "Global Reinsurance",
    "https://www.globalreinsurance.com/rss"
),

# Pensions & Investments — insurance/annuity coverage
(
    "Investments & ALM",
    "Pensions & Investments",
    "https://www.pionline.com/rss/all"
),
]
