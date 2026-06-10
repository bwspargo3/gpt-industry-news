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
]

# ------------------------------------------------------------------
# Direct RSS Feeds
# These are confirmed life/annuity-relevant sources.
# The intelligence.py fetcher uses rotating browser user-agents
# which is required — plain requests get 403 from most trade sites.
# ------------------------------------------------------------------

DIRECT_RSS_FEEDS = [
    # Core life/annuity trade press
    ("Trade Press",          "Carrier Management",       "https://www.carriermanagement.com/feed/"),
    ("Annuity Market",       "Life Annuity Specialist",  "https://lifeannuityspecialist.com/feed/"),

    # Reinsurance (confirmed working — produced all today's articles)
    ("Reinsurance",          "Reinsurance News",         "https://www.reinsurancene.ws/feed/"),

    # Rating agency — AM Best is the primary life/annuity rating source
    ("Rating Agency Actions","AM Best News",             "https://www.ambest.com/rss/latestnews.rss"),

    # Regulatory — IRS life insurance rulings
    ("Regulatory",           "Federal Register (IRS Life)",
     "https://www.federalregister.gov/api/v1/articles.rss?agencies[]=internal-revenue-service&topics[]=life-insurance"),

    # Regulatory — NAIC general news (separate from the LATF scraper)
    ("Regulatory",           "Federal Register (Treasury)",
     "https://www.federalregister.gov/api/v1/articles.rss?agencies[]=department-of-the-treasury&topics[]=life-insurance"),

    # Insurance Journal — P&C focused but covers major market moves
    ("Trade Press",          "Insurance Journal",        "https://www.insurancejournal.com/feed/"),
]
# Note: ThinkAdvisor, BenefitsPro, Pensions & Investments, InvestmentNews
# RSS feeds all returning 404 as of June 2026. Removed to reduce dead-source noise.
# Google News queries cover the same content via search.

# ------------------------------------------------------------------
# Google News RSS Queries — industry topics
#
# KEY LESSONS FROM PRODUCTION:
# 1. Do NOT append the year — Google News RSS date-ranks naturally
# 2. Keep queries SHORT (3-5 words) — long boolean queries fail silently
# 3. Quote exact phrases that must appear together
# 4. Google News RSS ignores most boolean operators — use phrase matching
# ------------------------------------------------------------------

SEARCH_QUERIES = [
    # Valuation & Reserving
    ("Valuation & Reserving",   "VM-20 life insurance reserve"),
    ("Valuation & Reserving",   "VM-22 annuity NAIC reserve"),
    ("Valuation & Reserving",   "principle based reserving life"),
    ("Valuation & Reserving",   "PBR life insurance actuarial"),
    ("Valuation & Reserving",   "LDTI life insurance accounting"),

    # Regulatory
    ("Regulatory",              "NAIC Life Actuarial Task Force"),
    ("Regulatory",              "NAIC annuity regulation"),
    ("Regulatory",              "DOL fiduciary rule annuity"),
    ("Regulatory",              "SEC annuity regulation 2026"),

    # Mortality & Experience
    ("Mortality & Experience",  "SOA mortality study"),
    ("Mortality & Experience",  "life insurance mortality experience"),
    ("Mortality & Experience",  "GLP-1 life insurance mortality"),
    ("Mortality & Experience",  "longevity risk life annuity"),

    # Reinsurance — LIFE specific (not P&C brokers)
    ("Reinsurance",             "life reinsurance transaction"),
    ("Reinsurance",             "asset intensive reinsurance"),
    ("Reinsurance",             "funded reinsurance life"),
    ("Reinsurance",             "Bermuda life reinsurance"),

    # Capital & Risk
    ("Capital & Risk",          "life insurance RBC capital NAIC"),
    ("Capital & Risk",          "AM Best life insurer rating"),
    ("Capital & Risk",          "life insurance solvency capital"),

    # Annuity Market
    ("Annuity Market",          "fixed indexed annuity sales LIMRA"),
    ("Annuity Market",          "RILA registered index annuity"),
    ("Annuity Market",          "MYGA multi-year guaranteed annuity"),
    ("Annuity Market",          "annuity sales record 2026"),
    ("Annuity Market",          "personal income annuity"),

    # Life Products
    ("Life Product Developments", "indexed universal life pricing"),
    ("Life Product Developments", "IUL actuarial guideline AG 49"),
    ("Life Product Developments", "term life insurance pricing"),

    # ALM & Investments
    ("Investments & ALM",       "private credit life insurer"),
    ("Investments & ALM",       "life insurance investment portfolio"),
    ("Investments & ALM",       "asset liability management annuity"),

    # Industry
    ("Industry Trends",         "life insurance artificial intelligence"),
    ("Industry Trends",         "private equity life insurance"),
    ("Industry Trends",         "insurtech life annuity"),

    # Research
    ("SOA / AAA Research",      "Society of Actuaries research"),
    ("SOA / AAA Research",      "American Academy Actuaries life"),
    ("Consulting & Research",   "Milliman life insurance report"),
    ("Consulting & Research",   "Oliver Wyman life insurance"),
]

# ------------------------------------------------------------------
# Carrier Newsroom Queries
# Focused on US life/annuity carriers only.
# Queries use the carrier name alone — "press release OR newsroom"
# adds noise on Google News RSS and doesn't improve results.
# ------------------------------------------------------------------

CARRIER_SEARCH_QUERIES = [
    # Mutuals & Giants
    ("Carrier Intelligence", '"New York Life" life insurance'),
    ("Carrier Intelligence", '"MassMutual" annuity life'),
    ("Carrier Intelligence", '"Northwestern Mutual" life insurance'),
    ("Carrier Intelligence", '"Guardian Life" insurance'),
    ("Carrier Intelligence", '"Penn Mutual" life'),

    # Publics
    ("Carrier Intelligence", '"MetLife" life insurance annuity'),
    ("Carrier Intelligence", '"Prudential Financial" life annuity'),
    ("Carrier Intelligence", '"Lincoln Financial" annuity'),
    ("Carrier Intelligence", '"Corebridge Financial"'),
    ("Carrier Intelligence", '"Equitable Holdings" annuity'),

    # Annuity Leaders & PE-Backed
    ("Carrier Intelligence", '"Athene" annuity reinsurance'),
    ("Carrier Intelligence", '"Global Atlantic" life annuity'),
    ("Carrier Intelligence", '"F&G" annuity life insurance'),
    ("Carrier Intelligence", '"Jackson National" annuity'),
    ("Carrier Intelligence", '"Allianz Life" annuity'),
    ("Carrier Intelligence", '"Symetra" life annuity'),
    ("Carrier Intelligence", '"Fortitude Re" reinsurance'),
    ("Carrier Intelligence", '"Resolution Life" reinsurance'),

    # Regionals
    ("Carrier Intelligence", '"Ameritas" life insurance'),
    ("Carrier Intelligence", '"Securian Financial" life'),
    ("Carrier Intelligence", '"Mutual of Omaha" life insurance'),
    ("Carrier Intelligence", '"Protective Life" annuity'),
    ("Carrier Intelligence", '"Transamerica" life annuity'),
    ("Carrier Intelligence", '"Pacific Life" annuity'),
    ("Carrier Intelligence", '"Sun Life" US annuity'),
    ("Carrier Intelligence", '"Principal Financial" life'),
    ("Carrier Intelligence", '"Brighthouse Financial" annuity'),
    ("Carrier Intelligence", '"Nationwide" life annuity'),
]
