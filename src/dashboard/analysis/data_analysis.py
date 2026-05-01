import pandas as pd
import sqlite3
import re

conn = sqlite3.connect(':memory:')
cursor = conn.cursor()


def run_query(title, description, sql):
    print(f"--- Query: {title} ---")
    print(f"Insight: {description}")
    df = pd.read_sql(sql, conn)
    print(df)
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

# Query 6: High-Rated Hidden Gems
run_query(
    "High-Rated Hidden Gems",
    "Finding high-rated anime with very few votes that deserve more attention from the community.",
    """
    SELECT a.title_ru, s.site_rating, s.site_votes 
    FROM anime a 
    JOIN anime_stats s ON a.anime_id = s.anime_id 
    WHERE s.site_rating > 8.0 AND s.site_votes < 50 
    ORDER BY s.site_rating DESC 
    LIMIT 10
    """
)

# Query 7: Source Material Influence
run_query(
    "Source Material Influence",
    "Comparing the average quality of anime based on their origin (manga, light novels, etc.).",
    """
    SELECT source, ROUND(AVG(site_rating), 2) as avg_rating, COUNT(*) as count 
    FROM anime a 
    JOIN anime_stats s ON a.anime_id = s.anime_id 
    GROUP BY source 
    HAVING count > 5 
    ORDER BY avg_rating DESC
    """
)

# Query 8: Genre Excellence
run_query(
    "Genre Excellence",
    "Top genres ranked by user ratings (minimum 10 titles per genre to ensure quality).",
    """
    SELECT g.name as genre, ROUND(AVG(s.site_rating), 2) as avg_rating 
    FROM genres g 
    JOIN anime_genres ag ON g.id = ag.genre_id 
    JOIN anime_stats s ON ag.anime_id = s.anime_id 
    GROUP BY g.name 
    HAVING COUNT(ag.anime_id) > 10 
    ORDER BY avg_rating DESC 
    LIMIT 10
    """
)

# Query 9: Industry Giants (Most Prolific Studios)
run_query(
    "Industry Giants",
    "Studios with the highest number of released projects, representing historical market dominance.",
    """
    SELECT st.name as studio, COUNT(ast.anime_id) as project_count 
    FROM studios st 
    JOIN anime_studios ast ON st.id = ast.studio_id 
    GROUP BY st.name 
    ORDER BY project_count DESC 
    LIMIT 10
    """
)

# Query 10: Director Engagement
run_query(
    "Director Engagement",
    "Identifying directors whose works generate the highest average user engagement (votes).",
    """
    SELECT d.name as director, ROUND(AVG(s.site_votes), 0) as avg_votes 
    FROM directors d 
    JOIN anime_directors ad ON d.id = ad.director_id 
    JOIN anime_stats s ON ad.anime_id = s.anime_id 
    GROUP BY d.name 
    HAVING COUNT(ad.anime_id) >= 3 
    ORDER BY avg_votes DESC 
    LIMIT 5
    """
)

# Query 11: Release Trends (Historical Growth)
run_query(
    "Release Trends",
    "Analyzing the volume of new anime releases over the last 15 years to track industry scaling.",
    """
    SELECT release_year, COUNT(*) as release_count 
    FROM anime 
    WHERE release_year BETWEEN 2009 AND 2024 
    GROUP BY release_year 
    ORDER BY release_year DESC
    """
)

# Query 12: Format Interaction Ratio
run_query(
    "Format Interaction Ratio",
    "Calculating the number of views per vote to see which formats (TV, ONA, Movie) drive more interaction.",
    """
    SELECT anime_type, ROUND(SUM(site_views)*1.0 / SUM(site_votes), 2) as views_per_vote 
    FROM anime a 
    JOIN anime_stats s ON a.anime_id = s.anime_id 
    GROUP BY anime_type 
    HAVING SUM(site_votes) > 0 
    ORDER BY views_per_vote DESC
    """
)

# Query 13: Forgotten Masterpieces
run_query(
    "Forgotten Masterpieces",
    "Discovering high-quality works (rating > 7.5) with extremely low view counts (under 500 views).",
    """
    SELECT a.title_ru, s.site_rating, s.site_views 
    FROM anime a 
    JOIN anime_stats s ON a.anime_id = s.anime_id 
    WHERE s.site_rating > 7.5 AND s.site_views < 500 AND s.site_views > 0 
    ORDER BY s.site_rating DESC 
    LIMIT 10
    """
)

# Query 14: Demographic Popularity
run_query(
    "Demographic Popularity",
    "Total view counts grouped by age rating to identify the most popular target demographics.",
    """
    SELECT age_rating, SUM(site_views) as total_views, COUNT(*) as title_count 
    FROM anime a 
    JOIN anime_stats s ON a.anime_id = s.anime_id 
    GROUP BY age_rating 
    ORDER BY total_views DESC
    """
)

# Query 15: Top Dubbing Groups
run_query(
    "Top Dubbing Groups",
    "Dubbing teams with the highest average project ratings (minimum 20 projects handled).",
    """
    SELECT dg.name as group_name, ROUND(AVG(s.site_rating), 2) as avg_rating, COUNT(*) as projects 
    FROM dubbing_groups dg 
    JOIN anime_dubbing_groups adg ON dg.id = adg.dubbing_group_id 
    JOIN anime_stats s ON adg.anime_id = s.anime_id 
    GROUP BY dg.name 
    HAVING projects > 20 
    ORDER BY avg_rating DESC 
    LIMIT 10
    """
)