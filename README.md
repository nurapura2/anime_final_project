# 🍜 YummyAnime Data Analysis Pipeline

<div align="center">

An End-to-End Data Pipeline to scrape, clean, store, analyze, and visualize anime data from [yummyani.me](https://yummyani.me).

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Cleaning-150458?style=flat-square&logo=pandas&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=flat-square&logo=sqlite&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/Web%20Scraping-BeautifulSoup-green?style=flat-square)
![Looker Studio](https://img.shields.io/badge/Looker%20Studio-Dashboard-4285F4?style=flat-square&logo=google&logoColor=white)
![Status](https://img.shields.io/badge/Status-Final%20Project-orange?style=flat-square)

</div>

---

## 📌 Project Overview

This repository contains the final project for the Data Analysis course. Our team built an End-to-End Data Pipeline to scrape, clean, store, analyze, and visualize anime data from [yummyani.me](https://yummyani.me).

The goal is to analyze trends in the anime industry — popularity by genre, release formats, age ratings, and more — using a full data analytics stack from raw web extraction to interactive BI dashboards.

---

## 📸 Screenshots

### Web Scraping in Action
<!-- TODO: Add screenshot of scraper running / raw CSV output -->
> *Screenshot coming soon*

### Database Schema
<!-- TODO: Add ER diagram or DB browser screenshot -->
> *Screenshot coming soon*

### Google Sheets Export
<!-- TODO: Add screenshot of the populated Google Sheet -->
> *Screenshot coming soon*

### Looker Studio Dashboard
<!-- TODO: Add screenshot of the dashboard -->
> *Screenshot coming soon*

---

## 🗂️ Data Dictionary

We collected a dataset of **10,142 records** containing the following attributes:

| Column | Description | Example |
|---|---|---|
| `title_ru` | Russian title of the anime | "Наруто" |
| `alt_names` | Alternative / original titles | "Naruto" |
| `anime_type` | Release format | TV Series, Movie, OVA, ONA |
| `status` | Current release status | Released, Ongoing, Announced |
| `release_year` | Year of broadcast | 2003 |
| `age_rating` | Recommended audience age | 16+, 18+, PG |
| `source` | Source material | Manga, Light Novel, Original |
| `site_rating` | User score on the platform | 8.4 |
| `site_votes` | Number of user votes | 12400 |
| `site_views` | Total views on the platform | 980000 |
| `genres` | Associated categories | Action, Drama, Fantasy |
| `studios` | Production studios | Bones, Madhouse |
| `directors` | Directors of the anime | Shinichiro Watanabe |
| `dubbing_groups` | Russian dubbing groups | AniLibria, 2x2 |

---

## 🛠️ Technology Stack

| Layer | Tools |
|---|---|
| Web Scraping | `Python`, `requests`, `BeautifulSoup4` |
| Data Preprocessing | `Pandas` |
| Database & Analysis | `SQLite3`, pure `SQL` |
| Integration & BI | `Google Sheets API`, `Looker Studio` |

---

## 🚀 Pipeline Stages

### 1. 🕷️ Web Scraping — `src/etl/extract.py`

- Extracts raw HTML using `requests`, parsed with `BeautifulSoup4`
- Handles pagination across all catalog pages
- Error handling for missing fields, timeouts, and failed requests
- Collects 10,142 records across 26 attributes
- Output → `data/raw/anime_catalog.csv`

### 2. 🧹 Data Preprocessing — `src/etl/transform.py`

- Handles missing values (fills with `None` / drops where critical)
- Removes duplicate entries
- Normalizes text: strips whitespace, consistent casing
- Converts `release_year`, `site_rating`, `site_votes`, `site_views` to numeric types
- Multi-value fields (`genres`, `studios`, etc.) split and normalized for relational storage
- Output → `data/processed/anime_catalog_clean.csv`

> Detailed before/after transformation logic is documented in the **Data Cleaning Passport** (`documentation/cleaning_passport.pdf`)

### 3. 🗄️ Database Management — `src/database/`

Connected to SQLite3 via Python. Schema uses **9 tables** across 3 layers:

**Reference Tables (Dictionaries)**
```
genres, studios, directors, dubbing_groups
```

**Main Table**
```
anime  →  anime_id, title_ru, alt_names, anime_type, status,
          release_year, age_rating, source, url
```

**Statistics Table (1:1 with anime)**
```
anime_stats  →  anime_id, site_rating, site_votes, site_views
```

**Junction Tables (Many-to-Many)**
```
anime_genres, anime_studios, anime_directors, anime_dubbing_groups
```

<details>
<summary>📄 View Full Schema (SQL)</summary>

```sql
-- Reference Tables
CREATE TABLE genres        (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE);
CREATE TABLE studios       (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE);
CREATE TABLE directors     (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE);
CREATE TABLE dubbing_groups(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE);

-- Main Anime Table
CREATE TABLE anime (
    anime_id     INTEGER PRIMARY KEY,
    title_ru     TEXT,
    alt_names    TEXT,
    anime_type   TEXT,
    status       TEXT,
    release_year INTEGER,
    age_rating   TEXT,
    source       TEXT,
    url          TEXT
);

-- Statistics Table (1:1 Relationship)
CREATE TABLE anime_stats (
    anime_id    INTEGER PRIMARY KEY,
    site_rating REAL,
    site_votes  INTEGER,
    site_views  INTEGER,
    FOREIGN KEY (anime_id) REFERENCES anime(anime_id) ON DELETE CASCADE
);

-- Junction Tables (Many-to-Many)
CREATE TABLE anime_genres (
    anime_id INTEGER, genre_id INTEGER,
    PRIMARY KEY (anime_id, genre_id),
    FOREIGN KEY (anime_id)  REFERENCES anime(anime_id),
    FOREIGN KEY (genre_id)  REFERENCES genres(id)
);

CREATE TABLE anime_studios (
    anime_id INTEGER, studio_id INTEGER,
    PRIMARY KEY (anime_id, studio_id),
    FOREIGN KEY (anime_id)  REFERENCES anime(anime_id),
    FOREIGN KEY (studio_id) REFERENCES studios(id)
);

CREATE TABLE anime_directors (
    anime_id INTEGER, director_id INTEGER,
    PRIMARY KEY (anime_id, director_id),
    FOREIGN KEY (anime_id)    REFERENCES anime(anime_id),
    FOREIGN KEY (director_id) REFERENCES directors(id)
);

CREATE TABLE anime_dubbing_groups (
    anime_id INTEGER, dubbing_group_id INTEGER,
    PRIMARY KEY (anime_id, dubbing_group_id),
    FOREIGN KEY (anime_id)         REFERENCES anime(anime_id),
    FOREIGN KEY (dubbing_group_id) REFERENCES dubbing_groups(id)
);
```

</details>

### 4. 📊 Data Analysis — `src/database/queries/`

Analytical questions answered with pure SQL. Example queries:

**Top 10 genres by average rating**
```sql
SELECT g.name AS genre,
       ROUND(AVG(s.site_rating), 2) AS avg_rating,
       COUNT(DISTINCT ag.anime_id)  AS total_anime
FROM genres g
JOIN anime_genres ag ON g.id = ag.genre_id
JOIN anime_stats  s  ON ag.anime_id = s.anime_id
WHERE s.site_rating IS NOT NULL
GROUP BY g.name
ORDER BY avg_rating DESC
LIMIT 10;
```

**Count of releases per year (trend)**
```sql
SELECT release_year,
       COUNT(*) AS releases
FROM anime
WHERE release_year IS NOT NULL
GROUP BY release_year
ORDER BY release_year;
```

**Distribution by anime type with average rating**
```sql
SELECT a.anime_type,
       COUNT(*)                     AS count,
       ROUND(AVG(s.site_rating), 2) AS avg_rating
FROM anime a
JOIN anime_stats s ON a.anime_id = s.anime_id
GROUP BY a.anime_type
ORDER BY count DESC;
```

**Top 10 most-viewed anime**
```sql
SELECT a.title_ru,
       a.release_year,
       s.site_views,
       s.site_rating
FROM anime a
JOIN anime_stats s ON a.anime_id = s.anime_id
ORDER BY s.site_views DESC
LIMIT 10;
```

**Most active dubbing groups by catalog volume**
```sql
SELECT d.name        AS dubbing_group,
       COUNT(*)      AS dubbed_titles
FROM dubbing_groups d
JOIN anime_dubbing_groups adg ON d.id = adg.dubbing_group_id
GROUP BY d.name
ORDER BY dubbed_titles DESC
LIMIT 10;
```

### 5. ☁️ Export & Visualization — `src/dashboard/`

- Cleaned data exported to **Google Sheets** via Google Sheets API
- **[📊 Google Sheets - Dataset](https://docs.google.com/spreadsheets/d/1wE2jzDtm50-0H0qlcDM1NiB9CExufcMk3x1ylPXYleY/edit?usp=sharing)**
- Interactive dashboard built in **Looker Studio** with bar charts, line charts, pie charts, and filter controls
- **[📈 Looker Studio Dashboard](#)** *(link coming soon)*

---

## 📂 Project Structure

```text
.
├── data/
│   ├── raw/                    # Raw scraped CSV  →  anime_catalog.csv
│   └── processed/              # Cleaned CSV      →  anime_catalog_clean.csv
│
├── documentation/
│   │
│   ├── cleaning_passport.pdf   # Before/after preprocessing log
│   └── schema_diagram.png      # ER diagram
│
├── notebooks/                  # Jupyter notebooks for EDA and testing
│
├── src/
│   │
│   ├── database/
│   │   ├── db/                 # DB format file
│   │   ├── diagrams/           # DB Diagrams
│   │   ├── queries/            # SQL analytical queries
│   │   └── schema/             # DB creation & schema
│   │
│   ├── etl/
│   │   ├── extract.py          # Web scraping script
│   │   ├── transform.py        # Data cleaning script
│   │   └── load.py             # Insert cleaned data into DB
│   │
│   ├── scrappers/              # Data scrappers scripts
│   ├── main.py                 # Run full ETL pipeline
│   └── config.py               # Project configurations
│
├── dashboard/                  # Google Sheets API upload
├── .env                        # API keys (not committed)
├── .gitignore                  
├── requirements.txt            
└── README.md
```

---

## ⚙️ Installation & Setup


```

---

## 👥 Team

| Name | Role |
|---|---|
| <Nurassyl> | Web Scraping & ETL |
| <Nurbolat> | Database & SQL Analysis |
| <Niyazbek> | Dashboard & Visualization |