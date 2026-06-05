# -----------------------------------------------------------------------------
# Google News Search Queries
# Primary discovery mechanism — also serves as fallback for dead RSS feeds.
# Google News reliably surfaces content from specific publications even when
# their direct RSS feeds are dead or blocked.
# (category, query)
# -----------------------------------------------------------------------------

SEARCH_QUERIES = [
    # Core actuarial — valuation and reserving
    ("Valuation & Reserving", "VM-20 life insurance reserve"),
    ("Valuation & Reserving", "VM-22 annuity reserve"),
    ("Valuation & Reserving", "principle based reserving NAIC"),
    ("Valuation & Reserving", "asset adequacy testing life insurance"),
    ("Valuation & Reserving", "AG 38 life insurance actuarial guideline"),

    # Regulatory
    ("Regulatory", "NAIC Life Actuarial Task Force LATF"),
    ("Regulatory", "NAIC life insurance actuarial guideline adopted"),
    ("Regulatory", "NAIC model regulation life insurance"),
    ("Regulatory", "state insurance department life annuity bulletin"),

    # Accounting
    ("Accounting & LDTI", "LDTI long duration targeted improvements insurance"),
    ("Accounting & LDTI", "ASC 944 insurance accounting FASB"),

    # Experience Studies
    ("Mortality & Experience", "SOA mortality experience study life insurance"),
    ("Mortality & Experience", "life insurance lapse policyholder behavior study"),
    ("Mortality & Experience", "GLP-1 ozempic life insurance mortality impact"),
    ("Mortality & Experience", "excess mortality life insurance claims 2026"),

    # Reinsurance
    ("Reinsurance", "life reinsurance transaction bermuda 2026"),
    ("Reinsurance", "asset intensive reinsurance funds withheld modco"),
    ("Reinsurance", "YRT coinsurance life reinsurance pricing"),
    ("Reinsurance", "life insurance block acquisition reinsurance 2026"),

    # Capital
    ("Capital & Risk", "life insurance RBC risk based capital NAIC"),
    ("Capital & Risk", "AM Best life insurer rating action downgrade 2026"),
    ("Capital & Risk", "Moodys Fitch life insurance outlook 2026"),

    # Annuities
    ("Annuity Market", "fixed indexed annuity FIA sales LIMRA 2026"),
    ("Annuity Market", "RILA registered index linked annuity sales 2026"),
    ("Annuity Market", "MYGA multi year guaranteed annuity 2026"),
    ("Annuity Market", "annuity hedging interest rate FIA carrier"),

    # Product
    ("Life Product Developments", "indexed universal life insurance IUL pricing"),
    ("Life Product Developments", "term life insurance pricing filing 2026"),
    ("Life Product Developments", "AG 49 IUL illustration actuarial guideline"),

    # Investments / ALM
    ("Investments & ALM", "private credit life insurance portfolio allocation"),
    ("Investments & ALM", "asset liability management annuity insurer duration"),
    ("Investments & ALM", "structured credit insurance investment portfolio 2026"),

    # Publication-targeted queries
    # These reliably surface articles from specific outlets via Google News
    # even when direct RSS is dead
    ("SOA / AAA Research",
        "site:soa.org OR \"Society of Actuaries\" research report 2026"),
    ("SOA / AAA Research",
        "\"American Academy of Actuaries\" life insurance annuity 2026"),
    ("SOA / AAA Research",
        "\"The Actuary\" magazine life annuity valuation 2026"),
    ("Trade Press",
        "\"Best's Review\" life insurance annuity actuarial"),
    ("Trade Press",
        "\"National Underwriter\" life health insurance 2026"),
    ("Trade Press",
        "\"InsuranceNewsNet\" life annuity actuarial 2026"),
    ("Trade Press",
        "\"Carrier Management\" life insurance reinsurance 2026"),
    ("Trade Press",
        "\"Reinsurance News\" life annuity bermuda 2026"),
    ("Annuity Market",
        "\"ThinkAdvisor\" annuity life insurance 2026"),
    ("Annuity Market",
        "\"LIMRA\" annuity sales research 2026"),
    ("Consulting & Research",
        "\"Milliman\" life insurance actuarial research 2026"),
    ("Consulting & Research",
        "\"Oliver Wyman\" life insurance annuity report 2026"),
    ("Consulting & Research",
        "\"Deloitte\" life insurance LDTI regulatory 2026"),
    ("Consulting & Research",
        "\"EY\" OR \"Ernst Young\" life insurance actuarial 2026"),
    ("Consulting & Research",
        "\"PwC\" life insurance capital reserving 2026"),
    ("Consulting & Research",
        "\"KPMG\" life insurance regulatory update 2026"),
    ("Consulting & Research",
        "\"WTW\" OR \"Willis Towers Watson\" life insurance 2026"),

    # Dynamic discovery — M&A, trends, emerging topics
    ("Carrier Intelligence",  "life insurance company acquisition merger 2026"),
    ("Carrier Intelligence",  "life annuity carrier strategic investment 2026"),
    ("Reinsurance",           "reinsurance block transaction life annuity 2026"),
    ("Industry Trends",       "artificial intelligence actuarial life insurance 2026"),
    ("Industry Trends",       "AI underwriting life insurance pricing 2026"),
    ("Industry Trends",       "private equity life insurance acquisition 2026"),
    ("Industry Trends",       "insurtech life annuity digital distribution 2026"),
    ("Annuity Market",        "annuity sales record 2026"),
    ("Annuity Market",        "RIA fee based annuity fiduciary 2026"),
    ("Regulatory",            "\"Federal Register\" IRS life insurance annuity 2026"),
]

# -----------------------------------------------------------------------------
# Carrier Watchlist Queries
# Specific enough to reduce false positives
# (category, query)
# -----------------------------------------------------------------------------

CARRIER_SEARCH_QUERIES = [
    # Kansas City / Midwest
    ("Carrier Intelligence", "Kansas City Life Insurance company 2026"),
    ("Carrier Intelligence", "Ameritas Life insurance annuity 2026"),
    ("Carrier Intelligence", "Securian Financial life insurance 2026"),
    ("Carrier Intelligence", "Country Financial life insurance annuity 2026"),
    ("Carrier Intelligence", "Business Men's Assurance BMI life insurance"),
    ("Carrier Intelligence", "Midland National Life Insurance annuity 2026"),
    ("Carrier Intelligence", "North American Company Life Annuity Sammons"),

    # Large nationals
    ("Carrier Intelligence", "Pacific Life Insurance annuity 2026"),
    ("Carrier Intelligence", "Equitable Holdings life insurance annuity 2026"),
    ("Carrier Intelligence", "AIG life insurance annuity 2026"),
    ("Carrier Intelligence", "Brighthouse Financial annuity life 2026"),
    ("Carrier Intelligence", "CNO Financial Bankers Life insurance 2026"),
    ("Carrier Intelligence", "Global Atlantic life reinsurance 2026"),
    ("Carrier Intelligence", "Protective Life Insurance annuity 2026"),
    ("Carrier Intelligence", "Lincoln Financial life annuity 2026"),
    ("Carrier Intelligence", "Transamerica life insurance annuity 2026"),
    ("Carrier Intelligence", "Mutual of Omaha life insurance 2026"),
    ("Carrier Intelligence", "26North Re reinsurance life"),
    ("Carrier Intelligence", "Independent Life insurance acquisition"),

    # Firm monitoring
    ("Carrier Intelligence", "Actuarial Resources Corporation ARC actuarial"),
    ("Carrier Intelligence", "Springline advisory actuarial consulting"),
]

# -----------------------------------------------------------------------------
# Direct RSS Feeds — VERIFIED WORKING as of June 2026
# Only feeds confirmed to return valid content are listed here.
# Dead feeds have been removed — Google News queries above cover those sources.
# (category, source_name, url)
# -----------------------------------------------------------------------------

DIRECT_RSS_FEEDS = [
    # The Actuary Magazine (SOA publication) — confirmed working
    (
        "SOA / AAA Research",
        "The Actuary Magazine",
        "https://theactuarymagazine.org/feed/"
    ),

    # Insurance Journal — broad but filtered by scoring
    (
        "Trade Press",
        "Insurance Journal",
        "https://www.insurancejournal.com/feed/"
    ),

    # Carrier Management
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

    # Life Annuity Specialist — was returning malformed XML; try with error tolerance
    (
        "Annuity Market",
        "Life Annuity Specialist",
        "https://lifeannuityspecialist.com/feed/"
    ),

    # Federal Register — IRS life insurance only (narrow topic filter)
    (
        "Regulatory",
        "Federal Register (IRS Life)",
        "https://www.federalregister.gov/api/v1/articles.rss"
        "?agencies[]=internal-revenue-service"
        "&topics[]=life-insurance"
    ),
]

# -----------------------------------------------------------------------------
# Targeted HTML Scrapers
# Each scraper is purpose-built for its source's actual page structure.
# More reliable than RSS for sources that have killed their feeds.
# (category, source_name, url, scraper_id)
# scraper_id maps to a specific extraction function in intelligence.py
# -----------------------------------------------------------------------------

HTML_SCRAPE_TARGETS = [
    (
        "SOA / AAA Research",
        "SOA Research Institute",
        "https://www.soa.org/research/research-topic/life-annuities/",
        "soa_research"
    ),
    (
        "SOA / AAA Research",
        "SOA News",
        "https://www.soa.org/news/",
        "soa_news"
    ),
    (
        "Regulatory",
        "NAIC Newsroom",
        "https://content.naic.org/newsroom",
        "naic_newsroom"
    ),
    (
        "Annuity Market",
        "LIMRA Newsroom",
        "https://www.limra.com/en/newsroom/",
        "limra_newsroom"
    ),
    (
        "Annuity Market",
        "ThinkAdvisor Life & Health",
        "https://www.thinkadvisor.com/life-health/",
        "thinkadvisor"
    ),
    (
        "Trade Press",
        "InsuranceNewsNet",
        "https://insurancenewsnet.com/oarticle/life-annuity",
        "insurancenewsnet"
    ),
    (
        "Consulting & Research",
        "Milliman Insights",
        "https://www.milliman.com/en/insight?practice=life-financial-reporting",
        "milliman"
    ),
]
