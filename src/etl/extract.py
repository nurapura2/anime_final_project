import pandas as pd

def extract_csv(path):
    return pd.read_csv(path)

df = extract_csv("data//raw//anime_catalog.csv")
