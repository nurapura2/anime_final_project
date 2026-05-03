from __future__ import annotations

import ast
import re
import sqlite3
from pathlib import Path
from typing import Union

import pandas as pd


DB_PATH = Path(__file__).resolve().parents[1] / "database" / "db" / "anime_catalog.db"


def is_missing(val) -> bool:
    if val is None:
        return True
    if isinstance(val, str):
        return val.strip() in {"", "N/A", "nan", "None"}
    try:
        return bool(pd.isna(val))
    except (TypeError, ValueError):
        return False


def to_int(val):
    if is_missing(val):
        return 0
    num = re.sub(r"\D", "", str(val))
    return int(num) if num else 0


def to_float(val):
    if is_missing(val):
        return 0.0
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def parse_list(val):
    """Convert list-like CSV values into a clean Python list."""
    if isinstance(val, (list, tuple, set)):
        return [str(item).strip() for item in val if not is_missing(item)]
    if is_missing(val):
        return []

    val_str = str(val).strip()
    if val_str.startswith("[") and val_str.endswith("]"):
        try:
            parsed = ast.literal_eval(val_str)
            if isinstance(parsed, (list, tuple, set)):
                return [str(item).strip() for item in parsed if not is_missing(item)]
        except (SyntaxError, ValueError):
            pass

    return [item.strip() for item in val_str.split("|") if item.strip()]


def to_text(val) -> str:
    items = parse_list(val)
    if items:
        return " | ".join(items)
    return "" if is_missing(val) else str(val).strip()


def first_existing(row, *names, default=None):
    for name in names:
        if name in row:
            value = row.get(name)
            if not is_missing(value):
                return value
    return default


def link_entity(cursor, anime_id, column_val, table_name, link_table, link_col_name):
    for name in parse_list(column_val):
        cursor.execute(f"INSERT OR IGNORE INTO {table_name} (name) VALUES (?)", (name,))
        cursor.execute(f"SELECT id FROM {table_name} WHERE name = ?", (name,))
        result = cursor.fetchone()
        if result:
            entity_id = result[0]
            cursor.execute(
                f"""
                INSERT OR IGNORE INTO {link_table} (anime_id, {link_col_name})
                VALUES (?, ?)
                """,
                (anime_id, entity_id),
            )


def insert_data(df, db_path: Union[str, Path] = DB_PATH) -> int:
    """Insert a cleaned anime dataframe into the normalized SQLite schema."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    inserted = 0
    for _, row in df.iterrows():
        anime_id = to_int(first_existing(row, "anime_id"))
        if not anime_id:
            continue

        year_value = first_existing(row, "year", "release_year")
        year_match = re.search(r"(\d{4})", str(year_value or ""))
        year = int(year_match.group(1)) if year_match else None

        cursor.execute(
            """
            INSERT OR REPLACE INTO anime (
                anime_id, title_ru, alt_names, anime_type, status,
                release_year, age_rating, source, url
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                anime_id,
                to_text(first_existing(row, "title_ru")),
                to_text(first_existing(row, "alt_names")),
                to_text(first_existing(row, "type", "anime_type")),
                to_text(first_existing(row, "status")),
                year,
                to_text(first_existing(row, "age_rating")),
                to_text(first_existing(row, "source")),
                to_text(first_existing(row, "url")),
            ),
        )

        cursor.execute(
            """
            INSERT OR REPLACE INTO anime_stats (
                anime_id, site_rating, site_votes, site_views
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                anime_id,
                to_float(first_existing(row, "site_rating")),
                to_int(first_existing(row, "site_votes")),
                to_int(first_existing(row, "site_views")),
            ),
        )

        link_entity(
            cursor,
            anime_id,
            first_existing(row, "genres", "genre"),
            "genres",
            "anime_genres",
            "genre_id",
        )
        link_entity(
            cursor,
            anime_id,
            first_existing(row, "studios", "studio"),
            "studios",
            "anime_studios",
            "studio_id",
        )
        link_entity(
            cursor,
            anime_id,
            first_existing(row, "directors", "director"),
            "directors",
            "anime_directors",
            "director_id",
        )
        link_entity(
            cursor,
            anime_id,
            first_existing(row, "dubbing_groups", "dubbing"),
            "dubbing_groups",
            "anime_dubbing_groups",
            "dubbing_group_id",
        )
        inserted += 1

    conn.commit()
    conn.close()
    print("Data loading completed.")
    return inserted
