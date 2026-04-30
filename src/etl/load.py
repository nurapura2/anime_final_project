import pandas as pd
import re
import sqlite3
import ast

conn = sqlite3.connect('database/db/anime_catalog.db')
cursor = conn.cursor()

def to_int(val):
    if pd.isna(val) or val == 'N/A': return 0
    num = re.sub(r'\D', '', str(val))
    return int(num) if num else 0

def to_float(val):
    if pd.isna(val) or val == 'N/A': return 0.0
    try: return float(val)
    except: return 0.0

def parse_list(val):
    """Превращает строку-список или строку с разделителем в реальный список"""
    if pd.isna(val) or val == 'N/A': return []
    if isinstance(val, list): return val
    val_str = str(val).strip()
    # Если строка выглядит как список Python: ['A', 'B']
    if val_str.startswith('[') and val_str.endswith(']'):
        try: return ast.literal_eval(val_str)
        except: pass
    # Если строка с разделителем: A | B
    return [e.strip() for e in val_str.split('|') if e.strip()]

def link_entity(cursor, anime_id, column_val, table_name, link_table, link_col_name):
    entities = parse_list(column_val)
    for name in entities:
        cursor.execute(f"INSERT OR IGNORE INTO {table_name} (name) VALUES (?)", (name,))
        cursor.execute(f"SELECT id FROM {table_name} WHERE name = ?", (name,))
        result = cursor.fetchone()
        if result:
            entity_id = result[0]
            cursor.execute(f"INSERT OR IGNORE INTO {link_table} (anime_id, {link_col_name}) VALUES (?, ?)", (anime_id, entity_id))

def insert_data(df):
    conn = sqlite3.connect('database/db/anime_catalog.db')
    cursor = conn.cursor()
    
    for _, row in df.iterrows():
        # Извлекаем год
        year_match = re.search(r'(\d{4})', str(row.get('year', '')))
        year = int(year_match.group(1)) if year_match else None
        
        # 1. Основная таблица
        cursor.execute("""
            INSERT OR REPLACE INTO anime (anime_id, title_ru, alt_names, anime_type, status, release_year, age_rating, source, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (row['anime_id'], row['title_ru'], row['alt_names'], row['type'], row['status'], year, row['age_rating'], row['source'], row['url']))
        
        # 2. Таблица статистики (теперь колонок столько же, сколько в create_table)
        cursor.execute("""
            INSERT OR REPLACE INTO anime_stats (anime_id, site_rating, site_votes, site_views, shikimori_rating, mal_rating, kinopoisk_rating, comments_count, reviews_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (row['anime_id'], to_float(row['site_rating']), to_int(row['site_votes']), to_int(row['site_views']), 
              to_float(row['shikimori_rating']), to_float(row['mal_rating']), to_float(row['kinopoisk_rating']),
              to_int(row['comments_count']), to_int(row['reviews_count'])))
        
        # 3. Связи (обработка разных имен колонок в CSV)
        link_entity(cursor, row['anime_id'], row.get('genres', row.get('genre')), 'genres', 'anime_genres', 'genre_id')
        link_entity(cursor, row['anime_id'], row.get('studios', row.get('studio')), 'studios', 'anime_studios', 'studio_id')
        link_entity(cursor, row['anime_id'], row.get('directors', row.get('director')), 'directors', 'anime_directors', 'director_id')
        link_entity(cursor, row['anime_id'], row.get('dubbing', row.get('dubbing_groups')), 'dubbing_groups', 'anime_dubbing_groups', 'dubbing_group_id')
        
    conn.commit()
    conn.close()
    print("Data loading completed.")

