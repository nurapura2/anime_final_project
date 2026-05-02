import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
import src.config as config

import requests
from bs4 import BeautifulSoup
import time
import random
import re
import pandas as pd


# ── Session setup ─────────────────────────────────────────────────────────────

base_url    = config.BASE_URL
catalog_url = config.CATALOG_URL
max_pages   = config.MAX_PAGES  # None = all pages, integer = limit

session = requests.Session()
session.headers.update(config.HEADERS)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sleep(delay_range):
    """Sleep for a random duration within the given (min, max) range."""
    time.sleep(random.uniform(*delay_range))


def fetch(url, retries=3):
    """
    Fetch a URL with retry logic.
    Backs off on 429/503 errors and request exceptions.
    Returns a Response object or None on failure.
    """
    for attempt in range(retries):
        try:
            response = session.get(url, timeout=config.TIMEOUT)

            if response.status_code in (429, 503):
                # Exponential-style back-off on rate limit / service unavailable
                _sleep((
                    config.DELAY_ERR[0] * (attempt + 1),
                    config.DELAY_ERR[1] * (attempt + 1),
                ))
                print(f"[fetch] HTTP {response.status_code} — retrying ({attempt + 1}/{retries})")
                continue

            if response.status_code != 200:
                print(f"[fetch] Unexpected status {response.status_code} for {url}")
                return None

            return response

        except requests.RequestException as e:
            print(f"[fetch] Request error: {e} — retrying ({attempt + 1}/{retries})")
            _sleep((
                config.DELAY_ERR[0] * (attempt + 1),
                config.DELAY_ERR[1] * (attempt + 1),
            ))

    print(f"[fetch] All retries exhausted for {url}")
    return None


# ── Main scraper ──────────────────────────────────────────────────────────────

def run():

    # ── 1. Determine total number of catalog pages ────────────────────────────

    response = fetch(catalog_url)
    if not response:
        print("[run] Failed to load catalog — aborting")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    last_page  = 1
    pagination = soup.find("ul", class_="pagination")
    if pagination:
        for a in pagination.find_all("a"):
            txt = a.get_text(strip=True)
            if txt.isdigit():
                last_page = max(last_page, int(txt))

    if max_pages:
        last_page = min(last_page, max_pages)

    print(f"[run] Total pages to scrape: {last_page}")


    # ── 2. Collect anime links from all catalog pages ─────────────────────────

    anime_links = []

    for page_num in range(1, last_page + 1):

        if page_num == 1:
            # Reuse already-fetched first page
            page_soup = soup
        else:
            url = f"{catalog_url}?page={page_num}"
            print(f"[catalog] Page {page_num}/{last_page}: {url}")
            response = fetch(url)
            if not response:
                continue
            page_soup = BeautifulSoup(response.text, "html.parser")
            _sleep(config.DELAY)  # polite delay between catalog pages

        for block in page_soup.find_all("div", class_="anime-column-info"):
            a_tag = block.find("a", class_="anime-title")
            if not a_tag:
                continue
            href = a_tag.get("href", "")
            if href:
                anime_links.append(base_url + href)

    # Remove duplicates while preserving order
    anime_links = list(dict.fromkeys(anime_links))
    print(f"[run] Unique anime found: {len(anime_links)}")


    # ── 3. Scrape each anime detail page ──────────────────────────────────────

    all_anime = []

    for i, link in enumerate(anime_links, 1):

        # Checkpoint: save progress every 100 entries and take a longer break
        if i % 100 == 0:
            _sleep(config.DELAY_LONG)
            checkpoint_df = pd.DataFrame(all_anime)
            checkpoint_df.to_csv(
                f"data/raw/anime_checkpoint_{i}.csv",
                index=False,
                encoding="utf-8-sig",
            )
            print(f"[checkpoint] Saved {i} entries")

        _sleep(config.DELAY)  # polite delay between anime pages

        response = fetch(link)
        if not response:
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # ── Title ─────────────────────────────────────────────────────────────
        titles_div = soup.find("div", class_="titles")
        h1         = titles_div.find("h1", itemprop="name") if titles_div else None
        title_ru   = h1.get_text(strip=True) if h1 else "N/A"

        # ── Alternative titles ────────────────────────────────────────────────
        alt_names = []
        alt_block = soup.find("ul", class_="alt-names-list")
        if alt_block:
            for li in alt_block.find_all("li"):
                classes = li.get("class", [])
                if "more-alt-names" not in classes:
                    t = li.get_text(strip=True)
                    if t and t != "…":
                        alt_names.append(t)

        # ── Site rating ───────────────────────────────────────────────────────
        anime_id    = "N/A"
        site_rating = "N/A"
        site_votes  = "N/A"
        site_views  = "N/A"

        rating_block = soup.find("div", class_="rating-info")
        if rating_block:
            anime_id     = rating_block.get("data-id", "N/A")
            main_r       = rating_block.find("span", class_="main-rating")
            site_rating  = main_r.get_text(strip=True) if main_r else "N/A"
            rating_info  = rating_block.find("span", class_="main-rating-info")
            votes_span   = rating_info.find("span") if rating_info else None
            site_votes   = votes_span.get_text(strip=True) if votes_span else "N/A"
            viewers_span = rating_block.find("span", class_="viewers-info")
            if viewers_span:
                site_views = re.sub(r"\s+", " ", viewers_span.get_text(strip=True))

        # ── Characteristics ───────────────────────────────────────────────────
        status     = "N/A"
        anime_type = "N/A"
        year       = "N/A"
        age_rating = "N/A"
        genres     = []
        source     = "N/A"
        studio     = []
        director   = []
        dubbing    = []

        info_ul = soup.find("ul", class_="content-main-info")
        if info_ul:
            for li in info_ul.find_all("li", recursive=False):
                span = li.find("span")
                if not span:
                    continue
                label = span.get_text(strip=True).rstrip(":").lower()
                div   = li.find("div")

                if "статус" in label:
                    a      = div.find("a") if div else None
                    status = a.get_text(strip=True) if a else (div.get_text(strip=True) if div else "N/A")

                elif "тип" in label:
                    anime_type = div.get_text(strip=True) if div else "N/A"

                elif "год выхода" in label:
                    a    = div.find("a") if div else None
                    year = a.get_text(strip=True) if a else "N/A"

                elif "возрастной" in label:
                    a          = div.find("a") if div else None
                    age_rating = a.get_text(strip=True) if a else "N/A"

                elif "жанр" in label:
                    genres_ul = li.find("ul")
                    if genres_ul:
                        genres = [a.get_text(strip=True) for a in genres_ul.find_all("a")]

                elif "первоисточник" in label:
                    source = div.get_text(strip=True) if div else "N/A"

                elif "студия" in label:
                    studio_ul = li.find("ul")
                    if studio_ul:
                        studio = [a.get_text(strip=True) for a in studio_ul.find_all("a")]

                elif "режиссер" in label:
                    director_ul = li.find("ul")
                    if director_ul:
                        director = [a.get_text(strip=True) for a in director_ul.find_all("a")]

                elif "озвучка" in label:
                    voices_ul = li.find("ul", class_="animeVoices")
                    if voices_ul:
                        dubbing = [a.get_text(strip=True) for a in voices_ul.find_all("a")]

        # ── External ratings ──────────────────────────────────────────────────
        shikimori_rating = "N/A"
        shikimori_url    = "N/A"
        worldart_rating  = "N/A"
        worldart_url     = "N/A"
        kinopoisk_rating = "N/A"
        kinopoisk_url    = "N/A"
        mal_rating       = "N/A"
        mal_url          = "N/A"

        ref_block = soup.find("div", class_="content-ref-ids")
        if ref_block:
            for a in ref_block.find_all("a"):
                label_attr = (a.get("aria-label") or a.get("data-balloon") or "").lower()
                href       = a.get("href", "")
                span       = a.find("span")
                rating     = span.get_text(strip=True) if span else "N/A"

                if "shikimori" in label_attr:
                    shikimori_rating = rating
                    shikimori_url    = href
                elif "worldart" in label_attr:
                    worldart_rating  = rating
                    worldart_url     = href
                elif "кинопоиск" in label_attr or "kinopoisk" in label_attr:
                    kinopoisk_rating = rating
                    kinopoisk_url    = href
                elif "myanime" in label_attr or "mal" in label_attr:
                    mal_rating       = rating
                    mal_url          = href

        # ── Comments / reviews ────────────────────────────────────────────────
        comments_count = "N/A"
        reviews_count  = "N/A"

        tabs_ul = soup.find("ul", class_="tabs")
        if tabs_ul:
            for tab_li in tabs_ul.find_all("li", class_="tabs-li"):
                title_span = tab_li.find("span", class_="title")
                count_span = tab_li.find("span", class_="count")
                if not title_span:
                    continue
                tab_title = title_span.get_text(strip=True).lower()
                count     = count_span.get_text(strip=True) if count_span else "N/A"
                if "коммент" in tab_title:
                    comments_count = count
                elif "рецен" in tab_title:
                    reviews_count  = count

        print(f"[{i}/{len(anime_links)}] {title_ru} | {anime_type} | {year} | {site_rating} | {link}")

        all_anime.append({
            "title_ru":         title_ru,
            "alt_names":        " | ".join(alt_names),
            "anime_id":         anime_id,
            "status":           status,
            "type":             anime_type,
            "year":             year,
            "age_rating":       age_rating,
            "genres":           " | ".join(genres),
            "source":           source,
            "studio":           " | ".join(studio),
            "director":         " | ".join(director),
            "dubbing":          " | ".join(dubbing),
            "site_rating":      site_rating,
            "site_votes":       site_votes,
            "site_views":       site_views,
            "shikimori_rating": shikimori_rating,
            "shikimori_url":    shikimori_url,
            "worldart_rating":  worldart_rating,
            "worldart_url":     worldart_url,
            "kinopoisk_rating": kinopoisk_rating,
            "kinopoisk_url":    kinopoisk_url,
            "mal_rating":       mal_rating,
            "mal_url":          mal_url,
            "comments_count":   comments_count,
            "reviews_count":    reviews_count,
            "url":              link,
        })


    # ── 4. Save final CSV ─────────────────────────────────────────────────────

    if all_anime:
        df = pd.DataFrame(all_anime)
        df.to_csv("data/raw/anime_catalog.csv", index=False, encoding="utf-8-sig")
        print("[run] Saved: data/raw/anime_catalog.csv")

    print(f"[run] Total anime scraped: {len(all_anime)}")


if __name__ == "__main__":
    run()