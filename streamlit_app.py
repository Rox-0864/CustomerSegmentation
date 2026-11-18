"""Streamlit dashboard for customer segmentation.

Run locally:
    streamlit run streamlit_app.py

This file sits at the repository root so Streamlit Community Cloud finds it by default,
and so `app.charts` is importable.
"""

import streamlit as st

from app.charts import (
    SEGMENT_ORDER,
    country_bars,
    country_totals,
    kpis,
    load_data,
    monthly_line,
    other_countries,
    rfm_scatter,
    segment_bars,
    uk_by_segment,
)


@st.cache_data
def get_data():
    return load_data()


st.set_page_config(page_title="Customer Segmentation", layout="centered")
segments, monthly = get_data()

st.title("Customer Segmentation")

selected = st.multiselect("Segments", options=SEGMENT_ORDER, default=SEGMENT_ORDER)
data = segments[segments["segment"].isin(selected)]

headline = kpis(data)
col_customers, col_spend, col_avg = st.columns(3)
col_customers.metric("Customers", headline["customers"])
col_spend.metric("Total spend", headline["revenue"])
col_avg.metric("Avg spend / customer", headline["avg_spend"])

st.plotly_chart(rfm_scatter(data))
st.plotly_chart(segment_bars(data))
st.plotly_chart(country_totals(data))
st.plotly_chart(uk_by_segment(data))
st.plotly_chart(other_countries(data))
st.plotly_chart(country_bars(data))
st.plotly_chart(monthly_line(monthly))
