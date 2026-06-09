# ------------------------------------------------------------------
# NewsAPI Boolean Queries
# ------------------------------------------------------------------

NEWSAPI_QUERIES = [
    ("Valuation & Reserving", '("life insurance" OR annuity) AND ("VM-20" OR "VM-22" OR PBR OR "principle based reserving")'),
    ("Regulatory", '("life insurance" OR annuity) AND (NAIC OR LATF OR "Department of Labor" OR "fiduciary rule")'),
    ("Accounting & LDTI", '("life insurance" OR annuity) AND ("LDTI" OR "ASC 944" OR FASB)'),
    ("Mortality & Experience", '("life insurance" OR annuity) AND (mortality OR "experience study" OR longevity)'),
    ("Reinsurance", '"life reinsurance" OR "asset intensive reinsurance" OR "Bermuda reinsurance"'),
    ("Capital & Risk", '("life insurance" OR annuity) AND ("risk based capital" OR RBC OR "rating agency")'),
    ("Annuity Market", '"fixed indexed annuity" OR RILA OR MYGA OR "annuity sales" OR "personal income annuity"'),
    ("Life Product Developments", '"indexed universal life" OR "term life insurance" OR "AG 49"'),
    ("Investments & ALM", '("life insurance" OR annuity) AND ("private credit" OR "asset liability management")'),
    ("Industry Trends", '("life insurance" OR annuity) AND ("artificial intelligence" OR insurtech OR "private equity")'),
    ("Consulting & Research", '("life insurance" OR annuity) AND (Milliman OR "Oliver Wyman" OR Deloitte OR PwC OR EY)'),
]

# ------------------------------------------------------------------
# Direct RSS Feeds
# ------------------------------------------------------------------

DIRECT_RSS_FEEDS = [
    ("Trade Press", "Carrier Management", "https://www.carriermanagement.com/feed/"),
    ("Reinsurance", "Reinsurance News", "https://www.reinsurancene.ws/feed/"),
    ("Annuity Market", "Life Annuity Specialist", "https://lifeannuityspecialist.com/feed/"),
    ("Rating Agency Actions", "AM Best News", "https://www.ambest.com/rss/latestnews.rss"),
    ("Regulatory", "Federal Register (IRS Life)", "https://www.federalregister.gov/api/v1/articles.rss?agencies[]=internal-revenue-service&topics[]=life-insurance"),
]

# ------------------------------------------------------------------
# Google News Queries — industry topics
# ------------------------------------------------------------------

SEARCH_QUERIES = [
    ("Valuation & Reserving", "VM-20 life insurance reserve 2026"),
    ("Valuation & Reserving", "VM-22 annuity reserve NAIC 2026"),
    ("Valuation & Reserving", "principle based reserving life insurance"),
    ("Regulatory", "NAIC Life Actuarial Task Force LATF 2026"),
    ("Accounting & LDTI", "LDTI long duration targeted improvements 2026"),
    ("Mortality & Experience", "SOA mortality study life insurance 2026"),
    ("Reinsurance", "life reinsurance transaction bermuda 2026"),
    ("Capital & Risk", "life insurance RBC risk based capital NAIC 2026"),
    ("Annuity Market", "fixed indexed annuity FIA sales LIMRA 2026"),
    ("Annuity Market", "personal income annuity PIA 2026"),
    ("Life Product Developments", "indexed universal life IUL pricing 2026"),
    ("Investments & ALM", "private credit life insurance portfolio 2026"),
    ("SOA / AAA Research", '"Society of Actuaries" research report life annuity 2026'),
]

# ------------------------------------------------------------------
# Carrier Newsroom & PR Queries (High Volume)
# ------------------------------------------------------------------

CARRIER_SEARCH_QUERIES = [
    # Mutuals & Giants
    ("Carrier Intelligence", '"New York Life" press release OR newsroom'),
    ("Carrier Intelligence", '"MassMutual" press release OR newsroom'),
    ("Carrier Intelligence", '"Northwestern Mutual" press release OR newsroom'),
    ("Carrier Intelligence", '"Guardian Life" press release OR newsroom'),
    ("Carrier Intelligence", '"Penn Mutual" press release OR newsroom'),
    
    # Publics
    ("Carrier Intelligence", '"MetLife" press release OR newsroom'),
    ("Carrier Intelligence", '"Prudential Financial" press release OR newsroom'),
    ("Carrier Intelligence", '"Lincoln Financial" press release OR newsroom'),
    ("Carrier Intelligence", '"Corebridge Financial" press release OR newsroom'),
    ("Carrier Intelligence", '"Equitable Holdings" press release OR newsroom'),

    # Annuity Leaders & PE-Backed
    ("Carrier Intelligence", '"Athene" press release OR newsroom'),
    ("Carrier Intelligence", '"Global Atlantic" press release OR newsroom'),
    ("Carrier Intelligence", '"F&G" press release OR newsroom'),
    ("Carrier Intelligence", '"Jackson National" press release OR newsroom'),
    ("Carrier Intelligence", '"Allianz Life" press release OR newsroom'),
    ("Carrier Intelligence", '"Symetra" press release OR newsroom'),
    ("Carrier Intelligence", '"Gainbridge" press release OR newsroom'),
    ("Carrier Intelligence", '"Fortitude Re" press release OR newsroom'),
    ("Carrier Intelligence", '"Resolution Life" press release OR newsroom'),

    # Regionals & Others
    ("Carrier Intelligence", '"Kansas City Life" press release OR newsroom'),
    ("Carrier Intelligence", '"Ameritas" press release OR newsroom'),
    ("Carrier Intelligence", '"Securian Financial" press release OR newsroom'),
    ("Carrier Intelligence", '"Mutual of Omaha" press release OR newsroom'),
    ("Carrier Intelligence", '"Sammons Financial" press release OR newsroom'),
    ("Carrier Intelligence", '"Protective Life" press release OR newsroom'),
    ("Carrier Intelligence", '"Transamerica" press release OR newsroom'),
]
