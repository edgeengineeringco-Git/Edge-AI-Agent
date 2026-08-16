"""FastAPI backend — Ireland-only Terrestrial Dose Indicator."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from models.sample_point import sample_point
from models.analyze_point import analyze_point
from analysis.short_report import build_short_report

app = FastAPI(title="Irish Terrestrial Dose Indicator", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

IRISH_BBOX = {"lat_min": 51.4, "lat_max": 55.4, "lon_min": -10.6, "lon_max": -5.3}


def _in_ireland(lat, lon):
    return IRISH_BBOX["lat_min"] <= lat <= IRISH_BBOX["lat_max"] and IRISH_BBOX["lon_min"] <= lon <= IRISH_BBOX["lon_max"]


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0", "scope": "Ireland only"}


@app.get("/dose")
def get_dose(lat: float = Query(..., ge=-90, le=90), lon: float = Query(..., ge=-180, le=180)):
    if not _in_ireland(lat, lon):
        return {"error": "Outside Ireland bounding box (51.4-55.4N, 10.6-5.3W)", "lat": lat, "lon": lon}
    raw = sample_point(lat, lon)
    result = analyze_point(raw)
    report = build_short_report(result, lat, lon)
    a = result["activities"]
    raeq = a["A_Ra226"] + 1.43 * a["A_Th232"] + 0.077 * a["A_K40"]
    return {
        "lat": lat, "lon": lon, "cell_m": result["cell_m"],
        "arms_mSv_yr": result["arms_mSv_yr"],
        "total_terrestrial_mSv_yr": result["total_terrestrial_mSv_yr"],
        "risk": result["risk"], "factors": result["factors"],
        "report_short": report, "confidence": result["confidence"],
        "activities": result["activities"],
        "gamma_rate_nGy_h": result["gamma_rate_nGy_h"],
        "radon_Bq_m3_est": result["radon_Bq_m3_est"],
        "raeq_Bq_kg": round(raeq, 1),
        "provenance": result["provenance"],
        "tellus_available": raw.get("tellus_eU_ppm") is not None,
        "epa_radon_available": raw.get("epa_radon_est_bqm3") is not None,
    }


@app.get("/dose/bbox")
def get_dose_grid(
    lat_min: float = Query(...), lat_max: float = Query(...),
    lon_min: float = Query(...), lon_max: float = Query(...),
    step_km: float = Query(2.0, ge=0.5, le=20),
):
    results = []
    step = step_km / 111.0
    lat = lat_min
    while lat < lat_max:
        lon = lon_min
        while lon < lon_max:
            if _in_ireland(lat, lon):
                raw = sample_point(lat, lon)
                result = analyze_point(raw)
                results.append({
                    "lat": round(lat, 4), "lon": round(lon, 4),
                    "tier": result["risk"]["tier"],
                    "total": round(result["total_terrestrial_mSv_yr"], 3),
                    "tellus": raw.get("tellus_eU_ppm") is not None,
                })
            lon += step
        lat += step
    return {"grid": results, "step_km": step_km, "count": len(results)}
