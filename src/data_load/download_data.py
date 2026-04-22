import os
import glob
import sqlite3
import pandas as pd

RAW_DIR = os.path.join("data", "raw")
DB_DIR = "db"
DB_PATH = os.path.join(DB_DIR, "lab.db")

SHEETS = {
    "Unemployed ": "unemployed",
    "Vacancies": "vacancies",
    "Unemployed by categories": "unemployed_by_categories",
}

def find_latest_file(folder: str):
    files = glob.glob(os.path.join(folder, "*"))
    if not files:
        raise FileNotFoundError(f"No files found in {folder}. Put your dataset into {folder}.")
    return max(files, key=os.path.getmtime)

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
    os.makedirs(DB_DIR, exist_ok=True)

    latest = find_latest_file(RAW_DIR)
    print(f"Using source file: {latest}")

    conn = sqlite3.connect(DB_PATH)

    for sheet_name, table_name in SHEETS.items():
        df = pd.read_excel(latest, sheet_name=sheet_name, header=0)
        df = clean_dataframe(df)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"Loaded sheet '{sheet_name}' into table '{table_name}' ({len(df)} rows)")

    conn.close()
    print(f"SQLite database created: {DB_PATH}")
    print("DONE")

if __name__ == "__main__":
    main()