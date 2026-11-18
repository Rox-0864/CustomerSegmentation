import pandas as pd

from pipeline.clean import clean


def make_row(**overrides):
    base = {
        "INVOICE_NO": "536365",
        "STOCK_CODE": "85123A",
        "DESCRIPTION": "WHITE HANGING HEART",
        "QUANTITY": 6,
        "INVOICE_DATE": "01/12/2019 08:26",
        "UNIT_PRICE": 2.55,
        "CUSTOMER_ID": "17850",
        "REGION": "United Kingdom",
    }
    base.update(overrides)
    return base


def test_valid_row_is_kept_with_total_price():
    df = pd.DataFrame([make_row()])
    out, log = clean(df)
    assert len(out) == 1
    assert out.loc[0, "TOTAL_PRICE"] == 6 * 2.55
    assert "COUNTRY" in out.columns
    assert log["rows_out"] == 1


def test_duplicates_are_removed():
    df = pd.DataFrame([make_row(), make_row()])
    out, log = clean(df)
    assert len(out) == 1
    assert log["removed_duplicates"] == 1


def test_rows_without_customer_are_removed():
    df = pd.DataFrame([make_row(CUSTOMER_ID=None), make_row(CUSTOMER_ID="")])
    out, log = clean(df)
    assert out.empty
    assert log["removed_no_customer"] == 2


def test_cancellations_are_removed():
    df = pd.DataFrame([make_row(INVOICE_NO="C536379")])
    out, log = clean(df)
    assert out.empty
    assert log["removed_cancellations"] == 1


def test_non_positive_quantity_or_price_is_removed():
    df = pd.DataFrame([make_row(QUANTITY=-1), make_row(UNIT_PRICE=0)])
    out, log = clean(df)
    assert out.empty
    assert log["removed_non_positive"] == 2


def test_bad_dates_are_removed():
    df = pd.DataFrame([make_row(INVOICE_DATE="not a date")])
    out, log = clean(df)
    assert out.empty
    assert log["removed_bad_dates"] == 1
