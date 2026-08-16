"""
Analyze Point — the smart agent (Steps A–H).
Reads the raw table and computes derived values.
None of these derived values exist in the table — the agent creates them.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dose_core.dose_calculation_core import (
    LITHOLOGY_ACTIVITIES, LITHOLOGY_FACTOR, glim_name,
    lithology_to_activities, lithology_factor,
    external_gamma_dose_rate, annual_external_dose,
    geogenic_radon_potential, geogenic_thoron_potential,
    radon_inhalation_dose, thoron_inhalation_dose,
    radium_equivalent, gamma_activity_index,
    excess_lifetime_cancer_risk, polygon_dose_fingerprint,
)

RADON_IRISH_FACTOR = 6.7 / 200.0  # Irish action level: 200 Bq/m3 -> 6.7 mSv/yr


def radon_inhalation_dose_irish(C_Rn):
    return C_Rn * RADON_IRISH_FACTOR


def risk_class_irish(E_mSv, C_Rn=None, raeq=None, gamma_rate=None):
    r = []
    f = []
    if E_mSv <= 2.2:
        t = "GREEN"
        r.append(f"{E_mSv:.2f}<=2.2")
    elif E_mSv <= 6.6:
        t = "AMBER"
        r.append(f"{E_mSv:.2f} 1-3x")
    else:
        t = "RED"
        r.append(f"{E_mSv:.2f}>3x")
    if C_Rn is not None and C_Rn >= 200:
        f.append(f"RADON_ACTION: {C_Rn:.0f}>=Irish 200")
        t = "RED"
    elif C_Rn is not None and C_Rn >= 100:
        f.append(f"RADON_ELEVATED: {C_Rn:.0f}>=WHO 100")
        if t == "GREEN":
            t = "AMBER"
    if raeq is not None and raeq >= 370:
        f.append(f"RAEQ_HIGH: {raeq:.0f}>=370")
        if t != "RED":
            t = "RED"
    if gamma_rate is not None and gamma_rate >= 1000:
        f.append(f"GAMMA_HIGH: {gamma_rate:.0f}>=1000")
        t = "RED"
    return {"tier": t, "rationale": r, "flags": f}


def analyze_point(raw):
    """Steps A–H: the smart agent analysis."""
    lith = raw.get("lithology_code", "Su")
    prior = lithology_to_activities(lith) or {"A_Ra226": 35, "A_Th232": 30, "A_K40": 420}
    A_Ra = prior["A_Ra226"]
    A_Th = prior["A_Th232"]
    A_K = prior["A_K40"]
    activity_source = f"geology prior ({glim_name(lith)})"

    # Step A: Tellus > GSI stream > lithology prior
    if raw.get("tellus_eU_ppm") is not None:
        A_Ra = raw["tellus_eU_ppm"] * 12.22
        activity_source = "Tellus airborne measured"
    if raw.get("tellus_eTh_ppm") is not None:
        A_Th = raw["tellus_eTh_ppm"] * 4.06
        activity_source = "Tellus airborne measured"
    if raw.get("tellus_K_pct") is not None:
        A_K = raw["tellus_K_pct"] * 313.0
        activity_source = "Tellus airborne measured"
    if raw.get("gsi_stream_U") is not None and "Tellus" not in activity_source:
        A_Ra = raw["gsi_stream_U"]
        activity_source = "GSI stream sediment"
    if raw.get("gsi_stream_Th") is not None and "Tellus" not in activity_source:
        A_Th = raw["gsi_stream_Th"]
    if raw.get("gsi_stream_K") is not None and "Tellus" not in activity_source:
        A_K = raw["gsi_stream_K"]

    # Step B: Teagasc > SoilGrids
    if raw.get("teagasc_permeability") is not None:
        permeability = raw["teagasc_permeability"]
        perm_note = "Teagasc"
    else:
        sand = raw.get("soil_sand_pct", 50) or 50
        clay = raw.get("soil_clay_pct", 20) or 20
        if sand > 60:
            permeability = 1.5e-13
            perm_note = "high (sandy)"
        elif clay > 35:
            permeability = 0.3e-13
            perm_note = "low (clay)"
        else:
            permeability = 1.0e-13
            perm_note = "moderate"

    # Step C: Structural
    dist_fault = raw.get("dist_nearest_fault_m", 1000) or 1000
    slope = raw.get("slope_deg", 0) or 0
    s1_vv = raw.get("s1_vv_db", -10) or -10
    lineament_density = min(2.0, max(0.0, abs(s1_vv + 10) / 10 + slope / 30))

    # Step D: S2 indices
    b4 = raw.get("s2_b4_red", 0.1) or 0.1
    b8 = raw.get("s2_b8_nir", 0.1) or 0.1
    b11 = raw.get("s2_b11_swir1", 0.1) or 0.1
    b12 = raw.get("s2_b12_swir2", 0.1) or 0.1
    ndvi = (b8 - b4) / (b8 + b4) if (b8 + b4) > 0 else 0

    # Step E: Seasonal
    temp = raw.get("era5_temp_c", 10) or 10
    moisture = raw.get("soil_moisture_m3m3", 0.2) or 0.2
    is_winter = temp < 5

    # Step F: Doses
    lf = lithology_factor(lith)
    C_Rn = raw.get("epa_radon_est_bqm3")
    fp = polygon_dose_fingerprint(
        lithology=lith,
        eU_ppm=raw.get("tellus_eU_ppm") or raw.get("gsi_stream_U"),
        eTh_ppm=raw.get("tellus_eTh_ppm") or raw.get("gsi_stream_Th"),
        K_pct=raw.get("tellus_K_pct") or raw.get("gsi_stream_K"),
        C_Rn=C_Rn, permeability=permeability,
        dist_fault_m=dist_fault, lineament_density=lineament_density,
        radon_method="eubss",
    )
    if C_Rn is not None:
        e_rn = radon_inhalation_dose_irish(C_Rn)
        fp["arms_mSv_yr"]["radon"] = e_rn
        fp["total_terrestrial_mSv_yr"] = (
            fp["arms_mSv_yr"]["radon"] + fp["arms_mSv_yr"]["thoron"] + fp["arms_mSv_yr"]["gamma"]
        )
        fp["radon_Bq_m3_est"] = C_Rn

    # Step G: Confidence
    conf_level = "medium"
    conf_reason = "geology prior; no measurement nearby"
    if raw.get("tellus_eU_ppm") is not None:
        conf_level = "high"
        conf_reason = "Tellus airborne radiometric (measured K/U/Th ~200m)"
    elif raw.get("gsi_stream_U") is not None:
        conf_level = "medium-high"
        conf_reason = "GSI stream sediment geochemistry"
    if raw.get("epa_radon_est_bqm3") is not None:
        conf_reason += "; EPA radon map (1km grid)"
    residuals = {}
    if raw.get("epa_radon_est_bqm3") is not None:
        residuals["radon"] = fp["radon_Bq_m3_est"] - raw["epa_radon_est_bqm3"]
    if raw.get("epa_gamma_rate_nGyh") is not None:
        residuals["gamma"] = fp["gamma_rate_nGy_h"] - raw["epa_gamma_rate_nGyh"]

    # Step H: Factors + risk
    factors = [
        {"id": "lithology", "value": f"{lith} ({glim_name(lith)})", "effect": "Rn Tn gamma source",
         "direction": "varies", "source": "GSI 1:100k", "resolution": "100m"},
        {"id": "activities", "value": f"Ra={A_Ra:.0f} Th={A_Th:.0f} K={A_K:.0f} Bq/kg",
         "effect": "source term", "direction": "varies", "source": activity_source,
         "resolution": "200m" if "Tellus" in activity_source else "—"},
        {"id": "permeability", "value": perm_note, "effect": "Rn transport",
         "direction": "up" if permeability > 1e-13 else ("down" if permeability < 0.5e-13 else "neutral"),
         "source": "Teagasc" if "Teagasc" in perm_note else "SoilGrids", "resolution": "250m"},
        {"id": "fault", "value": f"{dist_fault:.0f} m", "effect": "Rn pathway",
         "direction": "up" if dist_fault < 500 else "neutral", "source": "GSI/GEM", "resolution": "vector"},
        {"id": "epa_radon", "value": f"{C_Rn:.0f} Bq/m3" if C_Rn else "unavailable",
         "effect": "indoor Rn", "direction": "varies", "source": "EPA" if C_Rn else "—", "resolution": "1km"},
        {"id": "ndvi", "value": f"{ndvi:.2f}", "effect": "gamma shield",
         "direction": "down" if ndvi > 0.4 else ("up" if ndvi < 0.2 else "neutral"),
         "source": "Sentinel-2", "resolution": "10m"},
        {"id": "moisture", "value": f"{moisture:.2f}", "effect": "Rn exhalation",
         "direction": "down" if moisture > 0.3 else ("up" if moisture < 0.15 else "neutral"),
         "source": "ESA CCI", "resolution": "1-10km"},
        {"id": "season", "value": "winter" if is_winter else "summer", "effect": "indoor Rn",
         "direction": "up" if is_winter else "neutral", "source": "ERA5", "resolution": "~10km"},
    ]
    risk = risk_class_irish(
        fp["total_terrestrial_mSv_yr"], C_Rn,
        radium_equivalent(A_Ra, A_Th, A_K), fp["gamma_rate_nGy_h"],
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
        "confidence": {"level": conf_level, "reason": conf_reason},
        "residuals": residuals,
        "provenance": fp["provenance"],
        "cell_m": 100,
        "ndvi": ndvi,
    }
