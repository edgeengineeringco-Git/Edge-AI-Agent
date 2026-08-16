"""
Irish Terrestrial Dose — Smart Point Analysis
=============================================
Runs the fixed dose logic on the raw Irish data table.
Uses Tellus measured K/U/Th where available (measurement-grade).
EPA radon map as validation. Irish 200 Bq/m³ action level.
"""

from __future__ import annotations
from typing import Optional, Dict, List, Any

from dose_core.dose_calculation_core import (
    LITHOLOGY_ACTIVITIES,
    LITHOLOGY_FACTOR,
    GLIM_MAP,
    ppm_to_bqkg,
    lithology_to_activities,
    lithology_factor,
    external_gamma_dose_rate,
    annual_external_dose,
    geogenic_radon_potential,
    geogenic_thoron_potential,
    radon_from_grp,
    radon_inhalation_dose,
    thoron_inhalation_dose,
    radium_equivalent,
    gamma_activity_index,
    excess_lifetime_cancer_risk,
    polygon_dose_fingerprint,
    radon_inhalation_dose_irish,
    risk_class_irish,
)

# Irish radon action level = 200 Bq/m3 -> ~6.7 mSv/yr
RADON_IRISH_FACTOR = 6.7 / 200.0


def glim_name(lith: str) -> str:
    """Resolve GLiM code or lithology name to human-readable label."""
    key = lith
    if lith in LITHOLOGY_ACTIVITIES:
        return LITHOLOGY_ACTIVITIES[lith]["label"]
    mapped = GLIM_MAP.get(lith)
    if mapped and mapped in LITHOLOGY_ACTIVITIES:
        return LITHOLOGY_ACTIVITIES[mapped]["label"]
    return lith


def analyze_point(raw: dict) -> dict:
    """Run the fixed dose logic on the raw Irish data table."""

    # STEP A — Activities: Tellus measured > GSI stream sediment > lithology prior
    lith = raw.get("lithology_code", "Su")
    prior = lithology_to_activities(lith) or {"A_Ra226": 35, "A_Th232": 30, "A_K40": 420}
    A_Ra = prior["A_Ra226"]
    A_Th = prior["A_Th232"]
    A_K = prior["A_K40"]
    activity_source = f"geology prior ({glim_name(lith)})"

    # Tellus airborne radiometric = BEST source (measured K/U/Th)
    if raw.get("tellus_eU_ppm") is not None:
        A_Ra = raw["tellus_eU_ppm"] * 12.22
        activity_source = "Tellus airborne measured"
    if raw.get("tellus_eTh_ppm") is not None:
        A_Th = raw["tellus_eTh_ppm"] * 4.06
        activity_source = "Tellus airborne measured"
    if raw.get("tellus_K_pct") is not None:
        A_K = raw["tellus_K_pct"] * 313.0
        activity_source = "Tellus airborne measured"

    # GSI stream sediment = fallback measured
    if raw.get("gsi_stream_U") is not None and "Tellus" not in activity_source:
        A_Ra = raw["gsi_stream_U"]
        activity_source = "GSI stream sediment"
    if raw.get("gsi_stream_Th") is not None and "Tellus" not in activity_source:
        A_Th = raw["gsi_stream_Th"]
    if raw.get("gsi_stream_K") is not None and "Tellus" not in activity_source:
        A_K = raw["gsi_stream_K"]

    # STEP B — Permeability: Teagasc > SoilGrids
    if raw.get("teagasc_permeability") is not None:
        permeability = raw["teagasc_permeability"]
        perm_note = "Teagasc soil class"
    else:
        sand = raw.get("soil_sand_pct", 50) or 50
        clay = raw.get("soil_clay_pct", 20) or 20
        if sand > 60:
            permeability = 1.5e-13
            perm_note = "high (sandy, SoilGrids)"
        elif clay > 35:
            permeability = 0.3e-13
            perm_note = "low (clay, SoilGrids)"
        else:
            permeability = 1.0e-13
            perm_note = "moderate (SoilGrids)"

    # STEP C — Structural
    dist_fault = raw.get("dist_nearest_fault_m", 1000) or 1000
    slope = raw.get("slope_deg", 0) or 0
    s1_vv = raw.get("s1_vv_db", -10) or -10
    lineament_density = min(2.0, max(0.0, abs(s1_vv + 10) / 10 + slope / 30))

    # STEP D — S2 indices
    b4 = raw.get("s2_b4_red", 0.1) or 0.1
    b8 = raw.get("s2_b8_nir", 0.1) or 0.1
    b11 = raw.get("s2_b11_swir1", 0.1) or 0.1
    b12 = raw.get("s2_b12_swir2", 0.1) or 0.1
    b2 = raw.get("s2_b2_blue", 0.05) or 0.05
    ndvi = (b8 - b4) / (b8 + b4) if (b8 + b4) > 0 else 0
    clay_ratio = b11 / b12 if b12 > 0 else 0
    ferric_ratio = b4 / b2 if b2 > 0 else 0

    # STEP E — Seasonal
    temp = raw.get("era5_temp_c", 10) or 10
    moisture = raw.get("soil_moisture_m3m3", 0.2) or 0.2
    is_winter = temp < 5

    # STEP F — Doses via core module (use Irish radon method if EPA radon available)
    lf = lithology_factor(lith)

    # If EPA predicted radon exists, use it as the radon concentration
    C_Rn = raw.get("epa_radon_est_bqm3")  # EPA measured estimate

    fp = polygon_dose_fingerprint(
        lithology=lith,
        eU_ppm=raw.get("tellus_eU_ppm") or raw.get("gsi_stream_U"),
        eTh_ppm=raw.get("tellus_eTh_ppm") or raw.get("gsi_stream_Th"),
        K_pct=raw.get("tellus_K_pct") or raw.get("gsi_stream_K"),
        C_Rn=C_Rn,  # EPA radon if available, else geogenic
        permeability=permeability,
        dist_fault_m=dist_fault,
        lineament_density=lineament_density,
        radon_method="eubss",  # core uses EU BSS; adjust below for Irish
    )

    # If EPA radon used, recompute radon dose with Irish factor
    if C_Rn is not None:
        e_rn = radon_inhalation_dose_irish(C_Rn)
        fp["arms_mSv_yr"]["radon"] = e_rn
        fp["total_terrestrial_mSv_yr"] = (
            fp["arms_mSv_yr"]["radon"]
            + fp["arms_mSv_yr"]["thoron"]
            + fp["arms_mSv_yr"]["gamma"]
        )
        fp["radon_Bq_m3_est"] = C_Rn

    # STEP G — Confidence
    confidence_level = "medium"
    confidence_reason = "geology prior; no measurement nearby"
    if raw.get("tellus_eU_ppm") is not None:
        confidence_level = "high"
        confidence_reason = "Tellus airborne radiometric (measured K/U/Th)"
    elif raw.get("gsi_stream_U") is not None:
        confidence_level = "medium-high"
        confidence_reason = "GSI stream sediment geochemistry"
    if raw.get("epa_radon_est_bqm3") is not None:
        confidence_reason += "; EPA radon map (1km grid)"

    # Residuals
    residuals = {}
    if raw.get("epa_radon_est_bqm3") is not None:
        residuals["radon"] = fp["radon_Bq_m3_est"] - raw["epa_radon_est_bqm3"]
    if raw.get("epa_gamma_rate_nGyh") is not None:
        residuals["gamma"] = fp["gamma_rate_nGy_h"] - raw["epa_gamma_rate_nGyh"]

    # STEP H — Factors for report
    factors = [
        {
            "id": "lithology",
            "value": f"{lith} ({glim_name(lith)})",
            "effect": "Rn Tn γ source",
            "direction": "varies",
            "source": "GSI 1:100k",
            "resolution": "100m",
        },
        {
            "id": "activities",
            "value": f"Ra={A_Ra:.0f} Th={A_Th:.0f} K={A_K:.0f} Bq/kg",
            "effect": "source term",
            "direction": "varies",
            "source": activity_source,
            "resolution": "200m" if "Tellus" in activity_source else "—",
        },
        {
            "id": "permeability",
            "value": perm_note,
            "effect": "Rn transport",
            "direction": "up" if permeability > 1e-13 else "down" if permeability < 0.5e-13 else "neutral",
            "source": "Teagasc" if "Teagasc" in perm_note else "SoilGrids",
            "resolution": "250m",
        },
        {
            "id": "fault",
            "value": f"{dist_fault:.0f} m",
            "effect": "Rn pathway",
            "direction": "up" if dist_fault < 500 else "neutral",
            "source": "GSI faults",
            "resolution": "vector",
        },
        {
            "id": "epa_radon",
            "value": f"{C_Rn:.0f} Bq/m3" if C_Rn else "unavailable",
            "effect": "indoor Rn",
            "direction": "varies",
            "source": "EPA radon map" if C_Rn else "—",
            "resolution": "1km",
        },
        {
            "id": "ndvi",
            "value": f"{ndvi:.2f}",
            "effect": "gamma shield",
            "direction": "down" if ndvi > 0.4 else "up" if ndvi < 0.2 else "neutral",
            "source": "Sentinel-2 10m",
            "resolution": "10m",
        },
        {
            "id": "moisture",
            "value": f"{moisture:.2f} m³/m³",
            "effect": "Rn exhalation",
            "direction": "down" if moisture > 0.3 else "up" if moisture < 0.15 else "neutral",
            "source": "ESA CCI",
            "resolution": "1-10km",
        },
        {
            "id": "season",
            "value": "winter" if is_winter else "summer",
            "effect": "indoor Rn (stack)",
            "direction": "up" if is_winter else "neutral",
            "source": "ERA5",
            "resolution": "~10km",
        },
    ]

    # Recompute risk with Irish thresholds
    risk = risk_class_irish(
        fp["total_terrestrial_mSv_yr"],
        C_Rn,
        radium_equivalent(A_Ra, A_Th, A_K),
        fp["gamma_rate_nGy_h"],
    )

    return {
        "raw_table": raw,
        "factors": factors,
        "arms_mSv_yr": fp["arms_mSv_yr"],
        "total_terrestrial_mSv_yr": fp["total_terrestrial_mSv_yr"],
        "risk": risk,
        "activities": {"A_Ra226": A_Ra, "A_Th232": A_Th, "A_K40": A_K},
        "gamma_rate_nGy_h": fp["gamma_rate_nGy_h"],
        "radon_Bq_m3_est": fp["radon_Bq_m3_est"],
        "confidence": {"level": confidence_level, "reason": confidence_reason},
        "residuals": residuals,
        "provenance": fp["provenance"],
        "cell_m": 100,
        "ndvi": ndvi,
    }
