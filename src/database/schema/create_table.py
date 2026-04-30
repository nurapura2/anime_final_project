import sqlite3
import os

# ==========================================
# DATABASE SETUP (SQLite)
# ==========================================
def create_db():
    # Создаём папку, если её нет
    os.makedirs('database/db', exist_ok=True)

    conn = sqlite3.connect('database/db/anime_catalog.db')
    cursor = conn.cursor()

    cursor.executescript("""
    -- Drop tables if they exist to allow recreation with new schema
    DROP TABLE IF EXISTS anime_genres;
    DROP TABLE IF EXISTS anime_studios;
    DROP TABLE IF EXISTS anime_directors;
    DROP TABLE IF EXISTS anime_dubbing_groups;
    DROP TABLE IF EXISTS anime_stats;
    DROP TABLE IF EXISTS anime;
    DROP TABLE IF EXISTS genres;
    DROP TABLE IF EXISTS studios;
    DROP TABLE IF EXISTS directors;
    DROP TABLE IF EXISTS dubbing_groups;

    -- 1. Reference Tables (Dictionaries)
    CREATE TABLE genres (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE);
    CREATE TABLE studios (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE);
    CREATE TABLE directors (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE);
    CREATE TABLE dubbing_groups (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE);

    -- 2. Main Anime Table
    CREATE TABLE anime (
        anime_id INTEGER PRIMARY KEY,
        title_ru TEXT,
        alt_names TEXT,
        anime_type TEXT,
        status TEXT,
        release_year INTEGER,
        age_rating TEXT,
        source TEXT,
        url TEXT
    );

    -- 3. Statistics Table (1:1 Relationship with Anime)
    CREATE TABLE anime_stats (
        anime_id INTEGER PRIMARY KEY,
        site_rating REAL,
        site_votes INTEGER,
        site_views INTEGER,
        FOREIGN KEY (anime_id) REFERENCES anime(anime_id) ON DELETE CASCADE
    );

    -- 4. Junction Tables (Many-to-Many Relationships)
    CREATE TABLE anime_genres (
        anime_id INTEGER,
        genre_id INTEGER,
        PRIMARY KEY (anime_id, genre_id),
        FOREIGN KEY (anime_id) REFERENCES anime(anime_id),
        FOREIGN KEY (genre_id) REFERENCES genres(id)
    );

    CREATE TABLE anime_studios (
        anime_id INTEGER,
        studio_id INTEGER,
        PRIMARY KEY (anime_id, studio_id),
        FOREIGN KEY (anime_id) REFERENCES anime(anime_id),
        FOREIGN KEY (studio_id) REFERENCES studios(id)
    );

    CREATE TABLE anime_directors (
        anime_id INTEGER,
        director_id INTEGER,
        PRIMARY KEY (anime_id, director_id),
        FOREIGN KEY (anime_id) REFERENCES anime(anime_id),
        FOREIGN KEY (director_id) REFERENCES directors(id)
    );

    CREATE TABLE anime_dubbing_groups (
        anime_id INTEGER,
        dubbing_group_id INTEGER,
        PRIMARY KEY (anime_id, dubbing_group_id),
        FOREIGN KEY (anime_id) REFERENCES anime(anime_id),
        FOREIGN KEY (dubbing_group_id) REFERENCES dubbing_groups(id)
    );
    """)

    conn.commit()
    return conn, cursor


# Пример использования
if __name__ == "__main__":
    conn, cursor = create_db()
    print("Database created successfully!")
    conn.close()