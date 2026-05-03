from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Union

import pandas as pd


DB_PATH = Path(__file__).resolve().parents[1] / "db" / "anime_catalog.db"


QUERIES = [
    (
        "Distribution by Format",
        "Counts anime in each release format to understand catalog variety.",
        """
        SELECT anime_type, COUNT(*) AS total
        FROM anime
        GROUP BY anime_type
        ORDER BY total DESC
        """,
    ),
    (
        "Average Rating by Age Category",
        "Calculates average user rating by age rating.",
        """
        SELECT a.age_rating, ROUND(AVG(s.site_rating), 2) AS avg_score
        FROM anime a
        JOIN anime_stats s ON a.anime_id = s.anime_id
        WHERE a.age_rating NOT IN ('Unknown', 'N/A', 'Неизвестно')
        GROUP BY a.age_rating
        ORDER BY avg_score DESC
        """,
    ),
    (
        "Genre Popularity by Views",
        "Sums site views per genre through the junction table.",
        """
        SELECT g.name AS genre, SUM(s.site_views) AS total_views
        FROM genres g
        JOIN anime_genres ag ON g.id = ag.genre_id
        JOIN anime_stats s ON ag.anime_id = s.anime_id
        GROUP BY g.name
        ORDER BY total_views DESC
        LIMIT 10
        """,
    ),
    (
        "Most Anticipated Upcoming Releases",
        "Filters future projects and sorts them by user votes.",
        """
        SELECT a.title_ru, a.release_year, s.site_votes, a.status
        FROM anime a
        JOIN anime_stats s ON a.anime_id = s.anime_id
        WHERE a.release_year >= 2026
        ORDER BY s.site_votes DESC
        LIMIT 5
        """,
    ),
    (
        "Studio Reach and Efficiency",
        "Measures total views and project count per studio.",
        """
        SELECT st.name AS studio,
               COUNT(ast.anime_id) AS project_count,
               SUM(s.site_views) AS total_views
        FROM studios st
        JOIN anime_studios ast ON st.id = ast.studio_id
        JOIN anime_stats s ON ast.anime_id = s.anime_id
        GROUP BY st.name
        HAVING total_views > 0
        ORDER BY total_views DESC
        """,
    ),
    (
        "High-Rated Hidden Gems",
        "Finds high-rated anime with very few votes.",
        """
        SELECT a.title_ru, s.site_rating, s.site_votes
        FROM anime a
        JOIN anime_stats s ON a.anime_id = s.anime_id
        WHERE s.site_rating > 8.0 AND s.site_votes < 50
        ORDER BY s.site_rating DESC
        LIMIT 10
        """,
    ),
    (
        "Source Material Influence",
        "Compares average rating by source material.",
        """
        SELECT source, ROUND(AVG(site_rating), 2) AS avg_rating, COUNT(*) AS count
        FROM anime a
        JOIN anime_stats s ON a.anime_id = s.anime_id
        GROUP BY source
        HAVING count > 5
        ORDER BY avg_rating DESC
        """,
    ),
    (
        "Genre Excellence",
        "Ranks genres by user ratings with a minimum catalog size.",
        """
        SELECT g.name AS genre, ROUND(AVG(s.site_rating), 2) AS avg_rating
        FROM genres g
        JOIN anime_genres ag ON g.id = ag.genre_id
        JOIN anime_stats s ON ag.anime_id = s.anime_id
        GROUP BY g.name
        HAVING COUNT(ag.anime_id) > 10
        ORDER BY avg_rating DESC
        LIMIT 10
        """,
    ),
    (
        "Industry Giants",
        "Finds studios with the highest number of projects.",
        """
        SELECT st.name AS studio, COUNT(ast.anime_id) AS project_count
        FROM studios st
        JOIN anime_studios ast ON st.id = ast.studio_id
        GROUP BY st.name
        ORDER BY project_count DESC
        LIMIT 10
        """,
    ),
    (
        "Director Engagement",
        "Identifies directors with the highest average user votes.",
        """
        SELECT d.name AS director, ROUND(AVG(s.site_votes), 0) AS avg_votes
        FROM directors d
        JOIN anime_directors ad ON d.id = ad.director_id
        JOIN anime_stats s ON ad.anime_id = s.anime_id
        GROUP BY d.name
        HAVING COUNT(ad.anime_id) >= 3
        ORDER BY avg_votes DESC
        LIMIT 5
        """,
    ),
    (
        "Release Trends",
        "Tracks anime release volume over recent years.",
        """
        SELECT release_year, COUNT(*) AS release_count
        FROM anime
        WHERE release_year BETWEEN 2009 AND 2024
        GROUP BY release_year
        ORDER BY release_year DESC
        """,
    ),
    (
        "Format Interaction Ratio",
        "Calculates views per vote by release format.",
        """
        SELECT anime_type,
               ROUND(SUM(site_views) * 1.0 / SUM(site_votes), 2) AS views_per_vote
        FROM anime a
        JOIN anime_stats s ON a.anime_id = s.anime_id
        GROUP BY anime_type
        HAVING SUM(site_votes) > 0
        ORDER BY views_per_vote DESC
        """,
    ),
    (
        "Forgotten Masterpieces",
        "Finds high-rated works with low view counts.",
        """
        SELECT a.title_ru, s.site_rating, s.site_views
        FROM anime a
        JOIN anime_stats s ON a.anime_id = s.anime_id
        WHERE s.site_rating > 7.5 AND s.site_views < 500 AND s.site_views > 0
        ORDER BY s.site_rating DESC
        LIMIT 10
        """,
    ),
    (
        "Demographic Popularity",
        "Groups total view count by age rating.",
        """
        SELECT age_rating, SUM(site_views) AS total_views, COUNT(*) AS title_count
        FROM anime a
        JOIN anime_stats s ON a.anime_id = s.anime_id
        GROUP BY age_rating
        ORDER BY total_views DESC
        """,
    ),
    (
        "Top Dubbing Groups",
        "Ranks dubbing groups by average project rating.",
        """
        SELECT dg.name AS group_name,
               ROUND(AVG(s.site_rating), 2) AS avg_rating,
               COUNT(*) AS projects
        FROM dubbing_groups dg
        JOIN anime_dubbing_groups adg ON dg.id = adg.dubbing_group_id
        JOIN anime_stats s ON adg.anime_id = s.anime_id
        GROUP BY dg.name
        HAVING projects > 20
        ORDER BY avg_rating DESC
        LIMIT 10
        """,
    ),
]


def run_query(title: str, description: str, sql: str, conn: sqlite3.Connection) -> pd.DataFrame:
    print(f"--- Query: {title} ---")
    print(f"Insight: {description}")
    df = pd.read_sql(sql, conn)
    print(df)
    print()
    return df


def run_all_queries(db_path: Union[str, Path] = DB_PATH) -> list[pd.DataFrame]:
    db_path = Path(db_path)
    conn = sqlite3.connect(db_path)
    try:
        return [run_query(title, description, sql, conn) for title, description, sql in QUERIES]
    finally:
        conn.close()


if __name__ == "__main__":
    run_all_queries()
