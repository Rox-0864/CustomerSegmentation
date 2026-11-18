"""RFM feature building and KMeans customer segmentation.

Usage:
    python -m pipeline.segment --input data/processed/clean_transactions.csv \
        --output data/processed/rfm_segments.csv --k 4
    python -m pipeline.segment --input ... --evaluate   # print silhouette/inertia for k=2..8
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42
FEATURES = ["recency", "frequency", "monetary"]


def load_transactions(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"INVOICE_NO": str, "CUSTOMER_ID": str}, parse_dates=["INVOICE_DATE"])
    return df


def build_rfm(df: pd.DataFrame) -> pd.DataFrame:
    """One row per customer with Recency (days), Frequency (invoices), Monetary (total spend).

    The reference date is the day after the last transaction, so a customer who bought
    on the last day has recency 1 rather than 0.
    """
    reference = df["INVOICE_DATE"].max().normalize() + pd.Timedelta(days=1)
    grouped = df.groupby("CUSTOMER_ID")
    rfm = pd.DataFrame(
        {
            # Normalise the last purchase to midnight; otherwise a same-day purchase
            # made after 00:00 truncates to 0 days instead of 1.
            "recency": (reference - grouped["INVOICE_DATE"].max().dt.normalize()).dt.days,
            "frequency": grouped["INVOICE_NO"].nunique(),
            "monetary": grouped["TOTAL_PRICE"].sum().round(2),
            # Most frequent country. Only 8 of 4,338 customers bought from more than one.
            "country": grouped["COUNTRY"].agg(lambda s: s.mode().iloc[0]),
        }
    )
    return rfm.reset_index()


def scale_features(rfm: pd.DataFrame) -> np.ndarray:
    """RFM is heavily right-skewed; log1p before standardising keeps a few big
    spenders from dominating the distance metric."""
    X = np.log1p(rfm[FEATURES].astype(float))
    return StandardScaler().fit_transform(X)


def evaluate_k(X: np.ndarray, k_values=range(2, 9)) -> list[dict]:
    results = []
    for k in k_values:
        model = KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE)
        labels = model.fit_predict(X)
        results.append(
            {
                "k": k,
                "inertia": round(float(model.inertia_), 2),
                "silhouette": round(float(silhouette_score(X, labels)), 4),
            }
        )
    return results


def fit_segments(rfm: pd.DataFrame, k: int) -> pd.DataFrame:
    X = scale_features(rfm)
    model = KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE)
    out = rfm.copy()
    out["cluster"] = model.fit_predict(X)
    return out


def profile(segments: pd.DataFrame) -> pd.DataFrame:
    """Mean RFM per cluster plus size, to name segments by business meaning."""
    prof = segments.groupby("cluster")[FEATURES].agg(["mean", "median"]).round(1)
    prof.columns = [f"{a}_{b}" for a, b in prof.columns]
    prof["customers"] = segments.groupby("cluster").size()
    prof["share_pct"] = (prof["customers"] / len(segments) * 100).round(1)
    return prof.reset_index()


def name_segments(segments: pd.DataFrame) -> dict[int, str]:
    """Map cluster ids to business names using their profile, not their id.

    KMeans ids are arbitrary, so names are derived from the means:
    - highest monetary            -> Champions
    - highest recency (days)      -> Dormant
    - of the remaining two, higher frequency -> Loyal, the other -> Potential
    Only defined for k=4; other k fall back to generic labels.
    """
    prof = segments.groupby("cluster")[FEATURES].mean()
    if len(prof) != 4:
        return {c: f"Segment {c}" for c in prof.index}

    champions = prof["monetary"].idxmax()
    dormant = prof["recency"].idxmax()
    remaining = [c for c in prof.index if c not in (champions, dormant)]
    loyal, potential = sorted(remaining, key=lambda c: prof.loc[c, "frequency"], reverse=True)
    return {champions: "Champions", dormant: "Dormant", loyal: "Loyal", potential: "Potential"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build RFM and segment customers with KMeans.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/processed/rfm_segments.csv"))
    parser.add_argument("--k", type=int, default=4)
    parser.add_argument("--evaluate", action="store_true", help="Only print k metrics and exit.")
    args = parser.parse_args()

    rfm = build_rfm(load_transactions(args.input))
    X = scale_features(rfm)

    if args.evaluate:
        print(json.dumps(evaluate_k(X), indent=2))
        return

    segments = fit_segments(rfm, args.k)
    segments["segment"] = segments["cluster"].map(name_segments(segments))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    segments.to_csv(args.output, index=False)

    prof = profile(segments)
    prof.insert(1, "segment", prof["cluster"].map(name_segments(segments)))
    prof.to_csv(args.output.with_name("segment_profile.csv"), index=False)
    print(prof.to_string(index=False))


if __name__ == "__main__":
    main()
