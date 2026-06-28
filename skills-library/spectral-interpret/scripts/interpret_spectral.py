#!/usr/bin/env python3
"""
Interpret gamma-ray and pXRF spectral data for REE exploration.

Usage:
    python3 interpret_spectral.py --input <csv> --output <report.json>
        [--data-type auto|gamma|pxrf] [--anomaly-sigma 3] [--cluster-distance 200]

Output: JSON report with QC tier, background stats, anomalies, and (for gamma) radiometric summary.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

OXIDE_FACTORS = {
    "La": 1.173, "Ce": 1.228, "Pr": 1.208, "Nd": 1.166, "Sm": 1.160,
    "Eu": 1.158, "Gd": 1.153, "Tb": 1.176, "Dy": 1.148, "Ho": 1.146,
    "Er": 1.143, "Tm": 1.142, "Yb": 1.139, "Lu": 1.137, "Y": 1.270, "Sc": 1.534,
}
ALL_REE = ["La", "Ce", "Pr", "Nd", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "Y"]
HREE = ["Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "Y"]

CHOND = {
    "La": 0.237, "Ce": 0.613, "Pr": 0.0928, "Nd": 0.457, "Sm": 0.148,
    "Eu": 0.0563, "Gd": 0.199, "Tb": 0.0361, "Dy": 0.246, "Ho": 0.0546,
    "Er": 0.160, "Tm": 0.0247, "Yb": 0.161, "Lu": 0.0246,
}

CRUSTAL = {
    "Ce": 60, "La": 30, "Nd": 27, "Y": 21, "Dy": 3, "Th": 10, "eTh": 25,
}


def _auto_detect(df):
    cols = set(c.lower() for c in df.columns)
    if {"k_pct", "eu_ppm", "eth_ppm"} & cols:
        return "gamma"
    if {"la_ppm", "ce_ppm"} & cols:
        return "pxrf"
    return "pxrf"


def qc_gamma(df):
    flags = []
    tier = "PASS"
    if "acquisition_time_s" in df.columns:
        low = (df["acquisition_time_s"] < 1).sum()
        if low > 0:
            flags.append(f"{low} readings with acquisition_time < 1 s (airborne) or < 60 s (ground)")
    if "total_count_cps" in df.columns:
        low = (df["total_count_cps"] < 50).sum()
        if low > 0:
            flags.append(f"{low} readings with total_count_cps < 50 (possible malfunction)")
    if len(flags) > 2:
        tier = "CONDITIONAL"
    return tier, flags


def qc_pxrf(df):
    flags = []
    tier = "PASS"
    if "reading_time_s" in df.columns:
        low = (df["reading_time_s"] < 30).sum()
        if low > 0:
            flags.append(f"{low} readings with reading_time < 30 s (semi-quantitative)")
    if "Fe_pct" in df.columns:
        fe = (df["Fe_pct"] > 15).sum()
        if fe > 0:
            flags.append(f"{fe} readings with Fe > 15% (matrix suppression likely)")
    if "Ca_pct" in df.columns:
        ca = (df["Ca_pct"] > 20).sum()
        if ca > 0:
            flags.append(f"{ca} readings with Ca > 20% (carbonate matrix may inflate Ce/La)")
    if len(flags) > 2:
        tier = "CONDITIONAL"
    return tier, flags


def background_stats(df, element_cols):
    stats = {}
    for col in element_cols:
        if col not in df.columns:
            continue
        vals = df[col].dropna()
        if len(vals) == 0:
            continue
        med = float(vals.median())
        mad = float((vals - med).abs().median())
        if mad == 0:
            mad = float(vals.std()) * 0.6745
        stats[col] = {
            "median": round(med, 4),
            "mad": round(mad, 4),
            "background_threshold": round(med + 2 * mad, 4),
            "anomaly_threshold": round(med + 3 * mad, 4),
            "n": int(len(vals)),
        }
    return stats


def compute_ree_features(df):
    df = df.copy()
    avail_ree = [el for el in ALL_REE if f"{el}_ppm" in df.columns]
    if avail_ree:
        oxides = df[[f"{el}_ppm" for el in avail_ree]].fillna(0).copy()
        for el in avail_ree:
            oxides[f"{el}_ppm"] *= OXIDE_FACTORS.get(el, 1.0)
        df["TREO_pct"] = oxides.sum(axis=1) / 10000.0
    else:
        df["TREO_pct"] = float("nan")

    avail_hree = [el for el in HREE if f"{el}_ppm" in df.columns]
    if avail_hree and avail_ree:
        hree_sum = df[[f"{el}_ppm" for el in avail_hree]].fillna(0).sum(axis=1)
        ree_sum = df[[f"{el}_ppm" for el in avail_ree]].fillna(0).sum(axis=1)
        df["HREO_TREO_ratio"] = hree_sum / (ree_sum + 1e-6)
    else:
        df["HREO_TREO_ratio"] = float("nan")

    # Ce anomaly
    if all(f"{el}_ppm" in df.columns for el in ["Ce", "La", "Pr"]):
        la_n = df["La_ppm"] / CHOND["La"]
        pr_n = df["Pr_ppm"] / CHOND["Pr"]
        ce_n = df["Ce_ppm"] / CHOND["Ce"]
        denom = np.sqrt(la_n * pr_n)
        df["ce_anomaly"] = np.where(denom > 0, ce_n / denom, np.nan)
    else:
        df["ce_anomaly"] = float("nan")

    # Eu anomaly
    if all(f"{el}_ppm" in df.columns for el in ["Eu", "Sm", "Gd"]):
        sm_n = df["Sm_ppm"] / CHOND["Sm"]
        gd_n = df["Gd_ppm"] / CHOND["Gd"]
        eu_n = df["Eu_ppm"] / CHOND["Eu"]
        denom = np.sqrt(sm_n * gd_n)
        df["eu_anomaly"] = np.where(denom > 0, eu_n / denom, np.nan)
    else:
        df["eu_anomaly"] = float("nan")

    return df


def fingerprint_deposit(row):
    hreo = row.get("HREO_TREO_ratio") or 0
    ce = row.get("ce_anomaly") or 1.0
    th = row.get("Th_ppm") or 0
    y = row.get("Y_ppm") or 0
    ti = row.get("Ti_ppm") or 0
    zr = row.get("Zr_ppm") or 0
    sc = row.get("Sc_ppm") or 0
    cr = row.get("Cr_ppm") or 0
    ni = row.get("Ni_ppm") or 0
    nb = row.get("Nb_ppm") or 0

    if hreo < 0.15 and ce > 1.1 and th > 30 and nb > 20:
        return "Carbonatite"
    if hreo > 0.30 and th < 10:
        return "Ion-adsorption clay"
    if y > 50 and hreo > 0.35:
        return "Hydrothermal HREE"
    if sc > 30 and cr > 500 and ni > 200:
        return "Laterite / ophiolite-related"
    if ti > 50000 and zr > 500 and th > 20:
        return "Placer monazite-xenotime"
    return "Unknown"


def cluster_anomalies(df, value_col, x_col, y_col, eps_m, min_samples=3, sigma=3):
    if value_col not in df.columns:
        return pd.DataFrame()
    vals = df[value_col].dropna()
    med = vals.median()
    mad = (vals - med).abs().median()
    if mad == 0:
        mad = vals.std() * 0.6745
    threshold = med + sigma * mad
    anom = df[df[value_col] > threshold].copy()
    if len(anom) < min_samples:
        return pd.DataFrame()

    coords = anom[[x_col, y_col]].values
    scaler = StandardScaler()
    coords_s = scaler.fit_transform(coords)
    scale = max(scaler.scale_) if max(scaler.scale_) > 0 else 1.0
    eps_s = max(eps_m / scale, 0.01)
    labels = DBSCAN(eps=eps_s, min_samples=min_samples).fit(coords_s).labels_
    anom["cluster_id"] = labels
    anom = anom[anom["cluster_id"] >= 0]
    if anom.empty:
        return pd.DataFrame()

    rows = []
    for cid, g in anom.groupby("cluster_id"):
        row = {
            "cluster_id": int(cid),
            "centroid_x": float(g[x_col].mean()),
            "centroid_y": float(g[y_col].mean()),
            "peak_treo_pct": round(float(g[value_col].max()), 4) if value_col in g.columns else None,
            "mean_treo_pct": round(float(g[value_col].mean()), 4) if value_col in g.columns else None,
            "hreo_treo_ratio": round(float(g["HREO_TREO_ratio"].mean()), 4) if "HREO_TREO_ratio" in g.columns else None,
            "ce_anomaly": round(float(g["ce_anomaly"].mean()), 4) if "ce_anomaly" in g.columns else None,
            "eu_anomaly": round(float(g["eu_anomaly"].mean()), 4) if "eu_anomaly" in g.columns else None,
            "deposit_type_fingerprint": fingerprint_deposit(g.iloc[0]) if len(g) > 0 else "Unknown",
            "n_points": int(len(g)),
        }
        rows.append(row)
    return pd.DataFrame(rows)


def gamma_summary(df):
    out = {}
    if "eTh_ppm" in df.columns:
        out["peak_eTh"] = round(float(df["eTh_ppm"].max()), 2)
        out["mean_eTh"] = round(float(df["eTh_ppm"].mean()), 2)
    if "eU_ppm" in df.columns:
        out["peak_eU"] = round(float(df["eU_ppm"].max()), 2)
        out["mean_eU"] = round(float(df["eU_ppm"].mean()), 2)
    if "K_pct" in df.columns:
        out["mean_K_pct"] = round(float(df["K_pct"].mean()), 3)
    if "eTh_ppm" in df.columns and "eU_ppm" in df.columns:
        ratio = df["eTh_ppm"] / (df["eU_ppm"].replace(0, np.nan))
        out["mean_ThU_ratio"] = round(float(ratio.mean()), 2)
    if "eTh_ppm" in df.columns and "K_pct" in df.columns:
        f_param = (df["eTh_ppm"] + 3.5 * df["eU_ppm"]) / df["K_pct"].replace(0, np.nan)
        out["mean_F_parameter"] = round(float(f_param.mean()), 2)
    return out if out else None


def main():
    parser = argparse.ArgumentParser(description="Interpret gamma-ray and pXRF spectral data.")
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--output", required=True, help="Output JSON report path")
    parser.add_argument(
        "--data-type",
        default="auto",
        choices=["auto", "gamma", "pxrf"],
        help="Data type (default: auto-detect)",
    )
    parser.add_argument(
        "--anomaly-sigma", type=float, default=3, help="MAD multiplier for anomaly threshold"
    )
    parser.add_argument(
        "--cluster-distance", type=float, default=200, help="Max cluster distance in metres"
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"Error: file not found: {in_path}", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(in_path)
    data_type = args.data_type
    if data_type == "auto":
        data_type = _auto_detect(df)

    # QC
    if data_type == "gamma":
        qc_tier, qc_flags = qc_gamma(df)
    else:
        qc_tier, qc_flags = qc_pxrf(df)

    # Background
    if data_type == "gamma":
        elem_cols = [c for c in ["K_pct", "eU_ppm", "eTh_ppm", "total_count_cps"] if c in df.columns]
    else:
        elem_cols = [c for c in df.columns if c.endswith("_ppm") or c.endswith("_pct")]
    bg = background_stats(df, elem_cols)

    # REE features (pxrf only)
    anomalies_df = pd.DataFrame()
    if data_type == "pxrf":
        df = compute_ree_features(df)
        x_col = "x_utm" if "x_utm" in df.columns else None
        y_col = "y_utm" if "y_utm" in df.columns else None
        if x_col and y_col and "TREO_pct" in df.columns:
            anomalies_df = cluster_anomalies(
                df, "TREO_pct", x_col, y_col, args.cluster_distance, sigma=args.anomaly_sigma
            )

    # Gamma summary
    gsummary = gamma_summary(df) if data_type == "gamma" else None

    report = {
        "data_type": data_type,
        "qc_tier": qc_tier,
        "qc_flags": qc_flags,
        "n_samples": int(len(df)),
        "background": bg,
        "anomalies": anomalies_df.to_dict(orient="records") if not anomalies_df.empty else [],
        "gamma_summary": gsummary,
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
