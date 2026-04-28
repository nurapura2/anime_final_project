import pandas as pd
import numpy as np


def clean_anime_catalog(input_path: str, output_path: str) -> pd.DataFrame:
    df_raw = pd.read_csv(input_path)
    df = df_raw.copy()

    # Missing Values 
    missing = df.isnull().sum()
    missing_pct = missing / df.shape[0] * 100

    # Drop columns with 100% missing values
    missing_100 = missing_pct[missing_pct == 100]
    for col in missing_100.index:
        df = df.drop(columns=col)

    # Fill missing values
    df['alt_names'] = df['alt_names'].fillna('')
    df['year'] = df['year'].str.extract(r'(\d{4})').astype(float)
    df['year'] = df['year'].fillna(df['year'].median()).astype(int)
    df['genres'] = df['genres'].fillna('Unknown')
    df['director'] = df['director'].fillna('Unknown')
    df['dubbing'] = df['dubbing'].fillna('Unknown')
    df['studio'] = df['studio'].fillna('Unknown')

    # Drop columns not useful for analysis
    df = df.drop(columns=['kinopoisk_rating', 'kinopoisk_url'])

    # Data Types & Format 
    df['site_views'] = df['site_views'].str.extract(r'(\d+)').astype(int)

    # Split multi-value columns into lists
    for col in ['genres', 'alt_names', 'studio', 'director', 'dubbing']:
        df[col] = df[col].str.split('|')


    # Save 
    df.to_csv(output_path, index=False)

    return df


if __name__ == '__main__':
    df = clean_anime_catalog(
        input_path='../../data/raw/anime_catalog.csv',
        output_path='../../data/processed/anime_catalog_clean.csv'
    )
    print(df.shape)