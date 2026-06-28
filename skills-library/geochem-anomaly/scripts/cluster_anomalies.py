#!/usr/bin/env python3
"""
Spatially cluster geochemical anomalies with DBSCAN.

Usage:
    python3 cluster_anomalies.py --input <csv> --output <out.csv> [options]

Output: cluster summary CSV with centroid, peak, mean, area, and count per cluster.
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler


def cluster_anomalies(
    sample_df,
    element="TREO",
    x_col="x_utm",
    y_col="y_utm",
    eps=100,
    min_samples=3,
    threshold_sigma=3,
):
    """Cluster anomalies with DBSCAN above a median + sigma * MAD threshold."""
    vals = sample_df[element].dropna()
    median = vals.median()
    mad = (vals - median).abs().median()
    if mad == 0:
        mad = vals.std() * 0.6745  # fall back to std-derived MAD equivalent
    threshold = median + threshold_sigma * mad

    anomalies = sample_df[sample_df[element] > threshold].copy()

    if len(anomalies) < min_samples:
        anomalies["cluster_id"] = -1
        return anomalies[["cluster_id"]]

    coords = anomalies[[x_col, y_col]].values
    scaler = StandardScaler()
    coords_scaled = scaler.fit_transform(coords)

    # eps was given in metres; rescale to standardised units by the feature spread
    scale = max(scaler.scale_)
    eps_scaled = eps / scale if scale > 0 else eps / 1000

    clustering = DBSCAN(eps=max(eps_scaled, 0.01), min_samples=min_samples).fit(
        coords_scaled
    )
    anomalies["cluster_id"] = clustering.labels_

    clusters = anomalies[anomalies["cluster_id"] >= 0].groupby("cluster_id")

    summary = []
    for cid, group in clusters:
        x_std = group[x_col].std() if len(group) > 1 else eps / 2
        y_std = group[y_col].std() if len(group) > 1 else eps / 2
        summary.append(
            {
                "cluster_id": int(cid),
                "centroid_x": group[x_col].mean(),
                "centroid_y": group[y_col].mean(),
                "peak_value": group[element].max(),
                "mean_value": group[element].mean(),
                "area_estimate_m2": float(x_std * y_std * 4),
                "sample_count": int(len(group)),
            }
        )

    if not summary:
        return pd.DataFrame(
            columns=[
                "cluster_id",
                "centroid_x",
                "centroid_y",
                "peak_value",
                "mean_value",
                "area_estimate_m2",
                "sample_count",
            ]
        )

    return pd.DataFrame(summary)


def main():
    parser = argparse.ArgumentParser(
        description="Spatially cluster geochemical anomalies with DBSCAN."
    )
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--output", required=True, help="Output cluster summary CSV")
    parser.add_argument(
        "--element", default="TREO", help="Element column to threshold on"
    )
    parser.add_argument("--x-col", default="x_utm", help="X coordinate column")
    parser.add_argument("--y-col", default="y_utm", help="Y coordinate column")
    parser.add_argument(
        "--eps", type=float, default=100, help="DBSCAN neighbourhood radius in metres"
    )
    parser.add_argument(
        "--min-samples", type=int, default=3, help="Minimum points per cluster"
    )
    parser.add_argument(
        "--threshold-sigma",
        type=float,
        default=3,
        help="MAD multiplier for background threshold",
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)
    if not in_path.exists():
        print(f"Error: file not found: {in_path}", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(in_path)
    for col in [args.element, args.x_col, args.y_col]:
        if col not in df.columns:
            print(f"Error: required column '{col}' not found in {in_path}", file=sys.stderr)
            sys.exit(1)

    summary = cluster_anomalies(
        df,
        element=args.element,
        x_col=args.x_col,
        y_col=args.y_col,
        eps=args.eps,
        min_samples=args.min_samples,
        threshold_sigma=args.threshold_sigma,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out_path, index=False)
    print(f"Wrote {len(summary)} cluster(s) to {out_path}")


if __name__ == "__main__":
    main()
