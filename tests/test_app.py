import pandas as pd

from app.app import build_app
from app.charts import (
    SEGMENT_ORDER,
    country_bars,
    country_totals,
    kpis,
    load_data,
    other_countries,
    rfm_scatter,
    segment_bars,
    uk_by_segment,
)


def sample_segments():
    return pd.DataFrame(
        {
            "CUSTOMER_ID": [1, 2, 3, 4],
            "recency": [5, 10, 100, 200],
            "frequency": [10, 4, 2, 1],
            "monetary": [1000.0, 500.0, 300.0, 100.0],
            "cluster": [0, 1, 2, 3],
            "segment": ["Champions", "Loyal", "Potential", "Dormant"],
            "country": ["United Kingdom", "United Kingdom", "Germany", "France"],
        }
    )


def sample_monthly():
    return pd.DataFrame({"month": pd.to_datetime(["2020-01-01", "2020-02-01"]), "revenue": [10.0, 20.0]})


def test_kpis_sum_and_average():
    k = kpis(sample_segments())
    assert k["customers"] == "4"
    assert k["revenue"] == "1,900"
    assert k["avg_spend"] == "475"


def test_kpis_empty_selection_is_zero():
    k = kpis(sample_segments().iloc[0:0])
    assert k == {"customers": "0", "revenue": "0", "avg_spend": "0"}


def test_segment_bars_keep_canonical_order_and_counts():
    fig = segment_bars(sample_segments())
    # color="segment" produces one trace per segment, so collect x across traces.
    names = [t.x[0] for t in fig.data]
    assert names == SEGMENT_ORDER


def test_scatter_has_one_trace_per_segment():
    fig = rfm_scatter(sample_segments())
    assert len(fig.data) == 4


def test_app_builds_with_filter_and_graphs():
    app = build_app(sample_segments(), sample_monthly())
    assert app.layout is not None
    assert "segment-filter" in str(app.layout)


def test_real_data_loads_when_processed_files_exist():
    segments, monthly = load_data()
    assert {"segment", "monetary", "recency"}.issubset(segments.columns)
    assert {"month", "revenue"}.issubset(monthly.columns)


def test_country_totals_cover_every_customer():
    fig = country_totals(sample_segments())
    assert sum(fig.data[0].y) == 4


def test_uk_by_segment_counts_only_uk_customers():
    fig = uk_by_segment(sample_segments())
    # sample has 2 UK customers: Champions (1) and Loyal (1)
    counts = dict(zip(fig.data[0].x, fig.data[0].y)) if len(fig.data) == 1 else {t.name: t.y[0] for t in fig.data}
    assert sum(counts.values()) == 2


def test_other_countries_exclude_uk():
    fig = other_countries(sample_segments())
    plotted = {c for t in fig.data for c in t.y}
    assert "United Kingdom" not in plotted
    assert plotted == {"Germany", "France"}


def test_other_countries_empty_selection_does_not_fail():
    fig = other_countries(sample_segments().iloc[0:0])
    assert sum(sum(t.x) for t in fig.data if t.x is not None) == 0


def test_country_bars_include_uk_and_all_customers():
    fig = country_bars(sample_segments())
    plotted = {c for t in fig.data for c in t.y}
    assert "United Kingdom" in plotted
    assert sum(sum(t.x) for t in fig.data) == 4
