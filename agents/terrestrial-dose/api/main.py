"""
Euro-Dose API v2.0 — Stage 2: per-point data reading + fixed dose logic
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

from models.sample_point import sample_raw_data, analyze_point
from analysis.short_report import build_short_report
from dose_core.dose_calculation_core import (
    polygon_dose_fingerprint,
    WORLD_AVG_DOSE,
    WHO_RN_ACTION,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("eurodose.api")

app = FastAPI(
    title="European Terrestrial Dose Indicator API",
    version="2.0.0",
    description="Stage 1: downloads open datasets. Stage 2: reads cached data at point, feeds fixed dose logic.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0", "stage": "Stage 2: per-point data reading + fixed logic"}


@app.get("/dose")
def dose_endpoint(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
):
    # 1. Fetch raw data at this point (from cache or live)
    raw = sample_raw_data(lat, lon)

    lith = raw.get("lithology_code", "Su")
    if lith in ("water", "Wa", "ice", "Ice"):
        return JSONResponse({
            "lat": lat, "lon": lon, "glim": lith,
            "arms_mSv_yr": {"radon": 0, "thoron": 0, "gamma": 0},
            "total_terrestrial_mSv_yr": 0,
            "risk": {"tier": "GREEN", "rationale": ["Water/ice — no terrestrial dose"], "flags": []},
            "report_short": ["Water/ice body — no terrestrial dose."],
            "confidence": {"level": "n/a", "reason": ""},
            "raw_table": raw,
        })

    # 2. Run the fixed dose logic on the raw table
    result = analyze_point(raw)

    # 3. Build short report
    report = build_short_report(result, lat, lon)

    return JSONResponse({
        "lat": lat, "lon": lon,
        "cell_m": result["cell_m"],
        "arms_mSv_yr": result["arms_mSv_yr"],
        "total_terrestrial_mSv_yr": result["total_terrestrial_mSv_yr"],
        "risk": result["risk"],
        "factors": result["factors"],
        "report_short": report,
        "confidence": result["confidence"],
        "activities": result["activities"],
        "gamma_rate_nGy_h": result["gamma_rate_nGy_h"],
        "radon_Bq_m3_est": result["radon_Bq_m3_est"],
        "raeq_Bq_kg": result["raeq_Bq_kg"],
        "provenance": result["provenance"],
        "raw_table": raw,
    })


@app.get("/dose/bbox")
def dose_bbox(
    south: float = Query(..., ge=-90, le=90),
    west: float = Query(..., ge=-180, le=180),
    north: float = Query(..., ge=-90, le=90),
    east: float = Query(..., ge=-180, le=180),
    step: float = Query(0.5, ge=0.1, le=5.0),
):
    features = []
    lat = south
    while lat <= north:
        lng = west
        while lng <= east:
            raw = sample_raw_data(lat, lng)
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
