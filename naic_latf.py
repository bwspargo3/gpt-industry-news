import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

NAIC_CACHE_FILE = "naic_latf_cache.json"

BROWSER_HEADERS = {
    "User-Agent": "ActuarialIntelligence/1.0",
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Connection":      "keep-alive",
}

NAIC_TTL_DAYS     = 90
NAIC_MAX_ITEMS    = 1500
BASE_URL          = "https://content.naic.org"
INDEX_URL         = f"{BASE_URL}/cmte_a_latf.htm"
DOCUMENT_EXTS     = (".pdf", ".docx", ".doc", ".xlsx", ".pptx")

MONTH_MAP = {
    "january": "01", "february": "02", "march": "03",
    "april":   
