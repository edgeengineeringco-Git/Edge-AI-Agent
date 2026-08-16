"""
models/sample_point.py

1. sample_raw_data(lat, lon) — fetches all raw values at a point, returns a dict matching RAW_TABLE_SCHEMA.
2. analyze_point(raw) — runs the fixed dose logic on the raw table (Steps A–H).
"""

from __future__ import annotations
import sys
import os
from typing import Dict, Any, Optional

# Ensure dose_core is importable when running from repo root or agent scope
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

from dose_core.dose_calculation_core import (
    LITHOLOGY_ACTIVITIES, LITHOLOGY_FACTOR, glim_name,
    ppm_to_bqkg, lithology_to_activities, lithology_factor,
    external_gamma_dose_rate, annual_external_dose,
    geogenic_radon_potential, geogenic_thoron_potential,
    radon_inhalation_dose, thoron_inhalation_dose,
    radium_equivalent, gamma_activity_index,
    excess_lifetime_cancer_risk, risk_class,
    polygon_dose_fingerprint,
)

from ingest.point_sampler import PointSampler


# Reusable sampler instance
_sampler: Optional[PointSampler] = None

def _get_sampler() -> PointSampler:
    global _sampler
    if _sampler is None:
        _sampler = PointSampler()
    return _sampler


def sample_raw_data(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetch raw data at this point from all ingest modules.
    Returns a dict matching RAW_TABLE_SCHEMA. Missing values = None.
    """
    sampler = _get_sampler()
    point_data = sampler.sample(lon, lat)

    lith = point_data.get("lithology", {})
    sg = point_data.get("soilgrids", {})
    geo = point_data.get("geochemistry", {})
    val = point_data.get("validation", {})
    dem = point_data.get("dem", {})

    # Map SoilGrids layers if available
    sg_layers = sg.get("layers", {})
    clay = _extract_sg(sg_layers, "clay", "0-5cm")
    sand = _extract_sg(sg_layers, "sand", "0-5cm")
    silt = _extract_sg(sg_layers, "silt", "0-5cm")
    bdod = _extract_sg(sg_layers, "bdod", "0-5cm")

    # Nearest geochemistry sample
    geo_sample = {}
    if geo.get("status") == "available" and geo.get("samples"):
        geo_sample = geo["samples"][0]

    # Nearest validation measurement
    val_sample = {}
    if val.get("status") == "available" and val.get("measurements"):
        val_sample = val["measurements"][0]

    # JRC / validation mapping
    jrc_rn = val_sample.get("indoor_rn_Bq_m3")

    # FOREGS-style validation from geochemistry samples (named U_ppm, Th_ppm, K_pct)
    foregs_u = geo_sample.get("U_ppm")
    foregs_th = geo_sample.get("Th_ppm")
    foregs_k = geo_sample.get("K_pct")

    raw = {
        "lat": lat,
        "lon": lon,
        "map_scale": lith.get("resolution", "1M"),
        "lithology_code": lith.get("glim_code", "Su"),
        "lithology_description": lith.get("region", "Unknown"),
        "geology_age": None,
        "soil_clay_pct": clay,
        "soil_sand_pct": sand,
        "soil_silt_pct": silt,
        "soil_bulk_density": bdod,
        "depth_to_bedrock_m": None,
        "soil_ph": None,
        "elevation_m": dem.get("elevation_m"),
        "slope_deg": None,
        "aspect_deg": None,
        "nearest_fault_name": None,
        "nearest_fault_type": None,
        "dist_nearest_fault_m": 5000,  # model default
        "s2_b2_blue": None,
        "s2_b3_green": None,
        "s2_b4_red": None,
        "s2_b8_nir": None,
        "s2_b11_swir1": None,
        "s2_b12_swir2": None,
        "s1_vv_db": None,
        "s1_vh_db": None,
        "soil_moisture_m3m3": None,
        "corine_code": None,
        "corine_label": None,
        "era5_temp_c": None,
        "era5_pressure_hpa": None,
        "era5_humidity_pct": None,
        "era5_precip_mm": None,
        "era5_wind_ms": None,
        "emag2_magnetic_nt": None,
        "wgm_gravity_mgal": None,
        "population_count": None,
        "foregs_eU_ppm": foregs_u,
        "foregs_eTh_ppm": foregs_th,
        "foregs_K_pct": foregs_k,
        "jrc_indoor_rn": jrc_rn,
        "jrc_gamma_rate": None,
        "jrc_soil_K": None,
        "jrc_soil_U": None,
        "jrc_soil_Th": None,
    }
    return raw


def _extract_sg(layers: Dict, name: str, depth_label: str) -> Optional[float]:
    layer = layers.get(name, {})
    val = layer.get(depth_label)
    if val is not None:
        # SoilGrids v2.0 returns values scaled by 10 for some properties
        return float(val) * 0.1 if name in ("clay", "sand", "silt") else float(val)
    return None


def analyze_point(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Run the fixed dose logic on the raw data table. Returns doses + analysis."""

    # STEP A — Derive activities from raw lithology (or measured override)
    lith = raw.get("lithology_code", "Su")
    prior = lithology_to_activities(lith) or {"A_Ra226": 35, "A_Th232": 30, "A_K40": 420}
    A_Ra = prior["A_Ra226"]
    A_Th = prior["A_Th232"]
    A_K  = prior["A_K40"]
    activity_source = f"geology prior ({glim_name(lith)})"

    # Override with FOREGS if available
    if raw.get("foregs_eU_ppm") is not None:
        A_Ra = raw["foregs_eU_ppm"] * 12.22
        activity_source = "FOREGS measured"
    if raw.get("foregs_eTh_ppm") is not None:
        A_Th = raw["foregs_eTh_ppm"] * 4.06
        activity_source = "FOREGS measured"
    if raw.get("foregs_K_pct") is not None:
        A_K = raw["foregs_K_pct"] * 313.0
        activity_source = "FOREGS measured"

    # Override with JRC soil radionuclides if available
    if raw.get("jrc_soil_U") is not None:
        A_Ra = raw["jrc_soil_U"]
        activity_source = "JRC measured"
    if raw.get("jrc_soil_Th") is not None:
        A_Th = raw["jrc_soil_Th"]
        activity_source = "JRC measured"
    if raw.get("jrc_soil_K") is not None:
        A_K = raw["jrc_soil_K"]
        activity_source = "JRC measured"

    # STEP B — Derive permeability from raw soil texture
    sand = raw.get("soil_sand_pct", 50) or 50
    clay = raw.get("soil_clay_pct", 20) or 20
    if sand > 60:
        permeability = 1.5e-13
        perm_note = "high (sandy)"
    elif clay > 35:
        permeability = 0.3e-13
        perm_note = "low (clay-rich)"
    else:
        permeability = 1.0e-13
        perm_note = "moderate"

    # STEP C — Structural factors from raw data
    dist_fault = raw.get("dist_nearest_fault_m", 1000) or 1000
    slope = raw.get("slope_deg", 0) or 0
    s1_vv = raw.get("s1_vv_db", -10) or -10
    lineament_density = min(2.0, max(0.0, abs(s1_vv + 10) / 10 + slope / 30))

    # STEP D — S2 indices from raw bands
    b4 = raw.get("s2_b4_red", 0.1) or 0.1
    b8 = raw.get("s2_b8_nir", 0.1) or 0.1
    b11 = raw.get("s2_b11_swir1", 0.1) or 0.1
    b12 = raw.get("s2_b12_swir2", 0.1) or 0.1
    b2 = raw.get("s2_b2_blue", 0.05) or 0.05
    ndvi = (b8 - b4) / (b8 + b4) if (b8 + b4) > 0 else 0
    clay_ratio = b11 / b12 if b12 > 0 else 0
    ferric_ratio = b4 / b2 if b2 > 0 else 0

    # STEP E — Seasonal factor from raw ERA5
    temp = raw.get("era5_temp_c", 10) or 10
    moisture = raw.get("soil_moisture_m3m3", 0.2) or 0.2
    is_winter = temp < 5
    season_factor = 1.2 if is_winter else 1.0

    # STEP F — Compute doses via the fixed core module
    lf = lithology_factor(lith)
    fp = polygon_dose_fingerprint(
        lithology=lith,
        permeability=permeability,
        dist_fault_m=dist_fault,
        lineament_density=lineament_density,
        radon_method="eubss",
    )

    # STEP G — Validation & confidence
    confidence_level = "medium"
    confidence_reason = f"geology prior ({glim_name(lith)}); no measurement nearby"
    residuals = {}
    if raw.get("jrc_indoor_rn") is not None:
        predicted_rn = fp["radon_Bq_m3_est"]
        measured_rn = raw["jrc_indoor_rn"]
        residuals["radon"] = predicted_rn - measured_rn
        if abs(residuals["radon"]) < measured_rn * 0.3:
            confidence_level = "high"
            confidence_reason = f"JRC indoor radon nearby; residual {residuals['radon']:.0f} Bq/m3"
    if raw.get("jrc_gamma_rate") is not None:
        predicted_gamma = fp["gamma_rate_nGy_h"]
        measured_gamma = raw["jrc_gamma_rate"]
        residuals["gamma"] = predicted_gamma - measured_gamma

    # STEP H — Build factor list for the report
    factors = []
    factors.append({"id": "lithology", "value": f"{lith} ({glim_name(lith)})",
                    "effect": "Rn Tn gamma source", "direction": "varies",
                    "source": "EGDI geology", "resolution": raw.get("map_scale","1:100k")})
    factors.append({"id": "permeability", "value": f"{perm_note} ({permeability:.1e})",
                    "effect": "Rn transport", "direction": "up" if sand>60 else "down" if clay>35 else "neutral",
                    "source": "SoilGrids 250m", "resolution": "250m"})
    factors.append({"id": "fault", "value": f"{dist_fault:.0f} m",
                    "effect": "Rn pathway", "direction": "up" if dist_fault<500 else "neutral",
                    "source": "GEM faults", "resolution": "vector"})
    factors.append({"id": "ndvi", "value": f"{ndvi:.2f}",
                    "effect": "gamma shield", "direction": "down" if ndvi>0.4 else "up" if ndvi<0.2 else "neutral",
                    "source": "Sentinel-2 10m", "resolution": "10m"})
    factors.append({"id": "moisture", "value": f"{moisture:.2f} m3/m3",
                    "effect": "Rn exhalation", "direction": "down" if moisture>0.3 else "up" if moisture<0.15 else "neutral",
                    "source": "ESA CCI", "resolution": "1-10km"})
    factors.append({"id": "season", "value": "winter" if is_winter else "summer",
                    "effect": "indoor Rn (stack)", "direction": "up" if is_winter else "neutral",
                    "source": "ERA5", "resolution": "~10km"})
    factors.append({"id": "activities", "value": f"Ra={A_Ra:.0f} Th={A_Th:.0f} K={A_K:.0f} Bq/kg",
                    "effect": "source term", "direction": "varies",
                    "source": activity_source, "resolution": "—"})

    cell_m = 100 if "100" in str(raw.get("map_scale","")) else 50

    return {
        "raw_table": raw,
        "factors": factors,
        "arms_mSv_yr": fp["arms_mSv_yr"],
        "total_terrestrial_mSv_yr": fp["total_terrestrial_mSv_yr"],
        "risk": fp["risk"],
        "activities": {"A_Ra226": A_Ra, "A_Th232": A_Th, "A_K40": A_K},
        "gamma_rate_nGy_h": fp["gamma_rate_nGy_h"],
        "radon_Bq_m3_est": fp["radon_Bq_m3_est"],
        "thoron_gas_Bq_m3_est": fp["thoron_gas_Bq_m3_est"],
        "raeq_Bq_kg": fp["raeq_Bq_kg"],
        "i_gamma": fp["i_gamma"],
        "confidence": {"level": confidence_level, "reason": confidence_reason},
        "residuals": residuals,
        "provenance": fp["provenance"],
        "ndvi": ndvi,
        "clay_ratio": clay_ratio,
        "cell_m": cell_m,
    }
