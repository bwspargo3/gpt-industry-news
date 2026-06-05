# -----------------------------------------------------------------------------
# Google News Search Queries — high-signal targeted queries
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

    # Dynamic Discovery — M&A, trends, emerging topics
    ("Carrier Intelligence",    "life insurance acquisition merger 2026"),
    ("Carrier Intelligence",    "annuity company deal transaction 2026"),
    ("Reinsurance",             "reinsurance acquisition block transaction 2026"),
    ("Industry Trends",         "artificial intelligence life insurance actuarial"),
    ("Industry Trends",         "AI underwriting life insurance 2026"),
    ("Industry Trends",         "private equity life insurance annuity 2026"),
    ("Industry Trends",         "GLP-1 ozempic life insurance mortality"),
    ("Industry Trends",         "insurtech life annuity digital 2026"),
    ("Mortality & Experience",  "excess mortality life insurance claims 2026"),
    ("Annuity Market",          "annuity sales record LIMRA 2026"),
    ("Annuity Market",          "RIA fee based annuity market 2026"),

    # Publication proxy queries — catches trade press Google News doesn't surface via RSS
    ("SOA / AAA Research",      '"Society of Actuaries" research report 2026'),
    ("SOA / AAA Research",      '"American Academy of Actuaries" life insurance 2026'),
    ("Annuity Market",          '"LIMRA" annuity sales 2026'),
    ("Trade Press",             '"Best\'s Review" life insurance annuity'),
    ("Trade Press",             '"National Underwriter" life insurance annuity'),
    ("Trade Press",             '"Carrier Management" life insurance'),
    ("Trade Press",             '"Intelligent Insurer" life annuity reinsurance'),
    ("Regulatory",              '"Federal Register" IRS life insurance annuity'),
]

# -----------------------------------------------------------------------------
# Carrier Watchlist Queries
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
    ("Carrier Intelligence", "26North Re reinsurance"),
    ("Carrier Intelligence", "Independent Life insurance"),

    # Firm self-monitoring
    ("Carrier Intelligence", "Actuarial Resources Corporation ARC actuarial"),
    ("Carrier Intelligence", "Springline advisory actuarial consulting"),
]

# -----------------------------------------------------------------------------
# Direct RSS Feeds — primary and trade press sources
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

    # AM Best — ratings feed (not PR wire)
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

    # Trade press
    (
        "Trade Press",
        "Carrier Management",
        "https://www.carriermanagement.com/feed/"
    ),
    (
        "Reinsurance",
        "Reinsurance News",
        "https://www.reinsurancene.ws/feed/"
    ),
    (
        "Investments & ALM",
        "Insurance Asset Management",
        "https://insuranceassetmanagement.net/feed/"
    ),

    # Insurance Journal — life/annuity filtered by scoring
    (
        "Life Product Developments",
        "Insurance Journal",
        "https://www.insurancejournal.com/feed/"
    ),

    # Federal Register — IRS life insurance guidance only
    (
        "Regulatory",
        "Federal Register (IRS Life)",
        "https://www.federalregister.gov/api/v1/articles.rss"
        "?agencies[]=internal-revenue-service"
        "&topics[]=life-insurance"
    ),

    # Consulting firm research
    (
        "Consulting & Research",
        "Milliman Insights",
        "https://www.milliman.com/en/insight/rss"
    ),
]

# -----------------------------------------------------------------------------
# HTML Scrape Targets — fallback for sources without working RSS
# (category, source_name, url)
# -----------------------------------------------------------------------------

HTML_SCRAPE_TARGETS = [
    (
        "SOA / AAA Research",
        "SOA Research",
        "https://www.soa.org/resources/research-reports/"
    ),
    (
        "Annuity Market",
        "LIMRA Newsroom",
        "https://www.limra.com/en/newsroom/"
    ),
]
