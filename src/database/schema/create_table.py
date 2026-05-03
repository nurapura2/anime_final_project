from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Union


DB_PATH = Path(__file__).resolve().parents[1] / "db" / "anime_catalog.db"


def create_db(db_path: Union[str, Path] = DB_PATH):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executescript(
        """
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

        CREATE TABLE genres (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE);
        CREATE TABLE studios (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE);
        CREATE TABLE directors (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE);
        CREATE TABLE dubbing_groups (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE);

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

        CREATE TABLE anime_stats (
            anime_id INTEGER PRIMARY KEY,
            site_rating REAL,
            site_votes INTEGER,
            site_views INTEGER,
            FOREIGN KEY (anime_id) REFERENCES anime(anime_id) ON DELETE CASCADE
        );

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
        """
    )

    conn.commit()
    return conn, cursor


if __name__ == "__main__":
    conn, cursor = create_db()
    print("Database created successfully!")
    conn.close()
