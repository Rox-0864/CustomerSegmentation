from pathlib import Path

from streamlit.testing.v1 import AppTest

from app.charts import SEGMENT_ORDER

APP_PATH = str(Path(__file__).resolve().parent.parent / "streamlit_app.py")


def run_app():
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    return at


def test_app_runs_without_exceptions():
    at = run_app()
    assert not at.exception


def test_default_selection_shows_all_segments_and_seven_charts():
    at = run_app()
    assert at.multiselect[0].value == SEGMENT_ORDER
    assert len(at.metric) == 3
    assert len(at.get("plotly_chart")) == 7


def test_empty_selection_shows_zero_customers():
    at = run_app()
    at.multiselect[0].set_value([]).run()
    assert not at.exception
    assert at.metric[0].value == "0"


def test_public_data_has_no_customer_id():
    from app.charts import load_data

    segments, _ = load_data()
    assert "CUSTOMER_ID" not in segments.columns
