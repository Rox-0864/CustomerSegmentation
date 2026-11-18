"""Framework-agnostic chart and KPI builders shared by the Dash and Streamlit dashboards.

Every function takes the segment table (or monthly table) and returns a Plotly figure
or plain values, so both front ends render exactly the same content.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "public"
SEGMENT_ORDER = ["Champions", "Loyal", "Potential", "Dormant"]
UK = "United Kingdom"


def load_data(data_dir: Path = DATA_DIR) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Read the publishable data files. They are small, so each app loads them once."""
    segments = pd.read_csv(data_dir / "rfm_segments.csv")
    monthly = pd.read_csv(data_dir / "monthly_revenue.csv", parse_dates=["month"])
    return segments, monthly


def kpis(segments: pd.DataFrame) -> dict[str, str]:
    """Headline numbers for the current selection. Empty selection gives zeros."""
    if segments.empty:
        return {"customers": "0", "revenue": "0", "avg_spend": "0"}
    return {
        "customers": f"{len(segments):,}",
        "revenue": f"{segments['monetary'].sum():,.0f}",
        "avg_spend": f"{segments['monetary'].mean():,.0f}",
    }


def rfm_scatter(segments: pd.DataFrame):
    fig = px.scatter(
        segments,
        x="recency",
        y="monetary",
        color="segment",
        category_orders={"segment": SEGMENT_ORDER},
        hover_data={"frequency": True},
        log_y=True,
        labels={"recency": "Days since last purchase", "monetary": "Total spend (log scale)"},
        title="Customers by recency and spend",
    )
    fig.update_traces(marker={"size": 6, "opacity": 0.6})
    return fig


def segment_bars(segments: pd.DataFrame):
    summary = (
        segments.groupby("segment")
        .agg(customers=("monetary", "size"), revenue=("monetary", "sum"))
        .reindex(SEGMENT_ORDER)
        .dropna()
        .reset_index()
    )
    fig = px.bar(
        summary,
        x="segment",
        y="revenue",
        color="segment",
        category_orders={"segment": SEGMENT_ORDER},
        text="customers",
        labels={"revenue": "Total spend", "segment": "Segment"},
        title="Revenue by segment (label = customers)",
    )
    fig.update_traces(texttemplate="%{text:,} customers", textposition="outside")
    return fig


def country_totals(segments: pd.DataFrame):
    """Vertical bars: customers per country, all countries, no segment split."""
    counts = segments["country"].value_counts().rename_axis("country").reset_index(name="customers")
    fig = px.bar(
        counts,
        x="country",
        y="customers",
        labels={"country": "Country", "customers": "Customers"},
        title="Customers by country",
    )
    fig.update_xaxes(categoryorder="total descending")
    return fig


def uk_by_segment(segments: pd.DataFrame):
    """Customers in the United Kingdom, split by segment."""
    uk = segments[segments["country"] == UK]
    counts = (
        uk.groupby("segment").size().reindex(SEGMENT_ORDER, fill_value=0).reset_index(name="customers")
    )
    fig = px.bar(
        counts,
        x="segment",
        y="customers",
        color="segment",
        category_orders={"segment": SEGMENT_ORDER},
        text="customers",
        labels={"segment": "Segment", "customers": "Customers"},
        title="United Kingdom: customers by segment",
    )
    fig.update_traces(textposition="outside")
    return fig


def country_bars(segments: pd.DataFrame, top_n: int = 15):
    """Top N countries including the United Kingdom, stacked by segment."""
    if segments.empty:
        return px.bar(title="Customers by country, top 15")
    top = segments["country"].value_counts().head(top_n).index
    summary = (
        segments[segments["country"].isin(top)]
        .groupby(["country", "segment"])
        .size()
        .reset_index(name="customers")
    )
    return px.bar(
        summary,
        x="customers",
        y="country",
        color="segment",
        orientation="h",
        category_orders={"segment": SEGMENT_ORDER, "country": list(top)[::-1]},
        labels={"customers": "Customers", "country": "Country", "segment": "Segment"},
        title="Customers by country, top 15 (including United Kingdom)",
    )


def other_countries(segments: pd.DataFrame, top_n: int = 15):
    """Top N countries excluding the United Kingdom, stacked by segment."""
    others = segments[segments["country"] != UK]
    if others.empty:
        return px.bar(title="Other countries (excluding United Kingdom)")
    top = others["country"].value_counts().head(top_n).index
    summary = (
        others[others["country"].isin(top)]
        .groupby(["country", "segment"])
        .size()
        .reset_index(name="customers")
    )
    return px.bar(
        summary,
        x="customers",
        y="country",
        color="segment",
        orientation="h",
        category_orders={"segment": SEGMENT_ORDER, "country": list(top)[::-1]},
        labels={"customers": "Customers", "country": "Country", "segment": "Segment"},
        title="Other countries (excluding United Kingdom), top 15",
    )


def monthly_line(monthly: pd.DataFrame):
    return px.line(
        monthly,
        x="month",
        y="revenue",
        markers=True,
        labels={"month": "Month", "revenue": "Revenue"},
        title="Monthly revenue (Dec 2020 is partial: data ends 9 Dec)",
    )
