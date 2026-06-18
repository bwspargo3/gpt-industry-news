# ------------------------------------------------------------------
# NewsAPI Boolean Queries
# ------------------------------------------------------------------

NEWSAPI_QUERIES = [
    ("Valuation & Regulatory", '("life insurance" OR annuity) AND (VM-20 OR VM-22 OR PBR OR NAIC OR LATF OR LDTI OR FASB)'),
    ("Market & Products",      '("life insurance" OR annuity) AND (mortality OR reinsurance OR "fixed indexed" OR RILA OR IUL OR "private credit")'),
    ("Carrier Intelligence",   '(MetLife OR Prudential OR MassMutual OR Athene OR Corebridge OR Equitable) AND (earnings OR results OR annuity)'),
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

    # Rating agencies (REMOVED AM BEST - BLOCKED BY BOT MANAGER)
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
    ("Valuation & Reserving", "Moody's AXIS OR Milliman OR 'Oliver Wyman' life insurance"),
    ("Reinsurance",           "Mayer Brown OR Skadden life reinsurance"),
    ("Accounting & LDTI",     "PwC OR EY OR Deloitte LDTI insurance"),
    ("Mortality & Experience", "Munich Re OR SCOR mortality"),
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
    ("Valuation & Reserving",     "(VM-20 OR VM-22 OR PBR OR LDTI OR FASB) 'life insurance'"),
    ("Regulatory",                "(NAIC OR LATF OR 'DOL fiduciary') (actuarial OR annuity)"),
    ("Mortality & Experience",    "(mortality OR 'experience study' OR GLP-1 OR longevity) 'life insurance'"),
    ("Reinsurance",               "(reinsurance OR 'pension risk transfer') 'life insurance'"),
    ("Capital & Risk",            "(RBC OR 'solvency ratio' OR 'capital ratio') 'life insurance'"),
    ("Annuity Market",            "(FIA OR RILA OR MYGA OR LIMRA OR Wink OR Conning) annuity"),
    ("Life Product Developments", "(IUL OR 'AG 49' OR 'term life' OR 'whole life') insurance"),
    ("ALM & Investments",         "('private credit' OR ALM) 'life insurer'"),
    ("Industry Trends",           "(AI OR 'insurtech' OR 'private equity') 'life insurance'"),
    ("SOA / AAA Research",        "(SOA OR 'Society of Actuaries' OR AAA) research"),
]

# ------------------------------------------------------------------
# Carrier Newsroom Queries
#
# CRITICAL: Single carrier name queries outperform compound queries
# on Google News RSS. The gate in intelligence.py enforces life/annuity
# relevance, so broad queries are safe here.
# ------------------------------------------------------------------

CARRIER_SEARCH_QUERIES = [
    ("Carrier Intelligence", "MetLife OR Prudential OR MassMutual OR 'New York Life' OR 'Northwestern Mutual'"),
    ("Carrier Intelligence", "'Lincoln Financial' OR Corebridge OR Equitable OR Brighthouse OR Principal OR AIG"),
    ("Carrier Intelligence", "Athene OR 'Global Atlantic' OR Jackson OR F&G OR Gainbridge OR 'Allianz Life'"),
    ("Carrier Intelligence", "'Fortitude Re' OR 'Resolution Life' OR 'Somerset Re' OR 'Pacific Life' OR Transamerica"),
    ("Carrier Intelligence", "Nationwide OR Ameritas OR 'Protective Life' OR Sammons"),
]
