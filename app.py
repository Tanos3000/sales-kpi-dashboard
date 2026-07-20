"""Sales KPI Dashboard - Streamlit app.

Turns the sales-performance-analysis project's static notebook analysis into
an interactive dashboard. Run with: streamlit run app.py
"""

import plotly.express as px
import streamlit as st

from data_prep import load_clean_sales

st.set_page_config(page_title="Sales KPI Dashboard", page_icon="\U0001F4CA", layout="wide")


@st.cache_data
def get_data():
    return load_clean_sales()


sales = get_data()

st.title("Sales KPI Dashboard")
st.caption("UK online retailer, Dec 2010 - Dec 2011 (UCI Online Retail dataset)")

# --- Sidebar filters ---
st.sidebar.header("Filters")

min_date, max_date = sales["InvoiceDate"].min().date(), sales["InvoiceDate"].max().date()
date_range = st.sidebar.date_input(
    "Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
)

all_countries = sorted(sales["Country"].unique())
selected_countries = st.sidebar.multiselect("Country", options=all_countries, default=[])

# Only real merchandise (not postage/admin rows) can be filtered by product -
# see data_prep.py's IsProduct column for why.
product_revenue = sales[sales["IsProduct"]].groupby("Description")["Revenue"].sum()
top_products = product_revenue.sort_values(ascending=False).head(30).index.tolist()
selected_products = st.sidebar.multiselect(
    "Product (top 30 by revenue)", options=top_products, default=[]
)

st.sidebar.caption("Leave a filter empty to include everything.")

# --- Apply filters ---
# An empty date_input selection (user mid-pick) falls back to the full range.
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = sales[
    (sales["InvoiceDate"].dt.date >= start_date) & (sales["InvoiceDate"].dt.date <= end_date)
]
if selected_countries:
    filtered = filtered[filtered["Country"].isin(selected_countries)]
if selected_products:
    filtered = filtered[filtered["Description"].isin(selected_products)]

if filtered.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# --- KPI cards ---
total_revenue = filtered["Revenue"].sum()
total_orders = filtered["InvoiceNo"].nunique()
total_customers = filtered["CustomerID"].nunique()
avg_order_value = filtered.groupby("InvoiceNo")["Revenue"].sum().mean()
total_units = filtered["Quantity"].sum()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Revenue", f"£{total_revenue:,.0f}")
col2.metric("Orders", f"{total_orders:,}")
col3.metric("Customers", f"{total_customers:,}")
col4.metric("Avg. Order Value", f"£{avg_order_value:,.2f}")
col5.metric("Units Sold", f"{total_units:,}")

st.caption(f"Showing {len(filtered):,} of {len(sales):,} line items based on the filters above.")

st.divider()

# --- Charts ---
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Revenue over time")
    # Daily aggregation reads as noise once the filtered range gets long, so
    # switch to weekly totals once the range spans more than ~60 days.
    span_days = (end_date - start_date).days
    freq = "D" if span_days <= 60 else "W"
    trend = (
        filtered.set_index("InvoiceDate")["Revenue"]
        .resample(freq)
        .sum()
        .reset_index()
    )
    fig_trend = px.line(trend, x="InvoiceDate", y="Revenue", labels={"InvoiceDate": "Date", "Revenue": "Revenue (£)"})
    st.plotly_chart(fig_trend, use_container_width=True)

with chart_col2:
    st.subheader("Top 10 products by revenue")
    top10 = (
        filtered[filtered["IsProduct"]]
        .groupby("Description")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .sort_values()
    )
    fig_products = px.bar(
        top10, x=top10.values, y=top10.index, orientation="h",
        labels={"x": "Revenue (£)", "y": ""},
    )
    st.plotly_chart(fig_products, use_container_width=True)

st.subheader("Revenue by country")
country_revenue = filtered.groupby("Country")["Revenue"].sum().sort_values(ascending=False).head(15)
fig_country = px.bar(
    country_revenue, x=country_revenue.index, y=country_revenue.values,
    labels={"x": "Country", "y": "Revenue (£)"},
)
st.plotly_chart(fig_country, use_container_width=True)

st.divider()
st.caption(
    "Data: UCI Online Retail Dataset. Cleaning: exact duplicates, missing "
    "descriptions, returns, and a one-off accounting adjustment row are "
    "excluded - see data_prep.py."
)
