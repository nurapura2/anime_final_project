import random
import time

# Base website URL
BASE_URL = "https://old.yummyani.me"
CATALOG_URL = "https://old.yummyani.me/catalog"

# Headers to avoid blocking by the website
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
}

# Timeout for requests
TIMEOUT = 10

# Delay between requests 
DELAY      = (1.0, 2.5)   # between requests
DELAY_LONG = (10.0, 20.0) # at checkpoints
DELAY_ERR  = (5.0, 15.0)  # on 429/503

# Maximum number of pages to scrape per category
MAX_PAGES = 50

