import pandas as pd
import sqlite3
import re

conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

def run_query(title, description, sql):
    print(f"--- Query: {title} ---")
    print(f"Insight: {description}")
    print(pd.read_sql(sql, conn))
    print("\n")

# Query 1: COUNT + GROUP BY + ORDER BY
run_query(
    "Distribution by Format",
    "Counts the number of anime in each category (ONA, TV, Movie) to understand catalog variety.",
    "SELECT anime_type, COUNT(*) as total FROM anime GROUP BY anime_type ORDER BY total DESC"
)

# Query 2: AVG + JOIN + GROUP BY
run_query(
    "Average Rating by Age Category",
    "Calculates the average user rating for different age ratings to see target audience satisfaction.",
    """
    SELECT a.age_rating, ROUND(AVG(s.site_rating), 2) as avg_score
    FROM anime a
    JOIN anime_stats s ON a.anime_id = s.anime_id
    WHERE a.age_rating != 'Unknown' AND a.age_rating != 'Неизвестно'
    GROUP BY a.age_rating
    ORDER BY avg_score DESC
    """
)

# Query 3: SUM + JOIN + GROUP BY
run_query(
    "Genre Popularity by Views",
    "Sum of site views per genre, calculated through the junction table.",
    """
    SELECT g.name as genre, SUM(s.site_views) as total_views
    FROM genres g
    JOIN anime_genres ag ON g.id = ag.genre_id
    JOIN anime_stats s ON ag.anime_id = s.anime_id
    GROUP BY g.name
    ORDER BY total_views DESC
    LIMIT 10
    """
)

# Query 4: WHERE + ORDER BY (Filtering)
run_query(
    "Most Anticipated Upcoming Releases (2026-2027)",
    "Filters future projects and sorts them by user votes/interest.",
    """
    SELECT a.title_ru, a.release_year, s.site_votes, a.status
    FROM anime a
    JOIN anime_stats s ON a.anime_id = s.anime_id
    WHERE a.release_year >= 2026
    ORDER BY s.site_votes DESC
    LIMIT 5
    """
)

# Query 5: Complex JOIN (Studio Performance)
run_query(
    "Studio Reach and Efficiency",
    "Total view count and project count per studio to measure market presence.",
    """
    SELECT st.name as studio, COUNT(ast.anime_id) as project_count, SUM(s.site_views) as total_views
    FROM studios st
    JOIN anime_studios ast ON st.id = ast.studio_id
    JOIN anime_stats s ON ast.anime_id = s.anime_id
    GROUP BY st.name
    HAVING total_views > 0
    ORDER BY total_views DESC
    """
)