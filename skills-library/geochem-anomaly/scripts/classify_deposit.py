#!/usr/bin/env python3
"""
Classify deposit type from REE patterns.

Usage:
    python3 classify_deposit.py --input <csv> --output <out.csv>

Appends columns: hreo_treo, ce_anomaly, deposit_type
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HREE_ELEMENTS = ["Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "Y"]
ALL_REE = ["La", "Ce", "Pr", "Nd", "Sm", "Eu"] + HREE_ELEMENTS

CHOND = {"Ce": 0.613, "La": 0.237, "Pr": 0.0928, "Sm": 0.148, "Gd": 0.199}


def classify_deposit_type(sample_df):
    """Add hreo_treo, ce_anomaly, and deposit_type columns."""
    df = sample_df.copy()

    ree_cols = [f"{el}_ppm" for el in ALL_REE if f"{el}_ppm" in df.columns]
    hree_cols = [f"{el}_ppm" for el in HREE_ELEMENTS if f"{el}_ppm" in df.columns]

    # TREO — use available REEs only
    all_vals = df[ree_cols].fillna(0).sum(axis=1) if ree_cols else 0
    hree_vals = df[hree_cols].fillna(0).sum(axis=1) if hree_cols else 0

    df["hreo_treo"] = np.where(all_vals > 0, hree_vals / all_vals, np.nan)

    # Ce anomaly
    if all(k in df.columns for k in ["Ce_ppm", "La_ppm", "Pr_ppm"]):
        la_n = df["La_ppm"] / CHOND["La"]
        pr_n = df["Pr_ppm"] / CHOND["Pr"]
        ce_n = df["Ce_ppm"] / CHOND["Ce"]
        denom = np.sqrt(la_n * pr_n)
        df["ce_anomaly"] = np.where(denom > 0, ce_n / denom, np.nan)
    else:
        df["ce_anomaly"] = np.nan

    # Classification
    df["deposit_type"] = "Unknown"

    th = df["Th_ppm"] if "Th_ppm" in df.columns else 0
    y = df["Y_ppm"] if "Y_ppm" in df.columns else 0
    ti = df["Ti_ppm"] if "Ti_ppm" in df.columns else 0
    zr = df["Zr_ppm"] if "Zr_ppm" in df.columns else 0

    mask_carbonatite = (
        (df["hreo_treo"] < 0.15)
        & (df["ce_anomaly"] > 1.1)
        & (th > 30)
    )
    mask_iac = (df["hreo_treo"] > 0.30) & (th < 10)
    mask_hydrothermal = (y > 50) & (df["hreo_treo"] > 0.35)
    mask_placer = (ti > 50000) & (zr > 500)

    df.loc[mask_placer, "deposit_type"] = "Placer monazite"
    df.loc[mask_hydrothermal, "deposit_type"] = "Hydrothermal HREE"
    df.loc[mask_iac, "deposit_type"] = "Ion-adsorption clay"
    df.loc[mask_carbonatite, "deposit_type"] = "Carbonatite"

    return df


def main():
    parser = argparse.ArgumentParser(
        description="Classify deposit type from REE patterns."
    )
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--output", required=True, help="Output annotated CSV")
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)
    if not in_path.exists():
        print(f"Error: file not found: {in_path}", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(in_path)
    df = classify_deposit_type(df)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    counts = df["deposit_type"].value_counts().to_dict()
    print(f"Wrote {len(df)} rows to {out_path}")
    print("Deposit type counts:", counts)


if __name__ == "__main__":
    main()
