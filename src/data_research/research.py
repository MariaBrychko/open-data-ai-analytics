import os
import glob
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

RAW_DIR = os.path.join("data", "raw")
REPORTS_DIR = os.path.join("reports")

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
        df = df[df["region"].astype(str).str.lower() != "period"].copy()

    df = df.dropna(how="all").copy()

    for col in df.columns:
        if col != "region":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

def main():
    os.makedirs(REPORTS_DIR, exist_ok=True)

    latest = find_latest_file(RAW_DIR)
    print(f"Using file: {latest}")

    df = load_data(latest)
    df = clean_dataset(df)

    #EDA
    eda_path = os.path.join(REPORTS_DIR, "eda_summary.csv")
    df.describe(include="all").to_csv(eda_path)
    print(f"Saved: {eda_path}")

    #correlation
    num_df = df.select_dtypes(include="number").copy()

    corr_path = os.path.join(REPORTS_DIR, "correlation.csv")
    if num_df.shape[1] >= 2:
        corr = num_df.corr(numeric_only=True)
        corr.to_csv(corr_path)
        print(f"Saved: {corr_path}")
    else:
        print("Not enough numeric columns for correlation.")

    #linear regression
    target_col = "Number of unemployed at the end of the period"
    model_md = os.path.join(REPORTS_DIR, "model_report.md")

    if target_col not in df.columns:
        with open(model_md, "w", encoding="utf-8") as f:
            f.write("# Model Report\n\n")
            f.write("Target column not found.\n\n")
            f.write(f"Expected target: `{target_col}`\n\n")
            f.write("Available columns:\n")
            for c in df.columns:
                f.write(f"- {c}\n")
        print(f"Saved: {model_md}")
        print("Target column not found. Check the column name in the file.")
        return

    if target_col in num_df.columns and num_df.shape[1] >= 2:
        features = [c for c in num_df.columns if c != target_col]

        X = num_df[features].fillna(0)
        y = num_df[target_col].fillna(0)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model = LinearRegression()
        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)

        coefs = pd.Series(model.coef_, index=features).sort_values(key=lambda s: s.abs(), ascending=False)

        with open(model_md, "w", encoding="utf-8") as f:
            f.write("# Model Report (Linear Regression)\n\n")
            f.write(f"- Source file: `{latest}`\n")
            f.write(f"- Target: `{target_col}`\n")
            f.write(f"- Features used: {len(features)} numeric columns\n\n")
            f.write(f"**MAE:** {mae:.4f}\n\n")
            f.write(f"**R2:** {r2:.4f}\n\n")
            f.write("## Top 10 coefficients (by absolute value)\n")
            for name, val in coefs.head(10).items():
                f.write(f"- {name}: {val:.6f}\n")

        print(f"Saved: {model_md}")
    else:
        with open(model_md, "w", encoding="utf-8") as f:
            f.write("# Model Report\n\nNot enough numeric columns to train a model.\n")
        print(f"Saved: {model_md}")

    print("DONE")


if __name__ == "__main__":
    main()