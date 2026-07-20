"""Sales KPI Dashboard - Streamlit app.

Turns the sales-performance-analysis project's static notebook analysis into
an interactive dashboard. Run with: streamlit run app.py
"""

import streamlit as st

from data_prep import load_clean_sales

st.set_page_config(page_title="Sales KPI Dashboard", page_icon="\U0001F4CA", layout="wide")


@st.cache_data
def get_data():
    return load_clean_sales()


sales = get_data()

st.title("Sales KPI Dashboard")
st.caption("UK online retailer, Dec 2010 - Dec 2011 (UCI Online Retail dataset)")

total_revenue = sales["Revenue"].sum()
total_orders = sales["InvoiceNo"].nunique()
total_customers = sales["CustomerID"].nunique()
avg_order_value = sales.groupby("InvoiceNo")["Revenue"].sum().mean()
total_units = sales["Quantity"].sum()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Revenue", f"£{total_revenue:,.0f}")
col2.metric("Orders", f"{total_orders:,}")
col3.metric("Customers", f"{total_customers:,}")
col4.metric("Avg. Order Value", f"£{avg_order_value:,.2f}")
col5.metric("Units Sold", f"{total_units:,}")

st.divider()
st.caption(
    "Data: UCI Online Retail Dataset. Cleaning: exact duplicates, missing "
    "descriptions, returns, and a one-off accounting adjustment row are "
    "excluded - see data_prep.py."
)
