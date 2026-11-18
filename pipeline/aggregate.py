"""Precomputed aggregates for the dashboard, so the app never reads the 36 MB transactions file.

Usage:
    python -m pipeline.aggregate --input data/processed/clean_transactions.csv --output-dir data/processed
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def monthly_revenue(transactions: pd.DataFrame) -> pd.DataFrame:
    """Revenue, orders and active customers per calendar month."""
    df = transactions.assign(month=transactions["INVOICE_DATE"].dt.to_period("M").dt.to_timestamp())
    out = df.groupby("month").agg(
        revenue=("TOTAL_PRICE", "sum"),
        orders=("INVOICE_NO", "nunique"),
        customers=("CUSTOMER_ID", "nunique"),
    )
    return out.round(2).reset_index()


def main() -> None:
    parser = argparse.ArgumentParser(description="Precompute dashboard aggregates.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    args = parser.parse_args()

    transactions = pd.read_csv(args.input, parse_dates=["INVOICE_DATE"], dtype={"INVOICE_NO": str, "CUSTOMER_ID": str})
    args.output_dir.mkdir(parents=True, exist_ok=True)
    monthly = monthly_revenue(transactions)
    monthly.to_csv(args.output_dir / "monthly_revenue.csv", index=False)
    print(monthly.to_string(index=False))


if __name__ == "__main__":
    main()
