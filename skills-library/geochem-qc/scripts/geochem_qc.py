#!/usr/bin/env python3
"""
Automated QC validation for geochemical survey data.
Returns a verdict: PASS, CONDITIONAL, or FAIL.

Usage:
    python3 geochem_qc.py <csv_file> [--data-type pxrf|gamma|assay|auto]

Output (stdout): JSON with verdict, issues, warnings, and counts.
"""

import argparse
import json
import sys
from pathlib import Path


def automated_qc_check(csv_file, data_type="auto"):
    import pandas as pd

    df = pd.read_csv(csv_file)
    issues = []
    warnings = []

    # --- 0. Auto-detect data type from column names ---
    if data_type == "auto":
        cols = set(c.lower() for c in df.columns)
        if {"k_pct", "eu_ppm", "eth_ppm"} & cols:
            data_type = "gamma"
        elif {"la_ppm", "ce_ppm", "nd_ppm", "y_ppm"} & cols and not {
            "fe_pct",
            "x_utm",
        } & cols:
            data_type = "assay"
        else:
            data_type = "pxrf"

    # --- 1. STRUCTURE CHECK ---
    required_cols = {
        "pxrf": ["sample_id", "x_utm", "y_utm", "La_ppm", "Ce_ppm", "Fe_pct"],
        "gamma": ["sample_id", "x_utm", "y_utm", "K_pct", "eU_ppm", "eTh_ppm"],
        "assay": ["sample_id", "La_ppm", "Ce_ppm", "Nd_ppm", "Y_ppm"],
    }
    missing = [c for c in required_cols[data_type] if c not in df.columns]
    if missing:
        issues.append(f"Missing columns: {missing}")

    # --- 2. QC SAMPLE DETECTION ---
    blanks = df[df["sample_id"].astype(str).str.upper().str.contains("BLANK", na=False)]
    crms = df[
        df["sample_id"].astype(str).str.upper().str.contains("CRM|STD", na=False)
    ]
    dups = df[df["sample_id"].astype(str).str.upper().str.contains("DUP", na=False)]

    if len(blanks) == 0 and len(df) > 20:
        warnings.append(f"No blanks detected (< 5% of {len(df)} samples)")

    if len(crms) == 0 and len(df) > 20:
        warnings.append(f"No CRMs detected (< 5% of {len(df)} samples)")

    # --- 3. CRM RECOVERY CHECK ---
    if not crms.empty:
        # Certified values (example — adjust to your CRM lot certificate)
        expected_ranges = {
            "La": (28, 52),
            "Ce": (80, 100),
            "Nd": (24, 30),
        }
        for _, crm_row in crms.iterrows():
            for element, (lo, hi) in expected_ranges.items():
                col = f"{element}_ppm"
                val = crm_row.get(col)
                if pd.notna(val) and (val < lo or val > hi):
                    issues.append(
                        f"CRM {crm_row['sample_id']}: {element}={val} ppm "
                        f"outside 85-115% recovery (expected {lo}-{hi})"
                    )

    # --- 4. DUPLICATE RPD CHECK ---
    if not dups.empty:
        for _, dup_row in dups.iterrows():
            orig_id = (
                dup_row["sample_id"]
                .replace("_DUP", "")
                .replace("DUP", "")
                .replace("-DUP", "")
            )
            orig = df[df["sample_id"].astype(str).str.upper() == orig_id.upper()]
            if not orig.empty:
                for col in ["La_ppm", "Ce_ppm", "Nd_ppm"]:
                    if col in df.columns:
                        orig_val = orig[col].values[0]
                        dup_val = dup_row[col]
                        if (
                            pd.notna(orig_val)
                            and pd.notna(dup_val)
                            and (orig_val + dup_val) > 0
                        ):
                            rpd = (
                                abs(orig_val - dup_val)
                                / ((orig_val + dup_val) / 2)
                                * 100
                            )
                            if rpd > 30:
                                warnings.append(
                                    f"High duplicate RPD: {col} {rpd:.0f}% "
                                    f"between {orig_id} and {dup_row['sample_id']}"
                                )

    # --- 5. RANGE VALIDATION ---
    element_bounds = {
        "La_ppm": (0, 50000),
        "Ce_ppm": (0, 100000),
        "Fe_pct": (0, 80),
        "K_pct": (0, 14),
        "eU_ppm": (0, 5000),
        "eTh_ppm": (0, 10000),
    }
    for col, (lo, hi) in element_bounds.items():
        if col in df.columns:
            out_of_range = df[(df[col] < lo) | (df[col] > hi)]
            if len(out_of_range) > 0:
                issues.append(
                    f"{col}: {len(out_of_range)} value(s) out of range [{lo}, {hi}]"
                )

    # --- 6. OUTLIER DETECTION (3×IQR) ---
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
    for col in numeric_cols:
        vals = df[col].dropna()
        if len(vals) > 3:
            q1 = vals.quantile(0.25)
            q3 = vals.quantile(0.75)
            iqr = q3 - q1
            if iqr == 0:
                continue
            fence_high = q3 + 3 * iqr
            fence_low = max(0, q1 - 3 * iqr)
            outliers = vals[(vals > fence_high) | (vals < fence_low)]
            if len(outliers) > len(vals) * 0.01:
                warnings.append(
                    f"{col}: {len(outliers)} extreme outlier(s) (> 3×IQR)"
                )

    # --- VERDICT ---
    if issues:
        verdict = "FAIL"
    elif len(warnings) > 2:
        verdict = "CONDITIONAL"
    else:
        verdict = "PASS"

    return {
        "verdict": verdict,
        "issues": issues,
        "warnings": warnings,
        "n_samples": int(len(df)),
        "n_blanks": int(len(blanks)),
        "n_crms": int(len(crms)),
        "n_duplicates": int(len(dups)),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Automated QC validation for geochemical survey data."
    )
    parser.add_argument("csv_file", help="Path to the CSV file to validate")
    parser.add_argument(
        "--data-type",
        default="auto",
        choices=["auto", "pxrf", "gamma", "assay"],
        help="Data type (default: auto-detect from columns)",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        print(f"Error: file not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    result = automated_qc_check(str(csv_path), args.data_type)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
