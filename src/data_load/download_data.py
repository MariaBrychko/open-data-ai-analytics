import os
import sys
import urllib.request
from datetime import datetime

DATA_URL = "https://data.gov.ua/dataset/7a018f22-0e26-4698-ae4c-1b29981803bc/resource/700bd67f-040c-41de-8bf1-8328e5981736/download/2-sichen-gruden-2025.xlsx"

def ensure_dir(path: str) -> None:
    """Create folder if it doesn't exist."""
    os.makedirs(path, exist_ok=True)

def download_file(url: str, out_path: str) -> None:
    """Download file from URL to out_path."""
    print(f"Downloading:\n  {url}\n-> {out_path}")
    urllib.request.urlretrieve(url, out_path)
    print("DONE")

def main():
    raw_dir = os.path.join("data", "raw")
    ensure_dir(raw_dir)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    ext = ".data"
    for candidate in [".csv", ".xlsx", ".xls", ".json"]:
        if candidate in DATA_URL.lower():
            ext = candidate
            break

    out_file = os.path.join(raw_dir, f"dataset_{ts}{ext}")

    if DATA_URL == "PASTE_DIRECT_RESOURCE_URL_HERE":
        print("ERROR: You must paste the direct resource URL into DATA_URL.")
        sys.exit(1)

    download_file(DATA_URL, out_file)


if __name__ == "__main__":
    main()