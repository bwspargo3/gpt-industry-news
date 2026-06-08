# ------------------------------------------------------------------
# NewsAPI Boolean Queries
# ------------------------------------------------------------------

NEWSAPI_QUERIES = [
    ("Valuation & Reserving",
     '("life insurance" OR annuity) AND ("VM-20" OR "VM-22" OR PBR OR "principle based reserving")'),
    ("Regulatory",
     '("life insurance" OR annuity) AND (NAIC OR LATF OR "Department of Labor" OR "fiduciary rule")'),
    ("Accounting & LDTI",
     '("life insurance" OR annuity) AND ("LDTI" OR "ASC 944" OR FASB)'),
    ("Mortality & Experience",
     '("life insurance" OR annuity) AND (mortality OR "experience study" OR longevity)'),
    ("Reinsurance",
     '"life reinsurance" OR "asset intensive reinsurance" OR "Bermuda reinsurance"'),
    ("Capital & Risk",
     '("life insurance" OR annuity) AND ("risk based capital" OR RBC OR "rating agency")'),
    ("Annuity Market",
     '"fixed indexed annuity" OR RILA OR MYGA OR "annuity sales"'),
    ("Life Product Developments",
     '"indexed universal life" OR "term life insurance" OR "AG 49"'),
    ("Investments & ALM",
     '("life insurance" OR annuity) AND ("private credit" OR "asset liability management")'),
    ("Industry Trends",
     '("life insurance" OR annuity) AND ("artificial intelligence" OR insurtech OR "private equity")'),
    ("Consulting & Research",
     '("life insurance" OR annuity) AND (Milliman OR "Oliver Wyman" OR Deloitte OR PwC OR EY)'),
]

# ------------------------------------------------------------------
# Direct RSS Feeds
# URLs verified or corrected based on live error logs.
# Feeds confirmed dead (403/404) have been removed.
# ------------------------------------------------------------------

DIRECT_RSS_FEEDS = [
    # Carrier Management — confirmed working
    (
        "Trade Press",
        "Carrier Management",
        "https://www.carriermanagement.com/feed/",
    ),
    # Reinsurance News — confirmed working
    (
        "Reinsurance",
        "Reinsurance News",
        "https://www.reinsurancene.ws/feed/",
    ),
    # Life Annuity Specialist — parser handles malformed XML
    (
        "Annuity Market",
        "Life Annuity Specialist",
        "https://lifeannuityspecialist.com/feed/",
    ),
    # AM Best — editorial news (not PR wire)
    (
        "Rating Agency Actions",
        "AM Best News",
        "https://www.ambest.com/rss/latestnews.rss",
    ),
    # Federal Register — IRS life insurance only
    (
        "Regulatory",
        "Federal Register (IRS Life)",
        "https://www.federalregister.gov/api/v1/articles.rss"
        "?agencies[]=internal-revenue-service"
        "&topics[]=life-insurance",
    ),
    # REMOVED (confirmed dead in logs):
    # - Advisor Perspectives: 403
    # - Pensions & Investments /rss/all: 404
    # - PR Newswire insurance: too noisy, not actuarially relevant
    # - Insurance Journal /rss/lifehealth/: 404
]

# ------------------------------------------------------------------
# Google News Queries — industry topics
# ------------------------------------------------------------------

SEARCH_QUERIES = [
    ("Valuation & Reserving", "VM-20 life insurance reserve 2026"),
    ("Valuation & Reserving", "VM-22 annuity reserve NAIC 2026"),
    ("Valuation & Reserving", "principle based reserving life insurance"),
    ("Valuation & Reserving", "asset adequacy testing cash flow testing life insurance"),
    ("Regulatory", "NAIC Life Actuarial Task Force LATF 2026"),
    ("Regulatory", "NAIC actuarial guideline life insurance adopted"),
    ("Regulatory", "state insurance department life annuity bulletin 2026"),
    ("Accounting & LDTI", "LDTI long duration targeted improvements 2026"),
    ("Accounting & LDTI", "ASC 944 FASB life insurance 2026"),
    ("Mortality & Experience", "SOA mortality study life insurance 2026"),
    ("Mortality & Experience", "GLP-1 ozempic semaglutide life insurance mortality"),
    ("Mortality & Experience", "excess mortality life insurance 2026"),
    ("Reinsurance", "life reinsurance transaction bermuda 2026"),
    ("Reinsurance", "asset intensive reinsurance funds withheld modco"),
    ("Capital & Risk", "life insurance RBC risk based capital NAIC 2026"),
    ("Capital & Risk", "AM Best life insurer rating action 2026"),
    ("Annuity Market", "fixed indexed annuity FIA sales LIMRA 2026"),
    ("Annuity Market", "RILA registered index linked annuity 2026"),
    ("Annuity Market", "MYGA multi year guaranteed annuity 2026"),
    ("Life Product Developments", "indexed universal life IUL pricing 2026"),
    ("Life Product Developments", "AG 49 IUL illustration actuarial guideline"),
    ("Life Product Developments", "term life insurance pricing 2026"),
    ("Investments & ALM", "private credit life insurance portfolio 2026"),
    ("Investments & ALM", "asset liability management annuity insurer 2026"),
    ("SOA / AAA Research",
     '"Society of Actuaries" research report life annuity 2026'),
    ("SOA / AAA Research",
     '"American Academy of Actuaries" life insurance annuity 2026'),
    ("Industry Trends", "artificial intelligence actuarial life insurance 2026"),
    ("Industry Trends", "private equity life insurance acquisition 2026"),
    ("Consulting & Research", '"Milliman" life insurance actuarial 2026'),
    ("Consulting & Research", '"Oliver Wyman" life insurance annuity 2026'),
]

# ------------------------------------------------------------------
# Carrier Watchlist Queries
# ------------------------------------------------------------------

# ------------------------------------------------------------------
# Carrier Watchlist Queries
# ------------------------------------------------------------------

CARRIER_SEARCH_QUERIES = [

    # Mutuals
    ("Carrier Intelligence", '"New York Life"'),
    ("Carrier Intelligence", '"MassMutual"'),
    ("Carrier Intelligence", '"Northwestern Mutual"'),
    ("Carrier Intelligence", '"Guardian Life"'),
    ("Carrier Intelligence", '"Penn Mutual"'),
    ("Carrier Intelligence", '"Western & Southern"'),
    ("Carrier Intelligence", '"National Life Group"'),

    # Public Life Insurers
    ("Carrier Intelligence", '"MetLife"'),
    ("Carrier Intelligence", '"Prudential Financial"'),
    ("Carrier Intelligence", '"Lincoln Financial"'),
    ("Carrier Intelligence", '"Brighthouse Financial"'),
    ("Carrier Intelligence", '"Corebridge Financial"'),
    ("Carrier Intelligence", '"Principal Financial"'),
    ("Carrier Intelligence", '"Equitable Holdings"'),

    # Annuity Leaders
    ("Carrier Intelligence", '"Athene"'),
    ("Carrier Intelligence", '"Global Atlantic"'),
    ("Carrier Intelligence", '"F&G"'),
    ("Carrier Intelligence", '"Jackson National"'),
    ("Carrier Intelligence", '"Allianz Life"'),
    ("Carrier Intelligence", '"Nationwide"'),
    ("Carrier Intelligence", '"Symetra"'),
    ("Carrier Intelligence", '"Delaware Life"'),
    ("Carrier Intelligence", '"Gainbridge"'),

    # Regional / Mutual
    ("Carrier Intelligence", '"Kansas City Life"'),
    ("Carrier Intelligence", '"Ameritas"'),
    ("Carrier Intelligence", '"Securian Financial"'),
    ("Carrier Intelligence", '"Country Financial"'),
    ("Carrier Intelligence", '"Mutual of Omaha"'),
    ("Carrier Intelligence", '"OneAmerica"'),
    ("Carrier Intelligence", '"Foresters Financial"'),
    ("Carrier Intelligence", '"American National"'),
    ("Carrier Intelligence", '"Sagicor Life"'),

    # Sammons
    ("Carrier Intelligence", '"Midland National"'),
    ("Carrier Intelligence", '"North American Company"'),
    ("Carrier Intelligence", '"Sammons Financial"'),

    # PE / Bermuda
    ("Carrier Intelligence", '"26North"'),
    ("Carrier Intelligence", '"Fortitude Re"'),
    ("Carrier Intelligence", '"Resolution Life"'),
    ("Carrier Intelligence", '"Martello Re"'),
    ("Carrier Intelligence", '"Aspida"'),

    # Existing
    ("Carrier Intelligence", '"Protective Life"'),
    ("Carrier Intelligence", '"Transamerica"'),
    ("Carrier Intelligence", '"Nassau Financial"'),
    ("Carrier Intelligence", '"Pacific Life"'),
    ("Carrier Intelligence", '"CNO Financial"'),

    # Carrier Event Searches
    ("Carrier Intelligence",
     'life insurer earnings OR annuity carrier earnings'),

    ("Carrier Intelligence",
     'life insurance company acquisition'),

    ("Carrier Intelligence",
     'life insurer reinsurance transaction'),

    ("Carrier Intelligence",
     'annuity carrier product launch'),

    ("Carrier Intelligence",
     'life insurer rating action'),

    ("Carrier Intelligence",
     'life insurance strategic partnership'),

    ("Carrier Intelligence",
     'life insurance distribution agreement'),

    ("Carrier Intelligence",
     'life insurer capital management'),
]
