"""
Irish Terrestrial Dose Indicator API v3.0
=========================================
Ireland-only, measurement-grade dose estimation.
Tellus K/U/Th used where available. EPA radon map as validation.
Irish 200 Bq/m³ radon action level (stricter than EU 300).
"""

from __future__ import annotations
import os
import sys
import json
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from dose_core.dose_calculation_core import (
    polygon_dose_fingerprint,
    RISK,
    WORLD_AVG_DOSE,
    WHO_RN_ACTION,
    IRISH_RN_ACTION,
    RADON_IRISH_FACTOR,
    radon_inhalation_dose_irish,
    risk_class_irish,
    radium_equivalent,
)
from models.analyze_point import analyze_point
from ingest.ireland_data import IrelandDataLayers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("irishdose.api")

app = FastAPI(
    title="Irish Terrestrial Dose Indicator API",
    version="3.0.0",
    description="Ireland-only interactive terrestrial radiation dose estimation. Tellus measured K/U/Th + EPA radon validation.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_data_layers: IrelandDataLayers | None = None


def get_data_layers() -> IrelandDataLayers:
    global _data_layers
    if _data_layers is None:
        _data_layers = IrelandDataLayers()
    return _data_layers


IRELAND_BBOX = (-10.6, 51.4, -5.3, 55.4)


def _in_ireland(lon: float, lat: float) -> bool:
    w, s, e, n = IRELAND_BBOX
    return s <= lat <= n and w <= lon <= e


@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "3.0.0",
        "name": "Irish Terrestrial Dose Indicator",
        "coverage": "Ireland only (51.4–55.4°N, 10.6–5.3°W)",
        "radon_action_level_Bq_m3": IRISH_RN_ACTION,
    }


@app.get("/sample")
def sample_point(
    lat: float = Query(..., ge=51.4, le=55.4),
    lon: float = Query(..., ge=-10.6, le=-5.3),
):
    """Return the raw Irish data table for a point."""
    if not _in_ireland(lon, lat):
        return JSONResponse({"error": "Point outside Ireland"}, status_code=400)
    layers = get_data_layers()
    raw = layers.sample(lon, lat)
    return {"lat": lat, "lon": lon, "raw_table": raw}


@app.get("/dose")
def dose_endpoint(
    lat: float = Query(..., ge=51.4, le=55.4),
    lon: float = Query(..., ge=-10.6, le=-5.3),
):
    """Full dose analysis for an Irish point."""
    if not _in_ireland(lon, lat):
        return JSONResponse({"error": "Point outside Ireland"}, status_code=400)

    layers = get_data_layers()
    raw = layers.sample(lon, lat)

    # Water/ice check
    lith = raw.get("lithology_code", "Su")
    if lith in ("water", "Wa", "ice", "Ice"):
        return JSONResponse({
            "lat": lat, "lon": lon, "glim": lith,
            "arms_mSv_yr": {"radon": 0, "thoron": 0, "gamma": 0},
            "total_terrestrial_mSv_yr": 0,
            "risk": {"tier": "GREEN", "rationale": ["Water/ice — no terrestrial dose"], "flags": []},
            "report_short": {"lines": ["Water/ice body — no terrestrial dose."]},
            "confidence": {"level": "n/a", "reason": "n/a"},
            "raw_table": raw,
        })

    # Run the smart analysis
    result = analyze_point(raw)

    # Build report
    report_short = _generate_report(result)
    why = _generate_why(result)
    recs = _generate_recommendations(result)

    return JSONResponse({
        "lat": lat, "lon": lon,
        "glim": lith,
        "region": raw.get("lithology_description", "Unknown"),
        "national_survey": "GSI IE_100k",
        "arms_mSv_yr": result["arms_mSv_yr"],
        "total_terrestrial_mSv_yr": result["total_terrestrial_mSv_yr"],
        "gamma_rate_nGy_h": result["gamma_rate_nGy_h"],
        "activities_Bq_kg": result["activities"],
        "indices": {
            "raeq": round(radium_equivalent(
                result["activities"]["A_Ra226"],
                result["activities"]["A_Th232"],
                result["activities"]["A_K40"]
            ), 1),
            "I_gamma": round(
                result["activities"]["A_Ra226"] / 370 +
                result["activities"]["A_Th232"] / 259 +
                result["activities"]["A_K40"] / 4810, 4
            ),
            "indoor_Rn": round(result["radon_Bq_m3_est"], 1),
        },
        "risk": result["risk"],
        "analysis": {
            "dominant": report_short["dominant"],
            "share_pct": report_short["share_pct"],
            "why": why,
            "expected_or_anomaly": "expected" if result["total_terrestrial_mSv_yr"] <= 2.2 else ("elevated" if result["total_terrestrial_mSv_yr"] <= 5 else "anomaly"),
            "vs_world_avg": report_short["vs_world_avg"],
        },
        "report_short": report_short,
        "recommendations": recs,
        "confidence": result["confidence"],
        "provenance": result["provenance"],
        "cell_m": result["cell_m"],
        "map_scale": "1:100k",
        "meets_target_resolution": True,
        "factors": result["factors"],
        "residuals": result.get("residuals", {}),
        "raw_table": raw,
    })


def _generate_report(result: dict) -> dict:
    arms = result["arms_mSv_yr"]
    total = result["total_terrestrial_mSv_yr"]
    acts = result["activities"]
    risk = result["risk"]

    entries = [("radon", arms["radon"]), ("thoron", arms["thoron"]), ("gamma", arms["gamma"])]
    dominant = max(entries, key=lambda x: x[1])
    share_pct = round((dominant[1] / total * 100)) if total > 0 else 0

    lines = []
    if dominant[0] == "gamma":
        lines.append(f"Gamma dose ({arms['gamma']:.2f} mSv/yr, {share_pct}% of total) dominates.")
    elif dominant[0] == "radon":
        lines.append(f"Radon inhalation ({arms['radon']:.2f} mSv/yr, {share_pct}% of total) dominates.")
    else:
        lines.append(f"Thoron inhalation ({arms['thoron']:.2f} mSv/yr, {share_pct}% of total) dominates.")

    lines.append(f"Geology: {result['raw_table'].get('lithology_description', 'Unknown')}. Cell size: 100m (scale: 1:100k).")
    lines.append(f"Activities: Ra-226={acts['A_Ra226']:.0f}, Th-232={acts['A_Th232']:.0f}, K-40={acts['A_K40']:.0f} Bq/kg.")
    lines.append(f"Indoor Rn: {result['radon_Bq_m3_est']:.0f} Bq/m³ (WHO: {WHO_RN_ACTION}, Irish action: {IRISH_RN_ACTION}).")
    lines.append(f"Gamma rate: {result['gamma_rate_nGy_h']:.0f} nGy/h (world avg: 59).")
    ratio = total / WORLD_AVG_DOSE
    lines.append(f"Total ({total:.2f} mSv/yr) is {ratio:.1f}× UNSCEAR avg ({WORLD_AVG_DOSE}) — {risk['tier']}.")

    conf = result["confidence"]
    conf_level = conf["level"]
    conf_reason = conf["reason"]
    lines.append(f"Confidence: {conf_level} — {conf_reason}.")

    return {
        "lines": lines,
        "dominant": dominant[0],
        "share_pct": share_pct,
        "vs_world_avg": round(ratio, 2),
        "lithology_label": result["raw_table"].get("lithology_description", "Unknown"),
        "cell_m": 100,
        "map_scale": "100k",
    }


def _generate_why(result: dict) -> list[str]:
    arms = result["arms_mSv_yr"]
    total = result["total_terrestrial_mSv_yr"]
    acts = result["activities"]
    risk = result["risk"]
    raw = result["raw_table"]

    why = []
    entries = [("radon", arms["radon"]), ("thoron", arms["thoron"]), ("gamma", arms["gamma"])]
    dominant = max(entries, key=lambda x: x[1])
    share_pct = round((dominant[1] / total * 100)) if total > 0 else 0

    if dominant[0] == "gamma":
        why.append(f"Gamma ({arms['gamma']:.2f} mSv/yr, {share_pct}%) dominates — natural radioactivity in {raw.get('lithology_description', 'substrate')}.")
        if acts["A_K40"] > 800:
            why.append(f"High K-40 ({acts['A_K40']:.0f} Bq/kg) indicates K-feldspar-rich mineralogy.")
    elif dominant[0] == "radon":
        why.append(f"Radon ({arms['radon']:.2f} mSv/yr, {share_pct}%) dominates — {raw.get('lithology_description', 'substrate')} with Ra-226={acts['A_Ra226']:.0f} Bq/kg.")
        if result["radon_Bq_m3_est"] >= 200:
            why.append(f"Indoor radon ({result['radon_Bq_m3_est']:.0f} Bq/m³) exceeds Irish action level (200).")
        elif result["radon_Bq_m3_est"] >= 100:
            why.append(f"Indoor radon ({result['radon_Bq_m3_est']:.0f} Bq/m³) exceeds WHO reference (100).")
    else:
        why.append(f"Thoron ({arms['thoron']:.2f} mSv/yr, {share_pct}%) dominates.")
        if acts["A_Th232"] > 50:
            why.append(f"High Th-232 ({acts['A_Th232']:.0f} Bq/kg) triggers non-linear thoron enhancement.")

    if total > 5:
        why.append(f"Total dose ({total:.2f} mSv/yr) is significantly above UNSCEAR average (2.2).")
    elif total > 2.2:
        why.append(f"Total dose ({total:.2f} mSv/yr) is above UNSCEAR average (2.2).")

    return why


def _generate_recommendations(result: dict) -> list[dict]:
    recs = []
    total = result["total_terrestrial_mSv_yr"]
    tier = result["risk"]["tier"]
    conf = result["confidence"]
    acts = result["activities"]

    if tier == "RED":
        recs.append({"priority": "URGENT", "text": "Radon mitigation (sub-slab depressurisation) if indoor Rn exceeds Irish action level 200 Bq/m³."})
    if conf["level"] in ("low", "medium"):
        recs.append({"priority": "HIGH", "text": "Integrate Tellus airborne radiometric to replace geology-prior estimates where available."})
    if result["radon_Bq_m3_est"] >= 100:
        recs.append({"priority": "HIGH", "text": f"Deploy indoor radon detectors to validate geogenic estimate of {result['radon_Bq_m3_est']:.0f} Bq/m³."})
    if acts["A_Th232"] > 100:
        recs.append({"priority": "MEDIUM", "text": "Thoron measurement with grab-sampling. Consider CeBr₃ drone spectrometry for Th-232 mapping."})
    if tier == "GREEN" and conf["level"] == "high":
        recs.append({"priority": "LOW", "text": "No immediate action. Periodic monitoring every 5 years sufficient."})

    return recs


@app.get("/dose/bbox")
def dose_bbox(
    south: float = Query(..., ge=51.4, le=55.4),
    west: float = Query(..., ge=-10.6, le=-5.3),
    north: float = Query(..., ge=51.4, le=55.4),
    east: float = Query(..., ge=-10.6, le=-5.3),
    step: float = Query(0.1, ge=0.05, le=0.5),
):
    """Grid sampling across an Irish bbox."""
    features = []
    layers = get_data_layers()
    lat = south
    while lat <= north:
        lng = west
        while lng <= east:
            raw = layers.sample(lng, lat)
            lith = raw.get("lithology_code", "Su")
            if lith not in ("water", "Wa", "ice", "Ice"):
                result = analyze_point(raw)
                features.append({
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [lng, lat]},
                    "properties": {
                        "dose": result["total_terrestrial_mSv_yr"],
                        "tier": result["risk"]["tier"],
                        "lithology": lith,
                        "region": raw.get("lithology_description", "Unknown"),
                    },
                })
            lng += step
        lat += step

    return JSONResponse({
        "type": "FeatureCollection",
        "features": features,
        "meta": {"step_deg": step, "bbox": [south, west, north, east]},
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
