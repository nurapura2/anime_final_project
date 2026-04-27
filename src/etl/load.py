import pandas as pd
import re
import sqlite3

conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

def to_int(val):
    if pd.isna(val) or val == 'N/A': return 0
    num = re.sub(r'\D', '', str(val))
    return int(num) if num else 0

def to_float(val):
    if pd.isna(val) or val == 'N/A': return 0.0
    try: return float(val)
    except: return 0.0

def link_entity(anime_id, column_val, table_name, link_table, link_col_name):
    """Helper function to populate dictionaries and link tables"""
    if pd.isna(column_val) or column_val == 'N/A': return
    # Splitting string if multiple values exist (separated by |)
    entities = [e.strip() for e in str(column_val).split('|')]
    for name in entities:
        cursor.execute(f"INSERT OR IGNORE INTO {table_name} (name) VALUES (?)", (name,))
        entity_id = cursor.execute(f"SELECT id FROM {table_name} WHERE name = ?", (name,)).fetchone()[0]
        cursor.execute(f"INSERT OR IGNORE INTO {link_table} (anime_id, {link_col_name}) VALUES (?, ?)", (anime_id, entity_id))

def insert_data(raw_df):
    # Populating the database
    for _, row in raw_df.iterrows():
        # 1. Extract Year
        year_match = re.search(r'(\d{4})', str(row['year']))
        year = int(year_match.group(1)) if year_match else None
        
        # 2. Insert into 'anime' table
        cursor.execute("""
            INSERT INTO anime (anime_id, title_ru, alt_names, anime_type, status, release_year, age_rating, source, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (row['anime_id'], row['title_ru'], row['alt_names'], row['type'], row['status'], year, row['age_rating'], row['source'], row['url']))
        
        # 3. Insert into 'anime_stats' table
        cursor.execute("""
            INSERT INTO anime_stats (anime_id, site_rating, site_votes, site_views, shikimori_rating, mal_rating, kinopoisk_rating, comments_count, reviews_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (row['anime_id'], to_float(row['site_rating']), row['site_votes'], to_int(row['site_views']), 
              to_float(row['shikimori_rating']), to_float(row['mal_rating']), to_float(row['kinopoisk_rating']),
              to_int(row['comments_count']), to_int(row['reviews_count'])))
        
        # 4. Insert Junctions (Many-to-Many)
        link_entity(row['anime_id'], row['genres'], 'genres', 'anime_genres', 'genre_id')
        link_entity(row['anime_id'], row['studio'], 'studios', 'anime_studios', 'studio_id')
        link_entity(row['anime_id'], row['director'], 'directors', 'anime_directors', 'director_id')

    conn.commit()
    print("Success: Data migrated to relational structure.")