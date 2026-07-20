"""Loads and cleans the UCI Online Retail dataset for the dashboard.

Same cleaning decisions as the sales-performance-analysis project's
02_data_cleaning.ipynb (see that repo for the full step-by-step reasoning):
drop exact duplicates, drop rows with no product description, separate
returns from completed sales, drop zero/negative prices, compute Revenue.
"""

from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).parent / "data" / "online_retail.xlsx"


def load_clean_sales(path: Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_excel(path)

    df = df.drop_duplicates()
    df = df.dropna(subset=["Description"])

    sales = df[df["Quantity"] > 0].copy()
    sales = sales[sales["UnitPrice"] > 0].copy()

    # One row (StockCode "B", InvoiceNo "A563185") is an internal
    # "Adjust bad debt" accounting entry worth £11,062.06 - not a real sale.
    # Left in, it would inflate total revenue and order count by one
    # fictitious "order". Found by checking why InvoiceNo had mixed types
    # (int for real orders, str for this one non-numeric entry).
    sales = sales[sales["StockCode"] != "B"].copy()

    sales["Revenue"] = sales["Quantity"] * sales["UnitPrice"]
    sales["InvoiceDate"] = pd.to_datetime(sales["InvoiceDate"])

    return sales
