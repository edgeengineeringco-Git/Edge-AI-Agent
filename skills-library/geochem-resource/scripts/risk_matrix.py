#!/usr/bin/env python3
"""
Geological / analytical / economic risk matrix for a cluster summary.

Usage:
    python3 risk_matrix.py --input <csv> --output <json> [--drill-csv <csv>]
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


def calculate_risk_matrix(cluster_csv, drill_csv=None):
    clusters = pd.read_csv(cluster_csv)

    if "treo_pct" not in clusters.columns and "mean_value" in clusters.columns:
        clusters = clusters.rename(columns={"mean_value": "treo_pct"})
    if "confidence_tier" not in clusters.columns:
        clusters["confidence_tier"] = "Medium"

    # Optional drill data
    drill_data = None
    if drill_csv and Path(drill_csv).exists():
        drill_data = pd.read_csv(drill_csv)

    # GEOLOGICAL RISK
    if drill_data is not None and len(drill_data) > 3:
        geological_risk = "Low"
    elif len(clusters) > 10:
        geological_risk = "Medium"
    else:
        geological_risk = "High"

    # ANALYTICAL RISK
    tiers = clusters["confidence_tier"].value_counts()
    high_quality = tiers.get("High", 0) + tiers.get("Medium", 0)
    n = len(clusters)
    if n > 0 and high_quality / n > 0.8:
        analytical_risk = "Low"
    elif n > 0 and high_quality / n > 0.5:
        analytical_risk = "Medium"
    else:
        analytical_risk = "High"

    # ECONOMIC RISK
    mean_grade = clusters["treo_pct"].mean() if "treo_pct" in clusters.columns else 0
    if mean_grade > 1.5:
        economic_risk = "Low"
    elif mean_grade > 0.5:
        economic_risk = "Medium"
    else:
        economic_risk = "High"

    # OVERALL
    levels = {"Low": 1, "Medium": 2, "High": 3}
    overall = max(
        levels[geological_risk],
        levels[analytical_risk],
        levels[economic_risk],
    )
    overall_risk = ["Low", "Medium", "High"][overall - 1]

    if overall_risk == "Low":
        recommendation = "Advance to drilling"
    elif overall_risk == "Medium":
        recommendation = "Gather more data"
    else:
        recommendation = "Do not advance"

    return {
        "geological_risk": geological_risk,
        "analytical_risk": analytical_risk,
        "economic_risk": economic_risk,
        "overall_risk": overall_risk,
        "recommendation": recommendation,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Risk matrix for a geochemical anomaly cluster."
    )
    parser.add_argument("--input", required=True, help="Cluster summary CSV")
    parser.add_argument("--output", required=True, help="Output JSON path")
    parser.add_argument(
        "--drill-csv", default=None, help="Optional drill-hole CSV (sets geological risk)"
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"Error: file not found: {in_path}", file=sys.stderr)
        sys.exit(1)

    result = calculate_risk_matrix(str(in_path), args.drill_csv)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
