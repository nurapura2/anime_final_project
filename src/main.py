"""
Project entry point for the anime scraping, ETL, database, and analysis flow.
"""

from __future__ import annotations

import argparse
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Union


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
RAW_CSV = PROJECT_ROOT / "data" / "raw" / "anime_catalog.csv"
CLEAN_CSV = PROJECT_ROOT / "data" / "processed" / "anime_catalog_clean.csv"
DB_PATH = SRC_DIR / "database" / "db" / "anime_catalog.db"


def add_import_paths() -> None:
    """Make both project root and src importable from any working directory."""
    for path in (PROJECT_ROOT, SRC_DIR):
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)


@contextmanager
def working_directory(path: Path):
    """Temporarily run code from a predictable working directory."""
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def resolve_project_path(path: Union[str, Path]) -> Path:
    """Resolve relative CLI paths from the project root."""
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def require_file(path: Path, step_name: str) -> None:
    if not path.exists():
        raise FileNotFoundError(
            f"{step_name} needs this file, but it was not found: {path}"
        )


def print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def print_step(number: int, total: int, title: str) -> None:
    print(f"\n[{number}/{total}] {title}")


def scrape_only() -> None:
    """Scrape anime catalog pages into data/raw/anime_catalog.csv."""
    add_import_paths()
    from scrappers.scrapper import run as scrape_anime_catalog

    print_header("SCRAPING ANIME CATALOG")
    with working_directory(PROJECT_ROOT):
        scrape_anime_catalog()


def extract_data(path: Path = RAW_CSV):
    """Read a CSV file through the project extract layer."""
    add_import_paths()
    from etl.extract import extract_csv

    require_file(path, "Extract")
    df = extract_csv(path)
    print(f"Loaded {len(df)} rows from {path}")
    return df


def get_raw_data():
    """Return the raw scraped dataframe."""
    return extract_data(RAW_CSV)


def get_clean_data():
    """Return the cleaned dataframe."""
    return extract_data(CLEAN_CSV)


def transform_only(input_path: Path = RAW_CSV, output_path: Path = CLEAN_CSV):
    """Clean the raw catalog and save data/processed/anime_catalog_clean.csv."""
    add_import_paths()
    from etl.transform import clean_anime_catalog

    require_file(input_path, "Transform")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print_header("TRANSFORMING ANIME CATALOG")
    df_clean = clean_anime_catalog(input_path=str(input_path), output_path=str(output_path))
    print(f"Saved {len(df_clean)} cleaned rows to {output_path}")
    return df_clean


def create_database(db_path: Path = DB_PATH) -> None:
    """Create or recreate the SQLite schema."""
    add_import_paths()
    from database.schema.create_table import create_db

    print_header("CREATING DATABASE SCHEMA")
    conn, _ = create_db(db_path=db_path)
    conn.close()
    print(f"Database schema is ready: {db_path}")


def load_only(clean_path: Path = CLEAN_CSV, db_path: Path = DB_PATH, recreate_db: bool = True):
    """Load the cleaned catalog into SQLite."""
    add_import_paths()
    from etl.extract import extract_csv
    from etl.load import insert_data

    require_file(clean_path, "Load")
    if recreate_db:
        create_database(db_path)

    print_header("LOADING CLEAN DATA INTO SQLITE")
    df_clean = extract_csv(clean_path)
    inserted = insert_data(df_clean, db_path=db_path)
    print(f"Loaded {inserted} rows into {db_path}")
    return inserted


def run_analysis(db_path: Path = DB_PATH) -> None:
    """Run SQL analysis queries against the SQLite database."""
    add_import_paths()
    from database.queries.data_analysis import run_all_queries

    require_file(db_path, "Analysis")
    print_header("RUNNING SQL ANALYSIS")
    run_all_queries(db_path=db_path)


def run_full_pipeline(
    raw_path: Path = RAW_CSV,
    clean_path: Path = CLEAN_CSV,
    db_path: Path = DB_PATH,
    skip_scrape: bool = False,
    recreate_db: bool = True,
    run_queries: bool = False,
) -> None:
    """Run the complete project pipeline."""
    total = 5 if run_queries else 4
    print_header("STARTING FULL ANIME PIPELINE")

    if skip_scrape:
        print_step(1, total, "Skipping scraping and using existing raw CSV")
        require_file(raw_path, "Full pipeline")
    else:
        print_step(1, total, "Scraping anime catalog")
        scrape_only()

    print_step(2, total, "Extracting raw data")
    extract_data(raw_path)

    print_step(3, total, "Cleaning and transforming data")
    transform_only(input_path=raw_path, output_path=clean_path)

    print_step(4, total, "Loading clean data into SQLite")
    load_only(clean_path=clean_path, db_path=db_path, recreate_db=recreate_db)

    if run_queries:
        print_step(5, total, "Running SQL analysis")
        run_analysis(db_path=db_path)

    print_header("PIPELINE COMPLETED SUCCESSFULLY")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the YummyAnime scraping, ETL, database, and analysis pipeline."
    )
    parser.add_argument(
        "--mode",
        choices=("full", "scrape", "extract", "transform", "schema", "load", "analysis"),
        default="full",
        help="Which part of the project pipeline to run.",
    )
    parser.add_argument(
        "--raw-path",
        default=str(RAW_CSV.relative_to(PROJECT_ROOT)),
        help="Path to the raw anime catalog CSV.",
    )
    parser.add_argument(
        "--clean-path",
        default=str(CLEAN_CSV.relative_to(PROJECT_ROOT)),
        help="Path to the cleaned anime catalog CSV.",
    )
    parser.add_argument(
        "--db-path",
        default=str(DB_PATH.relative_to(PROJECT_ROOT)),
        help="Path to the SQLite database.",
    )
    parser.add_argument(
        "--skip-scrape",
        action="store_true",
        help="For full mode: reuse the existing raw CSV instead of scraping again.",
    )
    parser.add_argument(
        "--keep-db",
        action="store_true",
        help="For full/load mode: load into the existing DB instead of recreating schema.",
    )
    parser.add_argument(
        "--run-analysis",
        action="store_true",
        help="For full mode: run SQL analysis after loading the database.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    raw_path = resolve_project_path(args.raw_path)
    clean_path = resolve_project_path(args.clean_path)
    db_path = resolve_project_path(args.db_path)
    recreate_db = not args.keep_db

    if args.mode == "full":
        run_full_pipeline(
            raw_path=raw_path,
            clean_path=clean_path,
            db_path=db_path,
            skip_scrape=args.skip_scrape,
            recreate_db=recreate_db,
            run_queries=args.run_analysis,
        )
    elif args.mode == "scrape":
        scrape_only()
    elif args.mode == "extract":
        extract_data(raw_path)
    elif args.mode == "transform":
        transform_only(input_path=raw_path, output_path=clean_path)
    elif args.mode == "schema":
        create_database(db_path)
    elif args.mode == "load":
        load_only(clean_path=clean_path, db_path=db_path, recreate_db=recreate_db)
    elif args.mode == "analysis":
        run_analysis(db_path=db_path)


if __name__ == "__main__":
    main()
