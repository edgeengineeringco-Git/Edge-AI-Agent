#!/usr/bin/env python3
"""
Quick resource estimate from a cluster summary CSV.

Usage:
    python3 estimate_resource.py --input <csv> --output <json> [--bulk-density 2.5] [--depth 50]

Input CSV must contain (at minimum): sample_count, mean_value (TREO %),
area_estimate_m2, and ideally hreo_treo.
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


def estimate_resource(
    cluster_csv,
    bulk_density=2.5,
    depth_m=50,
):
    df = pd.read_csv(cluster_csv)

    if "mean_treo_pct" not in df.columns and "mean_value" in df.columns:
        df = df.rename(columns={"mean_value": "mean_treo_pct"})
    if "hreo_treo" not in df.columns:
        df["hreo_treo"] = 0.1
    if "area_m2" not in df.columns and "area_estimate_m2" in df.columns:
        df = df.rename(columns={"area_estimate_m2": "area_m2"})

    area_m2 = float(df["area_m2"].sum()) if "area_m2" in df.columns else 0.0
    tonnage_t = area_m2 * depth_m * bulk_density

    mean_treo_pct = float(df["mean_treo_pct"].mean()) if "mean_treo_pct" in df.columns else 0.0
    treo_tonnes = tonnage_t * (mean_treo_pct / 100.0)

    mean_hreo_treo = float(df["hreo_treo"].mean())
    creo_tonnes = treo_tonnes * mean_hreo_treo * 0.35

    n_samples = int(df["sample_count"].sum()) if "sample_count" in df.columns else len(df)
    if n_samples >= 5:
        confidence = "Medium"
    elif n_samples >= 2:
        confidence = "Low"
    else:
        confidence = "Unreliable"

    if mean_treo_pct > 1.0:
        economic = "Potentially Economic"
    elif mean_treo_pct > 0.5:
        economic = "Marginal"
    else:
        economic = "Subeconomic"

    return {
        "area_m2": area_m2,
        "tonnage_t": tonnage_t,
        "mean_treo_pct": mean_treo_pct,
        "treo_tonnes": treo_tonnes,
        "creo_tonnes": creo_tonnes,
        "mean_hreo_treo_ratio": mean_hreo_treo,
        "confidence_tier": confidence,
        "economic_status": economic,
        "depth_assumption_m": depth_m,
        "bulk_density_assumption": bulk_density,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Quick resource estimate from anomaly clusters."
    )
    parser.add_argument("--input", required=True, help="Cluster summary CSV")
    parser.add_argument("--output", required=True, help="Output JSON path")
    parser.add_argument(
        "--bulk-density", type=float, default=2.5, help="Bulk density (t/m^3)"
    )
    parser.add_argument(
        "--depth", type=float, default=50, help="Assumed mineralised thickness (m)"
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)
    if not in_path.exists():
        print(f"Error: file not found: {in_path}", file=sys.stderr)
        sys.exit(1)

    result = estimate_resource(str(in_path), args.bulk_density, args.depth)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
