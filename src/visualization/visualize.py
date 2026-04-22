import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

RAW_DIR = os.path.join("data", "raw")
FIG_DIR = os.path.join("reports", "figures")

TARGET_UNEMP = "Number of unemployed at the end of the period"
ALT_STATUS = "of them, persons who previously worked and received the status of unemployed within a year after dismissal"

def find_latest_file(folder: str):
    files = glob.glob(os.path.join(folder, "*"))
    if not files:
        raise FileNotFoundError(f"No files found in {folder}. Download data first.")
    return max(files, key=os.path.getmtime)

def load_data(path: str) -> pd.DataFrame:
    if path.lower().endswith(".csv"):
        return pd.read_csv(path)
    if path.lower().endswith(".xlsx") or path.lower().endswith(".xls"):
        return pd.read_excel(path, header=0)
    raise ValueError(f"Unsupported file type: {path}")

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns.astype(str)
        .str.replace("\n", " ", regex=False)
        .str.replace("\r", " ", regex=False)
        .str.strip()
    )
    if "region" in df.columns:
        df = df[
            ~df["region"].astype(str).str.strip().str.lower().isin(["period", "регіон"])
        ].copy()
    df = df.dropna(how="all").copy()

    for col in df.columns:
        if col != "region":
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def main():
    os.makedirs(FIG_DIR, exist_ok=True)

    latest = find_latest_file(RAW_DIR)
    print(f"Using file: {latest}")
    df = clean_dataset(load_data(latest))

    #bar
    plot_df = df.copy()
    plot_df = plot_df[plot_df["region"].astype(str).str.lower() != "усього"]

    if TARGET_UNEMP in plot_df.columns:
        bar = plot_df[["region", TARGET_UNEMP]].dropna()
        bar = bar.sort_values(TARGET_UNEMP, ascending=False)

        plt.figure()
        plt.bar(bar["region"], bar[TARGET_UNEMP])
        plt.xticks(rotation=90)
        plt.title("Unemployed at end of period by region")
        plt.tight_layout()
        out1 = os.path.join(FIG_DIR, "unemployed_by_region.png")
        plt.savefig(out1, dpi=200)
        plt.close()
        print(f"Saved: {out1}")
    else:
        print(f"Column not found: {TARGET_UNEMP}")

    #scatter
    if TARGET_UNEMP in df.columns and ALT_STATUS in df.columns:
        sc = df[["region", TARGET_UNEMP, ALT_STATUS]].dropna()

        plt.figure()
        plt.scatter(sc[ALT_STATUS], sc[TARGET_UNEMP])
        plt.title("Unemployed vs received status within a year after dismissal")
        plt.xlabel(ALT_STATUS)
        plt.ylabel(TARGET_UNEMP)
        plt.tight_layout()
        out2 = os.path.join(FIG_DIR, "scatter_unemployed_vs_status.png")
        plt.savefig(out2, dpi=200)
        plt.close()
        print(f"Saved: {out2}")
    else:
        print("Scatter skipped: required columns not found.")

    print("DONE")

if __name__ == "__main__":
    main()