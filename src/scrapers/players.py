#libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random


url = 'https://liquipedia.net/counterstrike/Portal:Players/Europe'

headers = {
    "User-Agent": "CSPlayersParser/1.0 (contact: your_email@example.com)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}
session = requests.Session()
session.headers.update(headers)

def fetch(url, retries=3):
    for attempt in range(retries):
        try:
            response = session.get(url, timeout=15)

            if response.status_code in (429, 503):
                time.sleep(random.uniform(5, 15) * (attempt + 1))
                continue

            if response.status_code != 200:
                return None

            return response

        except requests.RequestException:
            time.sleep(random.uniform(5, 15) * (attempt + 1))

    return None


response = fetch(url)
if not response:
    exit()
soup = BeautifulSoup(response.text, "html.parser")

country_links = []

country_links.append(url)

tabs = soup.find("ul", class_="tabs9")
if tabs:
    for a in tabs.find_all("a", href=True):
        href = a["href"]
        if "/counterstrike/Portal:Players" in href:
            full_link = f"https://liquipedia.net{href}"
            country_links.append(full_link)

country_links = list(set(country_links))
print(country_links)

all_players = []
i = 0

for country_url in country_links:

    time.sleep(random.uniform(1, 3))
    
    response = fetch(country_url)
    if not response:
        continue
    soup = BeautifulSoup(response.text, "html.parser")

    players_links = []
    tables = soup.find_all("table", class_="wikitable")

    for table in tables:
        for tr in table.find_all("tr"):
            td = tr.find("td")
            if not td:
                continue

            links = td.find_all("a", href=True)

            if not links:
                continue

            player = links[0]
            name = player.text.strip()
            link = player["href"]

            if link.startswith("/counterstrike/"):
                players_links.append(f'https://liquipedia.net{link}')

    players_links = list(set(players_links))
    print(players_links)

    for link in players_links:
        try:
            i += 1
            if i % 100 == 0:
                time.sleep(random.uniform(50, 100))
                df = pd.DataFrame(all_players)
                df.to_csv(f"cs_players_{i}.csv", index=False, encoding="utf-8-sig")
                print(df.head())

            time.sleep(random.uniform(1, 3))
            
            response = fetch(link)
            if not response:
                continue
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, "html.parser")

            name_tag = soup.find("div", class_="infobox-description", string="Name:")
            if name_tag:
                value_tag = name_tag.find_next_sibling("div")
                name = value_tag.text.strip() if value_tag else "N/A"
            else:
                name = "N/A"

            flag_div = soup.find("span", class_="flag")
            if flag_div:
                parent = flag_div.find_parent("div")
                country_tag = parent.find_all("a")[-1]
                nationality = country_tag.text.strip()
            else:
                nationality = "N/A"

            status_tag = soup.find("div", class_="infobox-description", string="Status:")
            if status_tag:
                value_tag = status_tag.find_next_sibling("div")
                status = value_tag.text.strip() if value_tag else "N/A"
            else:
                status = "N/A"

            years_tag = soup.find("div", class_="infobox-description", string="Years Active (Player):")
            if years_tag:
                value_tag = years_tag.find_next_sibling("div")
                years_active = value_tag.text.strip() if value_tag else "N/A"
            else:
                years_active = "N/A"

            coach_years_tag = soup.find("div", class_="infobox-description", string="Years Active (Coach):")
            if coach_years_tag:
                value_tag = coach_years_tag.find_next_sibling("div")
                coach_years_active = value_tag.text.strip() if value_tag else "N/A"
            else:
                coach_years_active = "N/A"

            role_tag = soup.find("div", class_="infobox-description", string="Role:")
            if role_tag:
                value_tag = role_tag.find_next_sibling("div")
                role = value_tag.text.strip() if value_tag else "N/A"
            else:
                role = "N/A"

            team_tag = soup.find("div", class_="infobox-description", string="Team:")
            if team_tag:
                value_tag = team_tag.find_next_sibling("div")
                team = value_tag.text.strip() if value_tag else "N/A"
            else:
                team = "N/A"

            alt_ids_tag = soup.find("div", class_="infobox-description", string="Alternate IDs:")
            if alt_ids_tag:
                value_tag = alt_ids_tag.find_next_sibling("div")
                alternate_ids = value_tag.text.strip() if value_tag else "N/A"
            else:
                alternate_ids = "N/A"

            winnings_tag = soup.find("div", class_="infobox-description", string="Approx. Total Winnings:")
            if winnings_tag:
                value_tag = winnings_tag.find_next_sibling("div")
                total_winnings = value_tag.text.strip() if value_tag else "N/A"
            else:
                total_winnings = "N/A"

            print(f"{name} | {nationality} | {status} | {coach_years_active} | {years_active} | {role} | {team} | {alternate_ids} | {total_winnings}")

            all_players.append({
                "Name":                  name,
                "Nationality":           nationality,
                "Status":                status,
                "Years Active (Player)": years_active,
                "Years Active (Coach)":  coach_years_active,
                "Role":                  role,
                "Team":                  team,
                "Alternate IDs":         alternate_ids,
                "Total Winnings":        total_winnings,
                "Profile URL":           link
            })
        except Exception as e:
            print("Error:", e)
            continue


df = pd.DataFrame(all_players)
df.to_csv("cs_players.csv", index=False, encoding="utf-8-sig")

print(f"{len(df)}")
print(df.head())