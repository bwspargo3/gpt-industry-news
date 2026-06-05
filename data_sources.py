# ------------------------------------------------------------------
# NewsAPI Boolean Queries
# Targets specific actuarial and life/annuity developments
# ------------------------------------------------------------------

NEWSAPI_QUERIES = [
    ("Valuation & Reserving", '("life insurance" OR annuity) AND ("VM-20" OR "VM-22" OR PBR OR "principle based reserving")'),
    ("Regulatory", '("life insurance" OR annuity) AND (NAIC OR LATF OR "Department of Labor" OR "fiduciary rule")'),
    ("Accounting & LDTI", '("life insurance" OR annuity) AND ("LDTI" OR "ASC 944" OR FASB)'),
    ("Mortality & Experience", '("life insurance" OR annuity) AND (mortality OR "experience study" OR longevity)'),
    ("Reinsurance", '"life reinsurance" OR "asset intensive reinsurance" OR "Bermuda"'),
    ("Capital & Risk", '("life insurance" OR annuity) AND ("risk based capital" OR RBC OR "rating agency")'),
    ("Annuity Market", '"fixed indexed annuity" OR RILA OR MYGA OR "annuity sales"'),
    ("Life Product Developments", '"indexed universal life" OR "term life insurance" OR "AG 49"'),
    ("Investments & ALM", '("life insurance" OR annuity) AND ("private credit" OR "asset liability management")'),
    ("Industry Trends", '("life insurance" OR annuity) AND ("artificial intelligence" OR insurtech OR "private equity")'),
    ("Consulting & Research", '("life insurance" OR annuity) AND (Milliman OR "Oliver Wyman" OR Deloitte OR PwC OR EY)'),
]

# ------------------------------------------------------------------
# Direct RSS Feeds — Verified open access (No Paywalls)
# ------------------------------------------------------------------

DIRECT_RSS_FEEDS = [
    (
        "Trade Press",
        "Insurance Journal",
        "https://www.insurancejournal.com/rss/lifehealth/",
    ),
    (
        "Carrier Intelligence",
        "PR Newswire",
        "https://www.prnewswire.com/rss/financial-services/insurance-latest-news/insurance-latest-news-list.rss"
    ),
    (
        "Rating Agency Actions",
        "AM Best",
        "https://news.ambest.com/PressReleases.aspx?rss=1"
    ),
    (
        "Regulatory",
        "Federal Register (IRS Life)",
        "https://www.federalregister.gov/api/v1/articles.rss?conditions[term]=life+insurance+annuity",
    ),
    (
        "Annuity Market",
        "Advisor Perspectives",
        "https://www.advisorperspectives.com/rss",
    ),
    (
        "Investments & ALM",
        "Pensions & Investments",
        "https://www.pionline.com/rss/all",
    ),
]

# ------------------------------------------------------------------
# Google News Search Queries (Fallback/Supplemental)
# ------------------------------------------------------------------

SEARCH_QUERIES = [
    ("Valuation & Reserving", "VM-20 life insurance reserve 2026"),
    ("Valuation & Reserving", "VM-22 annuity reserve NAIC 2026"),
    ("Valuation & Reserving", "principle based reserving life insurance"),
    ("Regulatory", "NAIC Life Actuarial Task Force LATF 2026"),
    ("Regulatory", "state insurance department life annuity bulletin 2026"),
    ("Accounting & LDTI", "LDTI long duration targeted improvements 2026"),
    ("Mortality & Experience", "SOA mortality study life insurance 2026"),
    ("Mortality & Experience", "GLP-1 ozempic semaglutide life insurance mortality"),
    ("Reinsurance", "life reinsurance transaction 2026"),
    ("Capital & Risk", "life insurance RBC risk based capital NAIC 2026"),
    ("Annuity Market", "fixed indexed annuity FIA sales record 2026"),
    ("Annuity Market", "RILA registered index linked annuity 2026"),
    ("Life Product Developments", "indexed universal life IUL pricing 2026"),
    ("Investments & ALM", "private credit life insurance portfolio 2026"),
    ("Investments & ALM", "asset liability management life annuity insurer"),
    ("SOA / AAA Research", "\"Society of Actuaries\" research report life annuity 2026"),
    ("SOA / AAA Research", "\"American Academy of Actuaries\" life insurance annuity 2026"),
]

# ------------------------------------------------------------------
# Carrier Watchlist Queries
# ------------------------------------------------------------------

CARRIER_SEARCH_QUERIES = [
    ("Carrier Intelligence", "\"Kansas City Life\" insurance"),
    ("Carrier Intelligence", "\"Ameritas Life\" insurance annuity"),
    ("Carrier Intelligence", "\"Securian Financial\" life insurance"),
    ("Carrier Intelligence", "\"Country Financial\" life insurance annuity"),
    ("Carrier Intelligence", "\"Business Men's Assurance\" BMI life"),
    ("Carrier Intelligence", "\"Midland National\" life insurance annuity"),
    ("Carrier Intelligence", "\"North American Company\" life annuity Sammons"),
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
    ("Carrier Intelligence", "\"Sammons Financial\" life insurance"),
    ("Carrier Intelligence", "\"Jackson National\" life annuity"),
    ("Carrier Intelligence", "\"Principal Financial\" life insurance 2026"),
]
