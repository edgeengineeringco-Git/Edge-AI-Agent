#!/usr/bin/env python3
"""
Main geochemical data processing pipeline.

Usage:
    python3 process_geochemical.py --input <csv> --output-dir <dir> [--data-type auto]

Outputs (inside output-dir):
    <stem>_processed.csv   — input rows + TREO_pct, HREO_TREO_ratio columns
    <stem>_summary.json    — n_rows, date_processed, mean/max TREO
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

OXIDE_FACTORS = {
    "La": 1.1728, "Ce": 1.2284, "Pr": 1.2082, "Nd": 1.1664,
    "Sm": 1.1596, "Eu": 1.1579, "Gd": 1.1526, "Tb": 1.1762,
    "Dy": 1.1477, "Ho": 1.1455, "Er": 1.1435, "Tm": 1.1421,
    "Yb": 1.1387, "Lu": 1.1371, "Y": 1.2699, "Sc": 1.5338,
}

ALL_REE = ["La", "Ce", "Pr", "Nd", "Sm", "Eu", "Gd", "Tb",
           "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "Y"]
HREE = ["Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "Y"]


def _auto_detect(df):
    cols = set(c.lower() for c in df.columns)
    if {"k_pct", "eu_ppm", "eth_ppm"} & cols:
        return "gamma"
    if {"la_ppm", "ce_ppm", "nd_ppm", "y_ppm"} & cols and not {"fe_pct", "x_utm"} & cols:
        return "assay"
    return "pxrf"


def normalize_and_correct(df, data_type):
    df = df.copy()
    if "moisture_pct" in df.columns:
        flagged = int((df["moisture_pct"] > 25).sum())
        if flagged:
            logger.warning(f"{flagged} rows flagged for high moisture (>25 %)")
    if data_type == "pxrf" and "Fe_pct" in df.columns:
        flagged = int((df["Fe_pct"] > 15).sum())
        if flagged:
            logger.warning(f"{flagged} rows flagged for Fe matrix suppression (>15 %)")
    return df


def calculate_grades(df):
    df = df.copy()

    # TREO — 15 REE as oxide wt%, summed then / 10 000
    avail_ree = [el for el in ALL_REE if f"{el}_ppm" in df.columns]
    if avail_ree:
        oxides = df[[f"{el}_ppm" for el in avail_ree]].fillna(0).copy()
        for el in avail_ree:
            oxides[f"{el}_ppm"] *= OXIDE_FACTORS.get(el, 1.0)
        df["TREO_pct"] = oxides.sum(axis=1) / 10000.0
    else:
        df["TREO_pct"] = float("nan")

    # HREO:TREO
    avail_hree = [el for el in HREE if f"{el}_ppm" in df.columns]
    if avail_hree and avail_ree:
        hree_sum = df[[f"{el}_ppm" for el in avail_hree]].fillna(0).sum(axis=1)
        ree_sum = df[[f"{el}_ppm" for el in avail_ree]].fillna(0).sum(axis=1)
        df["HREO_TREO_ratio"] = hree_sum / (ree_sum + 1e-6)
    else:
        df["HREO_TREO_ratio"] = float("nan")

    return df


def main():
    parser = argparse.ArgumentParser(
        description="Process geochemical survey data: normalize, correct, grade."
    )
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument(
        "--data-type",
        default="auto",
        choices=["auto", "pxrf", "gamma", "assay"],
        help="Data type (default: auto)",
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    out_dir = Path(args.output_dir)
    if not in_path.exists():
        print(f"Error: file not found: {in_path}", file=sys.stderr)
        sys.exit(1)

    out_dir.mkdir(parents=True, exist_ok=True)
    data_type = args.data_type
    if data_type == "auto":
        probe = pd.read_csv(in_path, nrows=5)
        data_type = _auto_detect(probe)

    logger.info(f"Loading {in_path} (type={data_type})")
    df = pd.read_csv(in_path)

    logger.info(f"Normalising and correcting ({len(df)} rows)")
    df = normalize_and_correct(df, data_type)

    logger.info("Calculating TREO and HREO:TREO")
    df = calculate_grades(df)

    out_csv = out_dir / f"{in_path.stem}_processed.csv"
    df.to_csv(out_csv, index=False)
    logger.info(f"Saved processed data to {out_csv}")

    summary = {
        "n_rows": int(len(df)),
        "date_processed": datetime.now().isoformat(),
        "input_file": str(in_path),
        "data_type": data_type,
        "mean_treo_pct": float(df["TREO_pct"].mean()) if "TREO_pct" in df.columns else None,
        "max_treo_pct": float(df["TREO_pct"].max()) if "TREO_pct" in df.columns else None,
    }
    out_json = out_dir / f"{in_path.stem}_summary.json"
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    logger.info(f"Processing complete. Summary: {out_json}")


if __name__ == "__main__":
    main()
