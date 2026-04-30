import os
import glob
import sqlite3
import urllib.request
from datetime import datetime
import pandas as pd

RAW_DIR = os.path.join("data", "raw")
DB_DIR = "db"
DB_PATH = os.path.join(DB_DIR, "lab.db")

DATA_URL = "https://data.gov.ua/dataset/7a018f22-0e26-4698-ae4c-1b29981803bc/resource/700bd67f-040c-41de-8bf1-8328e5981736/download/2-sichen-gruden-2025.xlsx"

SHEETS = {
    "Unemployed ": "unemployed",
    "Vacancies": "vacancies",
    "Unemployed by categories": "unemployed_by_categories",
}

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def find_latest_file(folder: str):
    files = glob.glob(os.path.join(folder, "*"))
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def download_file(url: str, out_path: str):
    print(f"Downloading:\n  {url}\n-> {out_path}")
    req = urllib.request.Request(
    url,
    headers={'User-Agent': 'Mozilla/5.0'}
)

with urllib.request.urlopen(req) as response, open(out_path, 'wb') as out_file:
    out_file.write(response.read())
    print("DONE")

def get_or_download_source_file():
    ensure_dir(RAW_DIR)

    latest = find_latest_file(RAW_DIR)
    if latest:
        print(f"Using existing file: {latest}")
        return latest

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    ext = ".data"
    for candidate in [".csv", ".xlsx", ".xls", ".json"]:
        if candidate in DATA_URL.lower():
            ext = candidate
            break

    out_file = os.path.join(RAW_DIR, f"dataset_{ts}{ext}")
    download_file(DATA_URL, out_file)
    return out_file

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns.astype(str)
        .str.replace("\n", " ", regex=False)
        .str.replace("\r", " ", regex=False)
        .str.strip()
    )

    first_col = df.columns[0]
    df = df.dropna(how="all").copy()

    df = df[
        ~df[first_col].astype(str).str.strip().str.lower().isin(["регіон", "period"])
    ].copy()

    return df

def main():
    ensure_dir(DB_DIR)

    source_file = get_or_download_source_file()
    print(f"Using source file: {source_file}")

    conn = sqlite3.connect(DB_PATH)

    for sheet_name, table_name in SHEETS.items():
        df = pd.read_excel(source_file, sheet_name=sheet_name, header=0)
        df = clean_dataframe(df)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"Loaded sheet '{sheet_name}' into table '{table_name}' ({len(df)} rows)")

    conn.close()
    print(f"SQLite database created: {DB_PATH}")
    print("DONE")

if __name__ == "__main__":
    main()