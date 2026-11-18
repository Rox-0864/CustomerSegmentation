"""Cleaning pipeline for the online retail dataset.

Usage:
    python -m pipeline.clean --input Online_Retail.csv --output data/processed/clean_transactions.csv
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

DATE_FORMAT = "%d/%m/%Y %H:%M"
REQUIRED_COLUMNS = [
    "INVOICE_NO",
    "STOCK_CODE",
    "DESCRIPTION",
    "QUANTITY",
    "INVOICE_DATE",
    "UNIT_PRICE",
    "CUSTOMER_ID",
    "REGION",
]


def load_raw(path: Path) -> pd.DataFrame:
    """Read the raw CSV, failing early if the expected columns are missing."""
    # The source file is not UTF-8 (contains £ as 0xA3), so read it as latin-1.
    df = pd.read_csv(
        path,
        encoding="latin-1",
        dtype={"INVOICE_NO": str, "STOCK_CODE": str, "CUSTOMER_ID": str},
    )
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in {path}: {sorted(missing)}")
    return df


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Apply cleaning rules and return the cleaned frame plus a log of rows removed per step.

    Each step is logged so the data loss is explicit and auditable.
    """
    log: dict[str, int] = {"rows_in": len(df)}
    df = df.copy()

    df["INVOICE_NO"] = df["INVOICE_NO"].astype(str).str.strip()
    df["CUSTOMER_ID"] = df["CUSTOMER_ID"].astype("string").str.strip()
    df["DESCRIPTION"] = df["DESCRIPTION"].astype("string").str.strip()
    df["REGION"] = df["REGION"].astype("string").str.strip()

    # 1. Exact duplicate rows.
    before = len(df)
    df = df.drop_duplicates()
    log["removed_duplicates"] = before - len(df)

    # 2. Rows without a customer cannot be segmented.
    before = len(df)
    df = df[df["CUSTOMER_ID"].notna() & (df["CUSTOMER_ID"] != "")]
    log["removed_no_customer"] = before - len(df)

    # 3. Cancellations: invoice numbers starting with "C".
    before = len(df)
    df = df[~df["INVOICE_NO"].str.startswith("C")]
    log["removed_cancellations"] = before - len(df)

    # 4. Non-positive quantities or prices (returns, adjustments, free items).
    before = len(df)
    df = df[(df["QUANTITY"] > 0) & (df["UNIT_PRICE"] > 0)]
    log["removed_non_positive"] = before - len(df)

    # 5. Parse dates; drop rows that fail to parse.
    before = len(df)
    df = df.assign(INVOICE_DATE=pd.to_datetime(df["INVOICE_DATE"], format=DATE_FORMAT, errors="coerce"))
    df = df.dropna(subset=["INVOICE_DATE"])
    log["removed_bad_dates"] = before - len(df)

    # 6. Derived monetary value and friendlier column names.
    df = df.assign(TOTAL_PRICE=df["QUANTITY"] * df["UNIT_PRICE"])
    df = df.rename(columns={"REGION": "COUNTRY"})

    log["rows_out"] = len(df)
    log["customers"] = int(df["CUSTOMER_ID"].nunique())
    return df.reset_index(drop=True), log


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean the online retail dataset.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--log", type=Path, default=Path("data/processed/cleaning_log.json"))
    args = parser.parse_args()

    raw = load_raw(args.input)
    cleaned, log = clean(raw)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(args.output, index=False)
    args.log.parent.mkdir(parents=True, exist_ok=True)
    args.log.write_text(json.dumps(log, indent=2), encoding="utf-8")

    print(json.dumps(log, indent=2))


if __name__ == "__main__":
    main()
