import sqlite3

# ==========================================
# 2. DATABASE SETUP (SQLite in-memory)
# ==========================================
def create_db():
   conn = sqlite3.connect('database\\db\\anime_catalog.db')
   cursor = conn.cursor()

# Creating tables according to relational schema (Many-to-Many logic)
   cursor.executescript("""
-- 1. Reference Tables (Dictionaries)
CREATE TABLE genres (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE);
CREATE TABLE studios (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE);
CREATE TABLE directors (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE);
CREATE TABLE dubbing_groups (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE);

-- 2. Main Anime Table
CREATE TABLE anime (
    anime_id INT PRIMARY KEY, 
    title_ru TEXT, 
    alt_names TEXT, 
    anime_type TEXT, 
    status TEXT, 
    release_year INT, 
    age_rating TEXT, 
    source TEXT, 
    url TEXT
);

-- 3. Statistics Table (1:1 Relationship with Anime)
CREATE TABLE anime_stats (
    anime_id INT PRIMARY KEY REFERENCES anime(anime_id) ON DELETE CASCADE,
    site_rating DECIMAL, 
    site_votes INT, 
    site_views INT,
    shikimori_rating DECIMAL, 
    mal_rating DECIMAL, 
    kinopoisk_rating DECIMAL,
    comments_count INT, 
    reviews_count INT
);

-- 4. Junction Tables (Many-to-Many Relationships)
CREATE TABLE anime_genres (
    anime_id INT REFERENCES anime(anime_id), 
    genre_id INT REFERENCES genres(id),
    PRIMARY KEY (anime_id, genre_id)
);
CREATE TABLE anime_studios (
    anime_id INT REFERENCES anime(anime_id), 
    studio_id INT REFERENCES studios(id),
    PRIMARY KEY (anime_id, studio_id)
);
CREATE TABLE anime_directors (
    anime_id INT REFERENCES anime(anime_id), 
    director_id INT REFERENCES directors(id),
    PRIMARY KEY (anime_id, director_id)
);
""")
   
   return conn, cursor
