# ------------------------------------------------------------------
# Google News Search Queries
# These are the most reliable source of content variation.
# Google News surfaces content from publications even when their
# direct RSS feeds are dead or blocked.
# (category, query)
# ------------------------------------------------------------------

SEARCH_QUERIES = [
    # Valuation & Reserving
    ("Valuation & Reserving", "VM-20 life insurance reserve 2026"),
    ("Valuation & Reserving", "VM-22 annuity reserve NAIC 2026"),
    ("Valuation & Reserving", "principle based reserving life insurance"),
    ("Valuation & Reserving", "asset adequacy testing life insurance actuary"),
    ("Valuation & Reserving", "AG 38 actuarial guideline life insurance"),
    ("Valuation & Reserving", "cash flow testing life insurance reserves"),

    # Regulatory
    ("Regulatory", "NAIC Life Actuarial Task Force LATF 2026"),
    ("Regulatory", "NAIC actuarial guideline life insurance adopted"),
    ("Regulatory", "NAIC model regulation life annuity"),
    ("Regulatory", "state insurance department life annuity bulletin 2026"),
    ("Regulatory", "DOL fiduciary rule annuity insurance 2026"),

    # Accounting
    ("Accounting & LDTI", "LDTI long duration targeted improvements 2026"),
    ("Accounting & LDTI", "ASC 944 FASB insurance accounting 2026"),
    ("Accounting & LDTI", "LDTI implementation life insurance 2026"),

    # Experience Studies
    ("Mortality & Experience", "SOA mortality study life insurance 2026"),
    ("Mortality & Experience", "life insurance lapse rate policyholder study"),
    ("Mortality & Experience", "GLP-1 ozempic semaglutide life insurance mortality"),
    ("Mortality & Experience", "excess mortality life insurance claims 2026"),
    ("Mortality & Experience", "longevity risk life annuity 2026"),

    # Reinsurance
    ("Reinsurance", "life reinsurance transaction 2026"),
    ("Reinsurance", "asset intensive reinsurance bermuda life annuity"),
    ("Reinsurance", "funds withheld modco YRT life reinsurance"),
    ("Reinsurance", "life insurance block acquisition reinsurance deal"),

    # Capital
    ("Capital & Risk", "life insurance RBC risk based capital NAIC 2026"),
    ("Capital & Risk", "AM Best life insurer rating action upgrade downgrade 2026"),
    ("Capital & Risk", "Moodys Fitch SP life insurance financial strength 2026"),

    # Annuities
    ("Annuity Market", "fixed indexed annuity FIA sales record 2026"),
    ("Annuity Market", "RILA registered index linked annuity 2026"),
    ("Annuity Market", "MYGA multi year guaranteed annuity rates 2026"),
    ("Annuity Market", "annuity sales LIMRA first quarter 2026"),
    ("Annuity Market", "FIA hedging cost interest rate annuity carrier"),

    # Life Products
    ("Life Product Developments", "indexed universal life IUL pricing 2026"),
    ("Life Product Developments", "term life insurance pricing trends 2026"),
    ("Life Product Developments", "AG 49 IUL illustration actuarial guideline"),
    ("Life Product Developments", "whole life insurance dividend 2026"),

    # Investments & ALM
    ("Investments & ALM", "private credit life insurance portfolio 2026"),
    ("Investments & ALM", "asset liability management life annuity insurer"),
    ("Investments & ALM", "structured credit insurance investment 2026"),
    ("Investments & ALM", "life insurer investment portfolio yield 2026"),

    # Industry Trends
    ("Industry Trends", "artificial intelligence actuarial life insurance 2026"),
    ("Industry Trends", "AI underwriting life insurance 2026"),
    ("Industry Trends", "private equity life insurance acquisition 2026"),
    ("Industry Trends", "insurtech life annuity digital 2026"),
    ("Industry Trends", "life insurance distribution RIA bank channel 2026"),

    # Publication-targeted queries — surfaces content from specific outlets
    # even when their direct RSS is dead
    ("SOA / AAA Research",
        "\"Society of Actuaries\" research report life annuity 2026"),
    ("SOA / AAA Research",
        "\"American Academy of Actuaries\" life insurance annuity 2026"),
    ("SOA / AAA Research",
        "\"The Actuary\" magazine SOA life annuity valuation"),
    ("Trade Press",
        "\"Best's Review\" life insurance annuity actuarial 2026"),
    ("Trade Press",
        "\"National Underwriter\" life health insurance 2026"),
    ("Trade Press",
        "\"InsuranceNewsNet\" life annuity 2026"),
    ("Trade Press",
        "\"Carrier Management\" life insurance reinsurance"),
    ("Trade Press",
        "\"Reinsurance News\" life annuity bermuda 2026"),
    ("Trade Press",
        "\"Insurance Journal\" life annuity actuarial 2026"),
    ("Annuity Market",
        "\"ThinkAdvisor\" annuity life insurance 2026"),
    ("Annuity Market",
        "\"LIMRA\" annuity life insurance research 2026"),
    ("Consulting & Research",
        "\"Milliman\" life insurance actuarial 2026"),
    ("Consulting & Research",
        "\"Oliver Wyman\" life insurance annuity 2026"),
    ("Consulting & Research",
        "\"Deloitte\" life insurance LDTI 2026"),
    ("Consulting & Research",
        "\"EY\" OR \"Ernst Young\" life insurance actuarial 2026"),
    ("Consulting & Research",
        "\"PwC\" life insurance reserving capital 2026"),
    ("Consulting & Research",
        "\"KPMG\" life insurance regulatory 2026"),
    ("Consulting & Research",
        "\"WTW\" OR \"Willis Towers Watson\" life insurance 2026"),
    ("Regulatory",
        "\"Federal Register\" IRS life insurance annuity qualified"),
]

# ------------------------------------------------------------------
# Carrier Watchlist Queries
# ------------------------------------------------------------------

CARRIER_SEARCH_QUERIES = [
    # Kansas City / Midwest
    ("Carrier Intelligence", "\"Kansas City Life\" insurance"),
    ("Carrier Intelligence", "\"Ameritas Life\" insurance annuity"),
    ("Carrier Intelligence", "\"Securian Financial\" life insurance"),
    ("Carrier Intelligence", "\"Country Financial\" life insurance annuity"),
    ("Carrier Intelligence", "\"Business Men's Assurance\" BMI life"),
    ("Carrier Intelligence", "\"Midland National\" life insurance annuity"),
    ("Carrier Intelligence", "\"North American Company\" life annuity Sammons"),

    # Large nationals
    ("Carrier Intelligence", "\"Pacific Life\" insurance annuity"),
    ("Carrier Intelligence", "\"Equitable Holdings\" life insurance annuity"),
    ("Carrier Intelligence", "\"AIG\" life insurance annuity 2026"),
    ("Carrier Intelligence", "\"Brighthouse Financial\" annuity life"),
    ("Carrier Intelligence", "\"CNO Financial\" OR \"Bankers Life\" insurance"),
    ("Carrier Intelligence", "\"Global Atlantic\" life reinsurance"),
    ("Carrier Intelligence", "\"Protective Life\" insurance annuity"),
    ("Carrier Intelligence", "\"Lincoln Financial\" life annuity 2026"),
    ("Carrier Intelligence", "\"Transamerica\" life insurance annuity 2026"),
    ("Carrier Intelligence", "\"Mutual of Omaha\" life insurance 2026"),
    ("Carrier Intelligence", "\"26North\" reinsurance life"),
    ("Carrier Intelligence", "\"Independent Life\" insurance acquisition"),
    ("Carrier Intelligence", "\"Sammons Financial\" life insurance"),
    ("Carrier Intelligence", "\"Nassau Financial\" life insurance"),
    ("Carrier Intelligence", "\"Athene\" annuity reinsurance 2026"),
    ("Carrier Intelligence", "\"F&G\" Fidelity Guaranty life annuity"),
    ("Carrier Intelligence", "\"Jackson National\" life annuity"),
    ("Carrier Intelligence", "\"Nationwide\" life insurance annuity 2026"),
    ("Carrier Intelligence", "\"Principal Financial\" life insurance 2026"),
]

# ------------------------------------------------------------------
# Direct RSS Feeds — verified working or likely working
# (category, source_name, url)
# ------------------------------------------------------------------

DIRECT_RSS_FEEDS = [
    # Insurance Journal — broad but filtered by scoring
    (
        "Trade Press",
        "Insurance Journal",
        "https://www.insurancejournal.com/feed/",
    ),
    # Carrier Management
    (
        "Trade Press",
        "Carrier Management",
        "https://www.carriermanagement.com/feed/",
    ),
    # Reinsurance News
    (
        "Reinsurance",
        "Reinsurance News",
        "https://www.reinsurancene.ws/feed/",
    ),
    # Life Annuity Specialist — malformed XML handled by fallback parser
    (
        "Annuity Market",
        "Life Annuity Specialist",
        "https://lifeannuityspecialist.com/feed/",
    ),
    # Federal Register — IRS life insurance only
    (
        "Regulatory",
        "Federal Register (IRS Life)",
        "https://www.federalregister.gov/api/v1/articles.rss"
        "?agencies[]=internal-revenue-service"
        "&topics[]=life-insurance",
    ),
    # Advisor Perspectives — has working RSS, covers annuity/retirement
    (
        "Annuity Market",
        "Advisor Perspectives",
        "https://www.advisorperspectives.com/rss",
    ),
    # Investment News — covers annuity/retirement distribution
    (
        "Annuity Market",
        "InvestmentNews",
        "https://www.investmentnews.com/rss",
    ),
    # Pensions & Investments — insurance investment coverage
    (
        "Investments & ALM",
        "Pensions & Investments",
        "https://www.pionline.com/rss/all",
    ),
]

# ------------------------------------------------------------------
# HTML Scrape Targets
# (category, source_name, url, scraper_id)
# ------------------------------------------------------------------

HTML_SCRAPE_TARGETS = [
    # SOA — correct current URL for life research
    (
        "SOA / AAA Research",
        "SOA Research Institute",
        "https://www.soa.org/research/topics/life-ann-res-topic-list/",
        "soa_research",
    ),
    # SOA news — correct current URL
    (
        "SOA / AAA Research",
        "SOA News",
        "https://www.soa.org/news-and-publications/news/",
        "soa_news",
    ),
    # NAIC newsroom — working
    (
        "Regulatory",
        "NAIC Newsroom",
        "https://content.naic.org/newsroom",
        "naic_newsroom",
    ),
    # LIMRA — working
    (
        "Annuity Market",
        "LIMRA Newsroom",
        "https://www.limra.com/en/newsroom/",
        "limra_newsroom",
    ),
    # ThinkAdvisor — scrape main page instead of subsection
    (
        "Trade Press",
        "ThinkAdvisor",
        "https://www.thinkadvisor.com/",
        "thinkadvisor",
    ),
    # Milliman — correct URL
    (
        "Consulting & Research",
        "Milliman Insights",
        "https://www.milliman.com/en/insight",
        "milliman",
    ),
    # InsuranceNewsNet — scrape main page
    (
        "Trade Press",
        "InsuranceNewsNet",
        "https://insurancenewsnet.com/",
        "insurancenewsnet",
    ),
    # AAA — American Academy of Actuaries
    (
        "SOA / AAA Research",
        "American Academy of Actuaries",
        "https://www.actuary.org/content/publications-0",
        "aaa_publications",
    ),
    # AM Best — news page (not PR wire)
    (
        "Rating Agency Actions",
        "AM Best News",
        "https://www.ambest.com/news/",
        "ambest_news",
    ),
]
