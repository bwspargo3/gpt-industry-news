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
    
    # -------------------------------------------------------------------------
    # Targeted Publication Proxy Feeds
    # Using Google News to bypass corporate firewalls and 404s
    # -------------------------------------------------------------------------
    ("SOA / AAA Research", '"Society of Actuaries" OR "American Academy of Actuaries" research report'),
    ("Annuity Market", '"LIMRA" annuity sales'),
    ("Annuity Market", '"ThinkAdvisor" annuity OR life insurance'),
    ("Life Product Developments", '"InsuranceNewsNet" life insurance OR annuity'),
    ("Life Product Developments", '"Life Annuity Specialist"'),
    ("Regulatory", '"Federal Register" IRS OR DOL life insurance annuity'),
]

# -----------------------------------------------------------------------------
# Carrier Watchlist
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

    # Corporate References
    ("Carrier Intelligence", "Actuarial Resources Corporation ARC actuarial"),
    ("Carrier Intelligence", "Springline advisory actuarial consulting"),
]

# -----------------------------------------------------------------------------
# Direct HTML Scrape Targets (Bypassing RSS entirely)
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
        "LIMRA", 
        "https://www.limra.com/en/newsroom/"
    ),
    (
        "Annuity Market", 
        "ThinkAdvisor", 
        "https://www.thinkadvisor.com/life-health/"
    ),
    (
        "Life Product Developments", 
        "InsuranceNewsNet", 
        "https://insurancenewsnet.com/topics/top-stories"
    ),
    (
        "Life Product Developments", 
        "Life Annuity Specialist", 
        "https://www.lifeannuityspecialist.com/"
    ),
]
