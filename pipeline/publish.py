"""Build the public data files that the apps read and that are committed to the repository.

The processed segment file contains CUSTOMER_ID, which must not be published.
This step drops it and copies the monthly aggregates unchanged.

Usage:
    python -m pipeline.publish --processed-dir data/processed --public-dir data/public
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import pandas as pd

PUBLIC_COLUMNS = ["recency", "frequency", "monetary", "country", "cluster", "segment"]


def build_public_segments(segments: pd.DataFrame) -> pd.DataFrame:
    """Keep only the columns the dashboards need. No customer identifier."""
    missing = set(PUBLIC_COLUMNS) - set(segments.columns)
    if missing:
        raise ValueError(f"Missing columns for publication: {sorted(missing)}")
    return segments[PUBLIC_COLUMNS].copy()


def main() -> None:
    parser = argparse.ArgumentParser(description="Write the publishable dashboard data.")
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--public-dir", type=Path, default=Path("data/public"))
    args = parser.parse_args()

    args.public_dir.mkdir(parents=True, exist_ok=True)
    segments = pd.read_csv(args.processed_dir / "rfm_segments.csv", dtype={"CUSTOMER_ID": str})
    build_public_segments(segments).to_csv(args.public_dir / "rfm_segments.csv", index=False)
    shutil.copy(args.processed_dir / "monthly_revenue.csv", args.public_dir / "monthly_revenue.csv")
    print(f"Wrote {len(segments)} customers (no CUSTOMER_ID) to {args.public_dir}")


if __name__ == "__main__":
    main()
