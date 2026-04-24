# Base website URL
BASE_URL = "https://www.hltv.org/"

# Category pages to scrape
CATEGORY_MAP = {
    "players": "https://www.hltv.org/players",
    "player_stats": "https://www.hltv.org/stats?csVersion=CS2",
    "maps": "https://www.hltv.org/stats/maps",
    "teams": "https://www.hltv.org/stats/teams?startDate=all",
    "matches": "https://www.hltv.org/stats/matches?startDate=all",
    "tournaments": "https://www.hltv.org/stats/events?startDate=all"
}
# Headers to avoid blocking by the website
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
    "Referer": "https://www.google.com/",
    "DNT": "1"
}

# Timeout for requests
TIMEOUT = 10

# Delay between requests 
DELAY = 3

# Maximum number of pages to scrape per category
MAX_PAGES = 50

OUTPUT_FILES = {
    "matches": "data/raw/matches.csv",
    "players": "data/raw/players.csv",
    "teams": "data/raw/teams.csv",
    "maps": "data/raw/maps.csv",
    "tournaments": "data/raw/tournaments.csv",
    "players_stats": "data/raw/players_stats.csv"
}
