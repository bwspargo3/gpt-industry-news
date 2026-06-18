# ------------------------------------------------------------------
# NewsAPI Boolean Queries
# ------------------------------------------------------------------

NEWSAPI_QUERIES = [
    ("Valuation & Reserving", '("life insurance" OR annuity) AND ("VM-20" OR "VM-22" OR PBR OR "principle based reserving")'),
    ("Regulatory", '("life insurance" OR annuity) AND (NAIC OR LATF OR "Department of Labor" OR "fiduciary rule")'),
    ("Accounting & LDTI", '("life insurance" OR annuity) AND ("LDTI" OR "ASC 944" OR FASB)'),
    ("Mortality & Experience", '("life insurance" OR annuity) AND (mortality OR "experience study" OR longevity)'),
    ("Reinsurance", '"life reinsurance" OR "asset intensive reinsurance" OR "funded reinsurance" OR "block reinsurance"'),
    ("Capital & Risk", '("life insurance" OR annuity) AND ("risk based capital" OR RBC OR "rating agency")'),
    ("Annuity Market", '"fixed indexed annuity" OR RILA OR MYGA OR "annuity sales" OR "personal income annuity"'),
    ("Life Product Developments", '"indexed universal life" OR "IUL pricing" OR "AG 49"'),
    ("Investments & ALM", '("life insurance" OR annuity) AND ("private credit" OR "asset liability management")'),
    ("Industry Trends", '("life insurance" OR annuity) AND ("artificial intelligence" OR insurtech OR "private equity")'),
    ("Consulting & Research", '("life insurance" OR annuity) AND (Milliman OR "Oliver Wyman" OR Deloitte OR PwC OR EY)'),
    # Extra carrier earnings queries — Q results generate significant actuarial insight
    ("Carrier Intelligence", '("life insurance" OR annuity) AND (earnings OR "quarterly results" OR "net income")'),
    ("Carrier Intelligence", '(MetLife OR Prudential OR "Lincoln Financial" OR Corebridge OR "Equitable Holdings") AND (earnings OR results OR annuity)'),
]

# ------------------------------------------------------------------
# Direct RSS Feeds — confirmed working as of June 2026
# ------------------------------------------------------------------

DIRECT_RSS_FEEDS = [
    # Core life/annuity trade press
    ("Trade Press",           "Carrier Management",          "https://www.carriermanagement.com/feed/"),
    ("Annuity Market",        "Life Annuity Specialist",     "https://lifeannuityspecialist.com/feed/"),

    # Reinsurance — consistently producing life/annuity content
    ("Reinsurance",           "Reinsurance News",            "https://www.reinsurancene.ws/feed/"),

    # Rating agencies
    ("Rating Agency Actions", "AM Best News",                "https://www.ambest.com/rss/latestnews.rss"),

    # Regulatory
    ("Regulatory",            "Federal Register (IRS Life)",
     "https://www.federalregister.gov/api/v1/articles.rss?agencies[]=internal-revenue-service&topics[]=life-insurance"),
    ("Regulatory",            "Federal Register (Treasury)",
     "https://www.federalregister.gov/api/v1/articles.rss?agencies[]=department-of-the-treasury&topics[]=life-insurance"),

    # Broad insurance trade
    ("Trade Press",           "Insurance Journal",           "https://www.insurancejournal.com/feed/"),
]

# ------------------------------------------------------------------
# High-Value Firm Search Queries
# ------------------------------------------------------------------

FIRM_SEARCH_QUERIES = [
    ("Valuation & Reserving", "Moody's AXIS insurance"),
    ("Valuation & Reserving", "Milliman life insurance report"),
    ("Valuation & Reserving", "Oliver Wyman life insurance"),
    ("Reinsurance",           "Mayer Brown life reinsurance"),
    ("Reinsurance",           "Skadden life reinsurance"),
    ("Accounting & LDTI",     "PwC LDTI insurance"),
    ("Accounting & LDTI",     "EY LDTI insurance"),
    ("Accounting & LDTI",     "Deloitte LDTI insurance"),
    ("Mortality & Experience", "Munich Re mortality"),
    ("Mortality & Experience", "SCOR life mortality"),
]

# ------------------------------------------------------------------
# Google News RSS Queries — industry topics
#
# PRODUCTION LESSONS:
# 1. No year suffix — Google News RSS ranks by recency automatically
# 2. Short queries (3-5 words) outperform long boolean strings
# 3. Quoted phrases for exact matches; single words for broad coverage
# 4. Google News RSS ignores OR/AND — use phrase matching only
# ------------------------------------------------------------------

SEARCH_QUERIES = [
    # Valuation & Reserving / Accounting
    ("Valuation & Reserving",     "VM-20 OR VM-22 OR PBR life insurance reserve"),
    ("Valuation & Reserving",     "LDTI OR FASB life insurance accounting"),
    ("Valuation & Reserving",     "NAIC GOES economic scenarios"),

    # Regulatory
    ("Regulatory",                "NAIC Life Actuarial Task Force OR LATF"),
    ("Regulatory",                "DOL fiduciary rule OR annuity suitability"),

    # Mortality & Experience
    ("Mortality & Experience",    "SOA mortality OR experience study"),
    ("Mortality & Experience",    "GLP-1 OR longevity life insurance"),
    ("Mortality & Experience",    "excess mortality life insurance"),

    # Reinsurance — life-specific
    ("Reinsurance",               "asset intensive OR funded reinsurance"),
    ("Reinsurance",               "life block reinsurance OR pension risk transfer"),

    # Capital & Risk
    ("Capital & Risk",            "life insurance RBC OR capital NAIC"),
    ("Capital & Risk",            "AM Best OR Fitch OR Moody's life insurer"),
    ("Capital & Risk",            "life insurance solvency capital ratio"),

    # Annuity Market — high volume, core section
    ("Annuity Market",            "FIA OR RILA OR MYGA annuity sales"),
    ("Annuity Market",            "LIMRA OR Wink OR Conning annuity"),

    # Life Products
    ("Life Product Developments", "indexed universal life OR IUL"),
    ("Life Product Developments", "IUL AG 49 actuarial guideline"),
    ("Life Product Developments", "term life OR whole life insurance"),

    # ALM & Investments
    ("Investments & ALM",         "private credit life insurer portfolio"),
    ("Investments & ALM",         "insurer asset liability management ALM"),

    # Industry Trends
    ("Industry Trends",           "life insurance artificial intelligence AI"),
    ("Industry Trends",           "private equity OR PE life insurance"),
    ("Industry Trends",           "insurtech life annuity technology"),

    # Research
    ("SOA / AAA Research",        "Society of Actuaries OR AAA research"),
]

# ------------------------------------------------------------------
# Carrier Newsroom Queries
#
# CRITICAL: Single carrier name queries outperform compound queries
# on Google News RSS. The gate in intelligence.py enforces life/annuity
# relevance, so broad queries are safe here.
# ------------------------------------------------------------------

CARRIER_SEARCH_QUERIES = [
    # Giants
    ("Carrier Intelligence", "MetLife OR Prudential OR MassMutual"),
    ("Carrier Intelligence", "New York Life OR Northwestern Mutual"),

    # Publics
    ("Carrier Intelligence", "Lincoln Financial OR Corebridge OR Equitable"),
    ("Carrier Intelligence", "Brighthouse OR Principal Financial OR AIG"),

    # PE / Annuity Specialists
    ("Carrier Intelligence", "Athene OR Global Atlantic OR Jackson"),
    ("Carrier Intelligence", "F&G OR Gainbridge OR Allianz Life"),
    ("Carrier Intelligence", "Fortitude Re OR Resolution Life OR Somerset Re"),

    # Active Mid-size
    ("Carrier Intelligence", "Pacific Life OR Transamerica OR Nationwide"),
    ("Carrier Intelligence", "Ameritas OR Protective Life OR Sammons"),
]
