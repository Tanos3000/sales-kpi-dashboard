"""Downloads the UCI Online Retail dataset into data/online_retail.xlsx.

Same dataset and download logic as the sales-performance-analysis project -
this dashboard visualizes the same underlying sales data.
"""

import io
import ssl
import zipfile
from pathlib import Path
from urllib.request import urlopen

import certifi

URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
DATA_DIR = Path(__file__).parent / "data"
TARGET = DATA_DIR / "online_retail.xlsx"


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    if TARGET.exists():
        print(f"Already downloaded: {TARGET}")
        return

    print("Downloading dataset from UCI Machine Learning Repository...")
    # Explicit certifi CA bundle: some Python installs (notably python.org
    # builds on macOS) don't have a system CA bundle wired up, which makes
    # plain urlopen() fail with CERTIFICATE_VERIFY_FAILED.
    context = ssl.create_default_context(cafile=certifi.where())
    with urlopen(URL, context=context) as response:
        zip_bytes = response.read()

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        with archive.open("Online Retail.xlsx") as source, open(TARGET, "wb") as target:
            target.write(source.read())

    print(f"Saved to {TARGET}")


if __name__ == "__main__":
    main()
