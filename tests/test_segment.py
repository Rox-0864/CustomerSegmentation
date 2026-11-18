import pandas as pd

from pipeline.segment import build_rfm, name_segments


def tx(customer, invoice, date, total, country="United Kingdom"):
    return {
        "CUSTOMER_ID": customer,
        "INVOICE_NO": invoice,
        "INVOICE_DATE": pd.Timestamp(date),
        "TOTAL_PRICE": total,
        "COUNTRY": country,
    }


def test_country_is_most_frequent_one():
    df = pd.DataFrame(
        [
            tx("1", "A", "2020-01-01 10:00", 1.0, country="Austria"),
            tx("1", "B", "2020-01-02 10:00", 1.0, country="Cyprus"),
            tx("1", "C", "2020-01-03 10:00", 1.0, country="Cyprus"),
        ]
    )
    rfm = build_rfm(df).set_index("CUSTOMER_ID")
    assert rfm.loc["1", "country"] == "Cyprus"


def test_rfm_values_for_one_customer():
    df = pd.DataFrame(
        [
            tx("1", "A", "2020-01-01 10:00", 10.0),
            tx("1", "A", "2020-01-01 11:00", 5.0),  # same invoice: counts once for frequency
            tx("1", "B", "2020-01-10 09:00", 20.0),
            tx("2", "C", "2020-01-05 08:00", 7.0),
        ]
    )
    rfm = build_rfm(df).set_index("CUSTOMER_ID")
    # Reference = 2020-01-11 (max date normalised + 1 day).
    assert rfm.loc["1", "recency"] == 1
    assert rfm.loc["1", "frequency"] == 2
    assert rfm.loc["1", "monetary"] == 35.0
    assert rfm.loc["2", "recency"] == 6
    assert rfm.loc["2", "frequency"] == 1


def test_recency_is_at_least_one_on_last_day_purchase():
    # Regression: a purchase late on the last day used to get recency 0.
    df = pd.DataFrame(
        [
            tx("1", "A", "2020-01-01 08:00", 1.0),
            tx("2", "B", "2020-01-10 23:59", 1.0),
        ]
    )
    rfm = build_rfm(df).set_index("CUSTOMER_ID")
    assert rfm["recency"].min() >= 1


def test_name_segments_by_profile_not_by_id():
    segments = pd.DataFrame(
        {
            "cluster": [5, 5, 9, 9, 1, 1, 3, 3],
            "recency": [10, 10, 300, 300, 60, 60, 20, 20],
            "frequency": [12, 12, 1, 1, 4, 4, 2, 2],
            "monetary": [9000, 9000, 300, 300, 1500, 1500, 400, 400],
        }
    )
    names = name_segments(segments)
    assert names[5] == "Champions"
    assert names[9] == "Dormant"
    assert names[1] == "Loyal"
    assert names[3] == "Potential"
