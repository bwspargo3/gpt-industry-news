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
# Google News RSS Queries — industry topics
#
# PRODUCTION LESSONS:
# 1. No year suffix — Google News RSS ranks by recency automatically
# 2. Short queries (3-5 words) outperform long boolean strings
# 3. Quoted phrases for exact matches; single words for broad coverage
# 4. Google News RSS ignores OR/AND — use phrase matching only
# ------------------------------------------------------------------

SEARCH_QUERIES = [
    # Valuation & Reserving
    ("Valuation & Reserving",     "VM-20 life insurance reserve"),
    ("Valuation & Reserving",     "VM-22 annuity reserve NAIC"),
    ("Valuation & Reserving",     "principle based reserving life"),
    ("Valuation & Reserving",     "LDTI life insurance accounting"),
    ("Valuation & Reserving",     "life insurance actuarial reserve"),

    # Regulatory
    ("Regulatory",                "NAIC Life Actuarial Task Force"),
    ("Regulatory",                "NAIC annuity suitability regulation"),
    ("Regulatory",                "DOL fiduciary rule annuity"),
    ("Regulatory",                "life insurance state regulation"),
    ("Regulatory",                "annuity best interest regulation"),

    # Mortality & Experience
    ("Mortality & Experience",    "SOA mortality study life"),
    ("Mortality & Experience",    "life insurance mortality improvement"),
    ("Mortality & Experience",    "GLP-1 ozempic life insurance"),
    ("Mortality & Experience",    "longevity annuity risk study"),
    ("Mortality & Experience",    "COVID excess mortality life insurance"),

    # Reinsurance — life-specific
    ("Reinsurance",               "life reinsurance transaction Bermuda"),
    ("Reinsurance",               "asset intensive reinsurance deal"),
    ("Reinsurance",               "funded reinsurance life annuity"),
    ("Reinsurance",               "pension risk transfer reinsurance"),
    ("Reinsurance",               "life block reinsurance assumption"),

    # Capital & Risk
    ("Capital & Risk",            "life insurance RBC capital NAIC"),
    ("Capital & Risk",            "AM Best life insurer rating action"),
    ("Capital & Risk",            "Moody's life insurance rating"),
    ("Capital & Risk",            "Fitch life insurer outlook"),
    ("Capital & Risk",            "life insurance solvency capital ratio"),

    # Annuity Market — high volume, core section
    ("Annuity Market",            "fixed indexed annuity FIA sales"),
    ("Annuity Market",            "RILA registered linked annuity"),
    ("Annuity Market",            "MYGA multi-year guaranteed annuity rate"),
    ("Annuity Market",            "LIMRA annuity sales record"),
    ("Annuity Market",            "personal income annuity PIA"),
    ("Annuity Market",            "annuity product launch"),
    ("Annuity Market",            "deferred income annuity sales"),

    # Life Products
    ("Life Product Developments", "indexed universal life IUL"),
    ("Life Product Developments", "IUL AG 49 actuarial guideline"),
    ("Life Product Developments", "term life insurance rate filing"),
    ("Life Product Developments", "whole life dividend interest rate"),
    ("Life Product Developments", "life insurance product innovation"),

    # ALM & Investments
    ("Investments & ALM",         "private credit life insurer portfolio"),
    ("Investments & ALM",         "life insurance investment strategy"),
    ("Investments & ALM",         "insurer asset liability management"),
    ("Investments & ALM",         "life insurer alternative assets"),
    ("Investments & ALM",         "insurance company bond portfolio"),

    # Industry Trends
    ("Industry Trends",           "life insurance artificial intelligence AI"),
    ("Industry Trends",           "private equity life insurance acquisition"),
    ("Industry Trends",           "insurtech life annuity technology"),
    ("Industry Trends",           "life insurance distribution channel"),
    ("Industry Trends",           "PE backed life insurer Bermuda"),

    # Research
    ("SOA / AAA Research",        "Society of Actuaries research report"),
    ("SOA / AAA Research",        "American Academy of Actuaries life"),
    ("SOA / AAA Research",        "actuarial research longevity mortality"),
    ("Consulting & Research",     "Milliman life insurance actuarial"),
    ("Consulting & Research",     "Oliver Wyman insurance report"),
    ("Consulting & Research",     "Willis Towers Watson life insurance"),
]

# ------------------------------------------------------------------
# Carrier Newsroom Queries
#
# CRITICAL: Single carrier name queries outperform compound queries
# on Google News RSS. The gate in intelligence.py enforces life/annuity
# relevance, so broad queries are safe here.
# ------------------------------------------------------------------

CARRIER_SEARCH_QUERIES = [
    # Mutuals & Giants — use name alone for broadest coverage
    ("Carrier Intelligence", "New York Life insurance"),
    ("Carrier Intelligence", "MassMutual life annuity"),
    ("Carrier Intelligence", "Northwestern Mutual insurance"),
    ("Carrier Intelligence", "Guardian Life insurance"),
    ("Carrier Intelligence", "Penn Mutual life"),
    ("Carrier Intelligence", "TIAA life annuity"),
    ("Carrier Intelligence", "New York Life annuity"),

    # Large publics — earnings and strategic moves
    ("Carrier Intelligence", "MetLife life insurance earnings"),
    ("Carrier Intelligence", "MetLife annuity results"),
    ("Carrier Intelligence", "Prudential Financial life insurance"),
    ("Carrier Intelligence", "Prudential annuity earnings"),
    ("Carrier Intelligence", "Lincoln Financial annuity"),
    ("Carrier Intelligence", "Lincoln Financial Group earnings"),
    ("Carrier Intelligence", "Corebridge Financial annuity"),
    ("Carrier Intelligence", "Equitable Holdings annuity life"),
    ("Carrier Intelligence", "Unum Group life insurance"),
    ("Carrier Intelligence", "Principal Financial life annuity"),
    ("Carrier Intelligence", "Brighthouse Financial annuity"),
    ("Carrier Intelligence", "Nationwide life annuity"),

    # PE-backed annuity leaders — most active in reinsurance/M&A
    ("Carrier Intelligence", "Athene annuity"),
    ("Carrier Intelligence", "Athene reinsurance life"),
    ("Carrier Intelligence", "Global Atlantic life annuity"),
    ("Carrier Intelligence", "Global Atlantic reinsurance"),
    ("Carrier Intelligence", "F&G annuity life"),
    ("Carrier Intelligence", "Fidelity Guaranty Life annuity"),
    ("Carrier Intelligence", "Jackson National annuity"),
    ("Carrier Intelligence", "Allianz Life annuity"),
    ("Carrier Intelligence", "Symetra life annuity"),
    ("Carrier Intelligence", "Gainbridge annuity"),
    ("Carrier Intelligence", "Fortitude Re life reinsurance"),
    ("Carrier Intelligence", "Resolution Life reinsurance"),
    ("Carrier Intelligence", "Somerset Re life reinsurance"),
    ("Carrier Intelligence", "Talcott Resolution life"),

    # Regionals & Mid-size
    ("Carrier Intelligence", "Ameritas life insurance"),
    ("Carrier Intelligence", "Securian Financial life"),
    ("Carrier Intelligence", "Mutual of Omaha life insurance"),
    ("Carrier Intelligence", "Protective Life annuity"),
    ("Carrier Intelligence", "Transamerica life annuity"),
    ("Carrier Intelligence", "Pacific Life annuity"),
    ("Carrier Intelligence", "Pacific Life Re reinsurance"),
    ("Carrier Intelligence", "Sun Life US annuity"),
    ("Carrier Intelligence", "Midland National annuity"),
    ("Carrier Intelligence", "North American life annuity"),
    ("Carrier Intelligence", "American Equity annuity"),
    ("Carrier Intelligence", "AIG life insurance annuity"),
    ("Carrier Intelligence", "Sammons Financial annuity"),
]
