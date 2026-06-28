#!/usr/bin/env python3
"""
REE ore grade economic assessment — structured zone report.

Usage:
    python3 assess_grade.py --input <zones.json|zones.csv> --output <report.json>
        [--basket-price 30] [--metallurgical-recovery 70]

Input: JSON array or CSV with one object/row per zone.
Output: JSON report with grade summary, tonnage, economic tier, risk, classification.
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd


# --- Cut-off tables (lower bound of each band, % TREO) ---
CUT_OFF = {
    "carbonatite":   {"subeconomic": 0.5, "marginal_lo": 0.5, "marginal_hi": 1.0, "economic_lo": 1.0, "economic_hi": 3.0, "high_grade": 3.0, "pit": "open"},
    "carbonatite_ug": {"subeconomic": 2.0, "marginal_lo": 2.0, "marginal_hi": 4.0, "economic_lo": 4.0, "economic_hi": 8.0, "high_grade": 8.0, "pit": "underground"},
    "iac_clay":      {"subeconomic": 0.04, "marginal_lo": 0.04, "marginal_hi": 0.07, "economic_lo": 0.07, "economic_hi": 0.20, "high_grade": 0.20},
    "alkaline":      {"subeconomic": 0.3, "marginal_lo": 0.3, "marginal_hi": 0.7, "economic_lo": 0.7, "economic_hi": 2.5, "high_grade": 2.5},
    "placer":        {"subeconomic": 0.5, "marginal_lo": 0.5, "marginal_hi": 1.0, "economic_lo": 1.0, "economic_hi": 3.0, "high_grade": 3.0},
}

BULK_DENSITY_DEFAULT = {
    "iac_clay": 1.6,
    "carbonatite": 2.7,
    "alkaline": 2.5,
    "placer": 1.9,
    "laterite": 1.8,
    "default": 2.5,
}

# Uncertainty multiplier by tier
UNCERTAINTY = {"high": 0.15, "medium": 0.30, "low": 0.50, "unreliable": 1.0}


def verify_confidence(zone):
    """Independently verify confidence tier from QC signals."""
    icp = zone.get("icp_validation_pts") or 0
    data_source = (zone.get("data_source") or "").lower()
    crm_ok = zone.get("crm_in_spec", True)
    dup_rpd_ok = zone.get("duplicate_rpd_ok", True)
    matrix_flags = zone.get("matrix_flags_present", False)

    if icp >= 5 and crm_ok and dup_rpd_ok and not matrix_flags:
        return "high"
    if (2 <= icp <= 4) or (data_source == "pXRF" and crm_ok):
        return "medium"
    if data_source in ("pXRF", "model_predicted") and not matrix_flags:
        return "low"
    if icp < 2 or matrix_flags or not crm_ok:
        return "unreliable"
    return zone.get("confidence_tier", "low")


def economic_tier(treo_pct, deposit_type, hreo_treo):
    """Classify economic tier with optional HREE premium."""
    key = deposit_type.lower().replace(" ", "_").replace("-", "_")
    # Map common aliases
    if "ion" in key or "iac" in key or "clay" in key:
        key = "iac_clay"
    elif "carbonatite" in key and "underground" in key:
        key = "carbonatite_ug"
    elif "carbonatite" in key:
        key = "carbonatite"
    elif "alkaline" in key or "peralkaline" in key:
        key = "alkaline"
    elif "placer" in key or "monazite" in key:
        key = "placer"
    else:
        key = "carbonatite"

    table = CUT_OFF.get(key, CUT_OFF["carbonatite"])

    # HREE premium: reduce effective cut-off by up to 40% if HREO:TREO > 0.25
    hree_premium = hreo_treo is not None and hreo_treo > 0.25
    discount = 0.6 if hree_premium else 1.0

    eco_lo = table["economic_lo"] * discount
    eco_hi = table["economic_hi"] * discount
    marg_lo = table["marginal_lo"] * discount
    marg_hi = table["marginal_hi"] * discount
    high = table["high_grade"] * discount

    if treo_pct >= high:
        return "High Grade", hree_premium
    if treo_pct >= eco_lo:
        if treo_pct <= eco_hi:
            return "Economic", hree_premium
        return "Economic", hree_premium
    if treo_pct >= marg_lo:
        return "Marginal", hree_premium
    return "Subeconomic", hree_premium


def classify_resource(confidence_tier, has_cp):
    """JORC / NI 43-101 classification."""
    if not has_cp:
        return "Exploration Target", "Competent Person review required for Inferred or higher"
    t = confidence_tier.lower()
    if t == "high":
        return "Indicated Resource", "High confidence; reasonable continuity demonstrated"
    if t == "medium":
        return "Inferred Resource", "Medium confidence; geological continuity assumed"
    if t == "low":
        return "Inferred Resource", "Low confidence; geological continuity assumed"
    return "Exploration Target", "Insufficient confidence for resource classification"


def risk_matrix(zone, confidence_tier, economic_tier_str):
    """Three-axis risk assessment."""
    # Geological
    drill_holes = zone.get("drill_hole_count") or 0
    if drill_holes > 3:
        geo = "Low"
    elif zone.get("surface_only", False):
        geo = "Medium"
    else:
        geo = "High"

    # Analytical
    t = confidence_tier.lower()
    if t == "high":
        ana = "Low"
    elif t == "medium":
        ana = "Medium"
    else:
        ana = "High"

    # Economic
    if economic_tier_str == "High Grade":
        eco = "Low"
    elif economic_tier_str == "Economic":
        eco = "Low"
    elif economic_tier_str == "Marginal":
        eco = "Medium"
    else:
        eco = "High"

    levels = {"Low": 1, "Medium": 2, "High": 3}
    overall = max(levels[geo], levels[ana], levels[eco])
    overall_str = ["Low", "Medium", "High"][overall - 1]

    return {
        "geological": geo,
        "analytical": ana,
        "economic": eco,
        "overall": overall_str,
    }


def phrasing(confidence_tier, economic_tier_str):
    t = confidence_tier.lower()
    if t == "unreliable":
        return "Data quality is insufficient for grade interpretation. Re-assay is required before any assessment."
    if t == "low":
        return "These results are indicative only. They should not be used for resource estimation or investment decisions."
    if economic_tier_str in ("Subeconomic",):
        return "A geochemical anomaly is present. Grade is below current economic thresholds but warrants further investigation to characterize extent and depth."
    if economic_tier_str == "Marginal":
        return "Preliminary results are encouraging but require ICP-MS confirmation and additional sampling before economic significance can be assessed."
    return "The data supports a potential economic REE concentration subject to Competent Person review."


def assess_zone(zone, basket_price, recovery_override):
    zid = zone.get("zone_id", "?")
    treo = zone.get("treo_pct") or 0.0
    hreo_treo = zone.get("hreo_treo_ratio")
    creo = zone.get("creo_pct")
    area = zone.get("area_m2") or 0.0
    depth = zone.get("depth_m") or 50.0
    deposit = zone.get("deposit_type") or "carbonatite"
    bulk_dens = zone.get("bulk_density_t_m3") or BULK_DENSITY_DEFAULT.get(
        deposit.lower().replace(" ", "_"), BULK_DENSITY_DEFAULT["default"]
    )
    recovery = recovery_override if recovery_override is not None else (zone.get("metallurgical_recovery_pct") or 70.0)
    has_cp = bool(zone.get("competent_person_cited", False))

    verified_tier = verify_confidence(zone)
    input_tier = (zone.get("confidence_tier") or "low").lower()
    flag = None
    tier_ranking = {"unreliable": 0, "low": 1, "medium": 2, "high": 3}
    if tier_ranking.get(verified_tier, 0) < tier_ranking.get(input_tier, 0):
        flag = f"Input tier '{input_tier}' upgraded to '{verified_tier}' based on QC signals"

    unc = UNCERTAINTY.get(verified_tier, 0.5)
    treo_lo = round(treo * (1 - unc), 4)
    treo_hi = round(treo * (1 + unc), 4)

    labels = []
    if hreo_treo is not None and hreo_treo > 0.30:
        labels.append("HREE-enriched")
    if creo and treo and (creo / treo) > 0.25:
        labels.append("magnet REE dominant")

    grade_summary = {
        "treo_pct": treo,
        "treo_range": [treo_lo, treo_hi],
        "hreo_treo_ratio": hreo_treo,
        "creo_pct": creo,
        "labels": labels,
    }

    # Tonnage (Medium+ only)
    tonnage = None
    if verified_tier in ("medium", "high") and area > 0:
        tonnage_t = area * depth * bulk_dens
        treo_tonnes = tonnage_t * (treo / 100.0)
        rec_treo = treo_tonnes * (recovery / 100.0)
        creo_tonnes = tonnage_t * ((creo or 0.0) / 100.0) * (recovery / 100.0)
        tonnage = {
            "area_m2": area,
            "depth_m": depth,
            "bulk_density_t_m3": bulk_dens,
            "tonnage_t": tonnage_t,
            "treo_tonnes": treo_tonnes,
            "recoverable_treo_tonnes": rec_treo,
            "creo_tonnes": creo_tonnes,
            "metallurgical_recovery_pct": recovery,
        }

    # Economic
    eco_tier, hree_premium = economic_tier(treo, deposit, hreo_treo)
    cut_off_table_key = deposit.lower().replace(" ", "_").replace("-", "_")
    if "iac" in cut_off_table_key or "clay" in cut_off_table_key:
        cut_off_table_key = "iac_clay"
    elif "carbonatite" in cut_off_table_key:
        cut_off_table_key = "carbonatite"
    elif "alkaline" in cut_off_table_key:
        cut_off_table_key = "alkaline"
    elif "placer" in cut_off_table_key:
        cut_off_table_key = "placer"
    else:
        cut_off_table_key = "carbonatite"
    cut_off = CUT_OFF[cut_off_table_key]

    met_risks = []
    if zone.get("high_thorium", False):
        met_risks.append("High Th content (>0.1% ThO2) — radiation waste classification")
    if zone.get("mixed_minerals", False):
        met_risks.append("Mixed REE minerals — complex separation circuit")
    if zone.get("fluorapatite_hosted", False):
        met_risks.append("Fluorapatite-hosted REE — difficult processing")

    economic = {
        "deposit_type": deposit,
        "cut_off_treo_pct": cut_off["economic_lo"],
        "economic_tier": eco_tier,
        "hree_premium_applied": hree_premium,
        "metallurgical_risk_flags": met_risks,
    }

    # Risk
    r = risk_matrix(zone, verified_tier, eco_tier)

    # Classification
    classification, class_note = classify_resource(verified_tier, has_cp)

    # Warnings
    warnings = []
    if verified_tier == "unreliable":
        warnings.append("Data quality insufficient — re-assay required before any assessment")
    if depth == 50.0 and not zone.get("depth_m"):
        warnings.append("Depth assumed 50 m (not provided) — highest-uncertainty parameter")

    return {
        "zone_id": zid,
        "input": zone,
        "verified_confidence_tier": verified_tier,
        "confidence_flag": flag,
        "grade_summary": grade_summary,
        "tonnage": tonnage,
        "economic": economic,
        "risk": r,
        "classification": classification,
        "classification_note": class_note,
        "phrasing": phrasing(verified_tier, eco_tier),
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(description="REE ore grade economic assessment.")
    parser.add_argument("--input", required=True, help="Input JSON or CSV with zone data")
    parser.add_argument("--output", required=True, help="Output JSON report path")
    parser.add_argument(
        "--basket-price", type=float, default=30.0, help="TREO basket price USD/kg"
    )
    parser.add_argument(
        "--metallurgical-recovery",
        type=float,
        default=None,
        help="Global recovery override (%)",
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"Error: file not found: {in_path}", file=sys.stderr)
        sys.exit(1)

    if in_path.suffix.lower() == ".csv":
        df = pd.read_csv(in_path)
        zones = df.to_dict(orient="records")
    else:
        with open(in_path) as f:
            zones = json.load(f)
        if isinstance(zones, dict):
            zones = [zones]

    report = {
        "report_date": date.today().isoformat(),
        "basket_price_usd_kg": args.basket_price,
        "zones": [assess_zone(z, args.basket_price, args.metallurgical_recovery) for z in zones],
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
