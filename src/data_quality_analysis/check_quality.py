import os
import glob
import pandas as pd

RAW_DIR = os.path.join("data", "raw")
REPORTS_DIR = os.path.join("reports")
OUT_DIR = os.path.join("data", "processed")

def find_latest_file(folder: str):
    files = glob.glob(os.path.join(folder, "*"))
    if not files:
        raise FileNotFoundError(f"No files found in {folder}. Download data first.")
    return max(files, key=os.path.getmtime)

def load_data(path: str) -> pd.DataFrame:
    if path.lower().endswith(".csv"):
        return pd.read_csv(path)
    if path.lower().endswith(".xlsx") or path.lower().endswith(".xls"):
        return pd.read_excel(path)
    raise ValueError(f"Unsupported file type: {path}")

def basic_quality_checks(df: pd.DataFrame) -> dict:
    result = {}
    result["rows"] = len(df)
    result["cols"] = len(df.columns)

    missing = df.isna().sum().sort_values(ascending=False)
    result["missing_total"] = int(missing.sum())
    result["missing_by_col_top10"] = missing.head(10).to_dict()

    result["duplicate_rows"] = int(df.duplicated().sum())

    result["dtypes"] = {c: str(t) for c, t in df.dtypes.items()}

    return result

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns.astype(str)
        .str.replace("\n", " ", regex=False)
        .str.replace("\r", " ", regex=False)
        .str.strip()
    )

    if "region" in df.columns:
        df = df[
            ~df["region"].astype(str).str.strip().str.lower().isin(["регіон", "period"])
        ].copy()

    df = df.dropna(how="all").copy()
    return df

def main():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

    latest = find_latest_file(RAW_DIR)
    print(f"Using file: {latest}")

    df = load_data(latest)
    df = clean_dataset(df)
    summary = basic_quality_checks(df)

    missing_df = df.isna().sum().reset_index()
    missing_df.columns = ["column", "missing_count"]
    missing_path = os.path.join(REPORTS_DIR, "missing_values.csv")
    missing_df.to_csv(missing_path, index=False)

    summary_md = os.path.join(REPORTS_DIR, "data_quality_report.md")
    with open(summary_md, "w", encoding="utf-8") as f:
        f.write("# Data Quality Report\n\n")
        f.write(f"- Source file: `{latest}`\n")
        f.write(f"- Rows: {summary['rows']}\n")
        f.write(f"- Columns: {summary['cols']}\n")
        f.write(f"- Total missing values: {summary['missing_total']}\n")
        f.write(f"- Duplicate rows: {summary['duplicate_rows']}\n\n")
        f.write("## Top missing columns (up to 10)\n")
        for k, v in summary["missing_by_col_top10"].items():
            f.write(f"- {k}: {v}\n")

    print(f"Saved: {missing_path}")
    print(f"Saved: {summary_md}")
    print("DONE")


if __name__ == "__main__":
    main()