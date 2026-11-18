"""Dash dashboard for customer segmentation.

Run locally:
    python -m app.app
"""

from __future__ import annotations

import pandas as pd
from dash import Dash, Input, Output, dcc, html

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


def build_app(segments: pd.DataFrame, monthly: pd.DataFrame) -> Dash:
    app = Dash(__name__, title="Customer Segmentation")
    options = [{"label": s, "value": s} for s in SEGMENT_ORDER]

    app.layout = html.Div(
        [
            html.H1("Customer Segmentation"),
            html.Label("Segments"),
            dcc.Dropdown(id="segment-filter", options=options, value=SEGMENT_ORDER, multi=True),
            html.Div(
                [
                    html.Div([html.H3("Customers"), html.P(id="kpi-customers")], className="kpi"),
                    html.Div([html.H3("Total spend"), html.P(id="kpi-revenue")], className="kpi"),
                    html.Div([html.H3("Avg spend / customer"), html.P(id="kpi-avg")], className="kpi"),
                ],
                style={"display": "flex", "gap": "2rem"},
            ),
            dcc.Graph(id="rfm-scatter"),
            dcc.Graph(id="segment-bars"),
            dcc.Graph(id="country-totals"),
            dcc.Graph(id="uk-segments"),
            dcc.Graph(id="other-countries"),
            dcc.Graph(id="country-bars"),
            dcc.Graph(id="monthly-revenue", figure=monthly_line(monthly)),
        ],
        style={"maxWidth": "1100px", "margin": "0 auto", "fontFamily": "sans-serif"},
    )

    @app.callback(
        Output("kpi-customers", "children"),
        Output("kpi-revenue", "children"),
        Output("kpi-avg", "children"),
        Output("rfm-scatter", "figure"),
        Output("segment-bars", "figure"),
        Output("country-totals", "figure"),
        Output("uk-segments", "figure"),
        Output("other-countries", "figure"),
        Output("country-bars", "figure"),
        Input("segment-filter", "value"),
    )
    def update(selected):
        selected = selected or []
        data = segments[segments["segment"].isin(selected)]
        k = kpis(data)
        return (
            k["customers"],
            k["revenue"],
            k["avg_spend"],
            rfm_scatter(data),
            segment_bars(data),
            country_totals(data),
            uk_by_segment(data),
            other_countries(data),
            country_bars(data),
        )

    return app


def create_app() -> Dash:
    segments, monthly = load_data()
    return build_app(segments, monthly)


# Exposed for WSGI servers (gunicorn app.app:server).
app = create_app()
server = app.server


if __name__ == "__main__":
    create_app().run(debug=True)
