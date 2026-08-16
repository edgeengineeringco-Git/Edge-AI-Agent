"""
Irish Terrestrial Dose Indicator - Backend API
================================================
Serves /dose, /dose/bbox, /health endpoints matching the frontend contract.

Install:
    pip install fastapi uvicorn numpy rasterio shapely geopandas cachetools requests

Run:
    uvicorn dose_backend:app --host 0.0.0.0 --port 8000 --reload

Data layout expected (see DATA_DIR below):
    data/
      gsi_bedrock_100k.tif        # lithology class raster, EPSG:4326, ~100m
      tellus_radiometric_k.tif    # K (%) raster
      tellus_radiometric_u.tif    # eU (ppm) raster
      tellus_radiometric_th.tif   # eTh (ppm) raster
      epa_radon_map.tif           # predicted radon Bq/m3, 1km grid
      teagasc_soil_permeability.tif  # permeability class raster
      gsi_faults.geojson          # fault lines, EPSG:4326
      corine_landcover.tif        # land cover code
      sentinel2_ndvi.tif          # NDVI, 10m (optional, cached)
      esa_cci_soil_moisture.tif   # volumetric soil moisture (optional)
      era5_season.json            # {"season": "winter"} - updated externally

If a file is missing, the module falls back to a synthetic/lithology-prior
model so the API still runs end-to-end for development.
"""

from __future__ import annotations

import json
import math
import os
import time
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Optional

import numpy as np
from cachetools import TTLCache
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ======================================================================
# CONFIG
# ======================================================================

DATA_DIR = Path(os.environ.get("DOSE_DATA_DIR", "./data"))
CELL_M_DEFAULT = 100

# UNSCEAR 2024 dose conversion coefficients (approximate, published values)
DCC_GAMMA_NGY_H_PER_BQ_KG = {
    "Ra226": 0.462,   # nGy/h per Bq/kg
    "Th232": 0.604,
    "K40": 0.0417,
}
GAMMA_NGY_H_TO_MSV_YR = 8760 * 0.7 * 1e-6  # occupancy factor 0.7, hours/yr, nGy->mGy->mSv approx
RADON_DCC_MSV_PER_BQ_M3_YR = 0.36e-3 * 0.4 * 8760 / 1000  # simplified UNSCEAR-style factor
THORON_FRACTION_OF_RADON = 0.10  # typical thoron/radon dose ratio when no direct Tn data

UNSCEAR_WORLD_AVG_MSV_YR = 2.2
RISK_GREEN_MAX = UNSCEAR_WORLD_AVG_MSV_YR * 1.0
RISK_AMBER_MAX = UNSCEAR_WORLD_AVG_MSV_YR * 3.0

# In-memory caches
DOSE_CACHE: TTLCache = TTLCache(maxsize=200_000, ttl=3600)      # computed /dose responses
RASTER_CACHE: dict = {}                                          # loaded raster arrays, never expire
SENTINEL_CACHE: TTLCache = TTLCache(maxsize=500, ttl=30 * 86400)  # Sentinel tiles, 30-day TTL
ERA5_CACHE: TTLCache = TTLCache(maxsize=50, ttl=7 * 86400)        # ERA5/soil moisture, 7-day TTL


# ======================================================================
# LITHOLOGY PRIOR TABLE (fallback when Tellus radiometrics unavailable)
# Typical K (%), eU (ppm), eTh (ppm) by simplified GSI lithology class
# ======================================================================

LITHOLOGY_PRIOR = {
    "Gr": {"name": "Granite",              "K": 4.0, "U": 5.0, "Th": 18.0, "permeability": "low"},
    "Pa": {"name": "Acid plutonic",         "K": 3.6, "U": 4.2, "Th": 15.0, "permeability": "low"},
    "Ss": {"name": "Sandstone",             "K": 1.8, "U": 1.8, "Th": 8.0,  "permeability": "high"},
    "Ls": {"name": "Limestone",             "K": 0.3, "U": 1.5, "Th": 1.5,  "permeability": "moderate"},
    "Sh": {"name": "Shale/Mudstone",        "K": 2.6, "U": 3.5, "Th": 10.0, "permeability": "low"},
    "Bs": {"name": "Basalt/Basic volcanic", "K": 0.8, "U": 0.5, "Th": 2.5,  "permeability": "moderate"},
    "Qz": {"name": "Quartzite",             "K": 0.5, "U": 1.0, "Th": 3.0,  "permeability": "moderate"},
    "Til": {"name": "Glacial till",         "K": 1.5, "U": 2.0, "Th": 7.0,  "permeability": "variable"},
    "Peat": {"name": "Peat/organic",        "K": 0.1, "U": 0.3, "Th": 0.5,  "permeability": "very low"},
    "Water": {"name": "Water body",         "K": 0.0, "U": 0.0, "Th": 0.0,  "permeability": "n/a"},
}
DEFAULT_LITHOLOGY = "Sh"


# ======================================================================
# DATA LOADERS (lazy, cached in RAM after first load)
# ======================================================================

def _try_import_rasterio():
    try:
        import rasterio
        return rasterio
    except ImportError:
        return None


class RasterLayer:
    """Wraps a GeoTIFF, loaded fully into RAM on first access."""

    def __init__(self, path: Path):
        self.path = path
        self._array = None
        self._transform = None
        self._bounds = None
        self._loaded = False
        self._available = path.exists()

    def _load(self):
        if self._loaded:
            return
        rasterio = _try_import_rasterio()
        if rasterio is None or not self._available:
            self._loaded = True
            return
        with rasterio.open(self.path) as src:
            self._array = src.read(1)
            self._transform = src.transform
            self._bounds = src.bounds
        self._loaded = True

    @property
    def available(self) -> bool:
        return self._available

    def sample(self, lat: float, lon: float) -> Optional[float]:
        """Point sample at lat/lon. Returns None if layer unavailable or out of bounds."""
        self._load()
        if self._array is None:
            return None
        try:
            row, col = ~self._transform * (lon, lat)
            row, col = int(row), int(col)
            if 0 <= row < self._array.shape[0] and 0 <= col < self._array.shape[1]:
                val = self._array[row, col]
                if np.isnan(val):
                    return None
                return float(val)
        except Exception:
            return None
        return None

    def window(self, lat_min, lat_max, lon_min, lon_max) -> Optional[np.ndarray]:
        self._load()
        if self._array is None:
            return None
        try:
            row_max, col_min = ~self._transform * (lon_min, lat_min)
            row_min, col_max = ~self._transform * (lon_max, lat_max)
            row_min, row_max = int(max(0, row_min)), int(min(self._array.shape[0], row_max))
            col_min, col_max = int(max(0, col_min)), int(min(self._array.shape[1], col_max))
            return self._array[row_min:row_max, col_min:col_max]
        except Exception:
            return None


@lru_cache(maxsize=1)
def get_layers() -> dict:
    """Load and cache all raster layer handles (lazy load on first sample)."""
    layers = {
        "bedrock": RasterLayer(DATA_DIR / "gsi_bedrock_100k.tif"),
        "tellus_k": RasterLayer(DATA_DIR / "tellus_radiometric_k.tif"),
        "tellus_u": RasterLayer(DATA_DIR / "tellus_radiometric_u.tif"),
        "tellus_th": RasterLayer(DATA_DIR / "tellus_radiometric_th.tif"),
        "epa_radon": RasterLayer(DATA_DIR / "epa_radon_map.tif"),
        "permeability": RasterLayer(DATA_DIR / "teagasc_soil_permeability.tif"),
        "landcover": RasterLayer(DATA_DIR / "corine_landcover.tif"),
        "ndvi": RasterLayer(DATA_DIR / "sentinel2_ndvi.tif"),
        "soil_moisture": RasterLayer(DATA_DIR / "esa_cci_soil_moisture.tif"),
    }
    return layers


@lru_cache(maxsize=1)
def get_faults():
    """Load fault lines once. Returns None if file/geopandas unavailable."""
    path = DATA_DIR / "gsi_faults.geojson"
    if not path.exists():
        return None
    try:
        import geopandas as gpd
        return gpd.read_file(path)
    except ImportError:
        return None


@lru_cache(maxsize=1)
def get_season() -> str:
    path = DATA_DIR / "era5_season.json"
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f).get("season", "unknown")
        except Exception:
            pass
    # Fallback: infer from current month (Northern Hemisphere)
    month = time.gmtime().tm_mon
    if month in (12, 1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    return "autumn"


def lithology_class_from_code(code: Optional[float]) -> str:
    """Map raw bedrock raster code to a lithology key. Adjust to your raster's legend."""
    if code is None:
        return DEFAULT_LITHOLOGY
    mapping = {1: "Gr", 2: "Pa", 3: "Ss", 4: "Ls", 5: "Sh", 6: "Bs", 7: "Qz", 8: "Til", 9: "Peat", 0: "Water"}
    return mapping.get(int(code), DEFAULT_LITHOLOGY)


def nearest_fault_distance_m(lat: float, lon: float) -> Optional[float]:
    faults = get_faults()
    if faults is None or faults.empty:
        return None
    try:
        from shapely.geometry import Point
        pt = Point(lon, lat)
        dists = faults.geometry.distance(pt)
        min_deg = float(dists.min())
        return min_deg * 111_000  # rough deg->m at Irish latitude
    except Exception:
        return None


# ======================================================================
# CORE DOSE CALCULATION
# ======================================================================

@dataclass
class Factor:
    id: str
    value: str
    effect: str
    direction: str  # "up" | "down" | "neutral" | "varies"
    source: str
    resolution: str

    def to_dict(self):
        return {
            "id": self.id, "value": self.value, "effect": self.effect,
            "direction": self.direction, "source": self.source, "resolution": self.resolution,
        }


@dataclass
class DoseResult:
    lat: float
    lon: float
    cell_m: int
    arms_mSv_yr: dict
    total_terrestrial_mSv_yr: float
    risk: dict
    factors: list = field(default_factory=list)
    report_short: list = field(default_factory=list)
    confidence: dict = field(default_factory=dict)
    activities: dict = field(default_factory=dict)
    gamma_rate_nGy_h: float = 0.0
    radon_Bq_m3: float = 0.0
    ra_eq_Bq_kg: float = 0.0
    provenance: list = field(default_factory=list)
    season: str = "unknown"
    data_sources: dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "lat": self.lat, "lon": self.lon, "cell_m": self.cell_m,
            "arms_mSv_yr": self.arms_mSv_yr,
            "total_terrestrial_mSv_yr": round(self.total_terrestrial_mSv_yr, 3),
            "risk": self.risk,
            "factors": [f.to_dict() if isinstance(f, Factor) else f for f in self.factors],
            "report_short": self.report_short,
            "confidence": self.confidence,
            "activities": self.activities,
            "gamma_rate_nGy_h": round(self.gamma_rate_nGy_h, 1),
            "radon_Bq_m3": round(self.radon_Bq_m3, 0),
            "ra_eq_Bq_kg": round(self.ra_eq_Bq_kg, 0),
            "provenance": self.provenance,
            "season": self.season,
            "data_sources": self.data_sources,
        }


def compute_dose(lat: float, lon: float, cell_m: int = CELL_M_DEFAULT) -> DoseResult:
    """
    Main dose computation. Reads real raster data if available,
    falls back to lithology priors if not.
    """
    layers = get_layers()
    provenance = []
    factors = []
    data_sources = {}

    # ── Step 1: Sample bedrock lithology ──
    bedrock_code = layers["bedrock"].sample(lat, lon)
    lith_key = lithology_class_from_code(bedrock_code)
    lith_info = LITHOLOGY_PRIOR[lith_key]
    if bedrock_code is not None:
        provenance.append(f"bedrock: raster code {int(bedrock_code)} → {lith_key} ({lith_info['name']})")
        data_sources["bedrock"] = "GSI Bedrock 1:100k raster"
    else:
        provenance.append(f"bedrock: fallback → {lith_key} ({lith_info['name']})")
        data_sources["bedrock"] = "lithology prior (no raster)"

    # ── Step 2: Sample Tellus radiometrics (K, eU, eTh) ──
    k_pct = layers["tellus_k"].sample(lat, lon)
    eU_ppm = layers["tellus_u"].sample(lat, lon)
    eTh_ppm = layers["tellus_th"].sample(lat, lon)

    if k_pct is not None:
        provenance.append(f"K: Tellus measured {k_pct:.2f}%")
        data_sources["K"] = "Tellus airborne radiometric"
    else:
        k_pct = lith_info["K"]
        provenance.append(f"K: lithology prior {k_pct:.1f}%")
        data_sources["K"] = "lithology prior"

    if eU_ppm is not None:
        provenance.append(f"eU: Tellus measured {eU_ppm:.1f} ppm")
        data_sources["eU"] = "Tellus airborne radiometric"
    else:
        eU_ppm = lith_info["U"]
        provenance.append(f"eU: lithology prior {eU_ppm:.1f} ppm")
        data_sources["eU"] = "lithology prior"

    if eTh_ppm is not None:
        provenance.append(f"eTh: Tellus measured {eTh_ppm:.1f} ppm")
        data_sources["eTh"] = "Tellus airborne radiometric"
    else:
        eTh_ppm = lith_info["Th"]
        provenance.append(f"eTh: lithology prior {eTh_ppm:.1f} ppm")
        data_sources["eTh"] = "lithology prior"

    # ── Step 3: Activities (Bq/kg) from concentrations ──
    A_Ra = eU_ppm * 12.22    # eU ppm → Ra-226 Bq/kg
    A_Th = eTh_ppm * 4.06    # eTh ppm → Th-232 Bq/kg
    A_K = k_pct * 313        # K % → K-40 Bq/kg

    # ── Step 4: Gamma dose ──
    gamma_nGy_h = (DCC_GAMMA_NGY_H_PER_BQ_KG["Ra226"] * A_Ra +
                   DCC_GAMMA_NGY_H_PER_BQ_KG["Th232"] * A_Th +
                   DCC_GAMMA_NGY_H_PER_BQ_KG["K40"] * A_K)
    gamma_mSv_yr = gamma_nGy_h * GAMMA_NGY_H_TO_MSV_YR

    factors.append(Factor("gamma", f"{gamma_nGy_h:.0f} nGy/h → {gamma_mSv_yr:.2f} mSv/yr",
                          "external gamma exposure", "neutral",
                          "Tellus" if "Tellus" in data_sources.get("K", "") else "lithology prior",
                          f"{cell_m}m"))

    # ── Step 5: Radon dose ──
    radon_measured = layers["epa_radon"].sample(lat, lon)
    if radon_measured is not None:
        C_Rn = radon_measured
        provenance.append(f"radon: EPA measured {C_Rn:.0f} Bq/m³")
        data_sources["radon"] = "EPA Radon Risk Map raster"
    else:
        # Estimate from activities, permeability, faults
        perm_layer = layers["permeability"]
        perm_val = perm_layer.sample(lat, lon)
        if perm_val is not None:
            perm_class = {1: "very low", 2: "low", 3: "moderate", 4: "high", 5: "variable"}.get(int(perm_val), "moderate")
        else:
            perm_class = lith_info["permeability"]
        data_sources["radon"] = "GRP model estimate"

        fault_dist = nearest_fault_distance_m(lat, lon)
        fault_factor = 1.0
        if fault_dist is not None and fault_dist < 2000:
            fault_factor = 1.0 + 0.3 * (1 - fault_dist / 2000)
            provenance.append(f"fault proximity: {fault_dist:.0f}m → factor {fault_factor:.2f}")

        perm_factor = {"very low": 0.3, "low": 0.7, "moderate": 1.0, "high": 1.5, "variable": 1.0, "n/a": 0}.get(perm_class, 1.0)
        grp = (A_Ra / 50) * perm_factor * fault_factor
        C_Rn = grp * 50
        provenance.append(f"radon: GRP estimate {C_Rn:.0f} Bq/m³ (perm={perm_class})")

    radon_mSv_yr = C_Rn * RADON_DCC_MSV_PER_BQ_M3_YR

    factors.append(Factor("radon", f"{C_Rn:.0f} Bq/m³ → {radon_mSv_yr:.2f} mSv/yr",
                          "indoor radon inhalation",
                          "up" if C_Rn >= 200 else "neutral",
                          data_sources.get("radon", "model"),
                          "1km" if radon_measured else "model"))

    # ── Step 6: Thoron dose ──
    thoron_mSv_yr = radon_mSv_yr * THORON_FRACTION_OF_RADON
    factors.append(Factor("thoron", f"{thoron_mSv_yr:.2f} mSv/yr (10% of radon)",
                          "thoron-220 inhalation", "neutral", "derived", "model"))

    # ── Step 7: Seasonal adjustment ──
    season = get_season()
    season_factor = {"winter": 1.15, "spring": 1.0, "summer": 0.9, "autumn": 1.05}.get(season, 1.0)
    if season_factor != 1.0:
        radon_mSv_yr *= season_factor
        thoron_mSv_yr *= season_factor
        factors.append(Factor("season", f"{season} → factor {season_factor}",
                              "occupancy/ventilation adjustment", "varies", "ERA5", "seasonal"))

    # ── Step 8: Total dose ──
    total = gamma_mSv_yr + radon_mSv_yr + thoron_mSv_yr

    # ── Step 9: Risk classification ──
    risk_tier = "GREEN"
    risk_flags = []
    if total > RISK_AMBER_MAX:
        risk_tier = "RED"
        risk_flags.append(f"total {total:.2f} > {RISK_AMBER_MAX:.1f} mSv/yr")
    elif total > RISK_GREEN_MAX:
        risk_tier = "AMBER"
        risk_flags.append(f"total {total:.2f} > {RISK_GREEN_MAX:.1f} mSv/yr")

    if C_Rn >= 200:
        risk_tier = "RED"
        risk_flags.append(f"radon {C_Rn:.0f} ≥ Irish 200 Bq/m³ action level")
    elif C_Rn >= 100:
        if risk_tier == "GREEN":
            risk_tier = "AMBER"
        risk_flags.append(f"radon {C_Rn:.0f} ≥ WHO 100 Bq/m³ guideline")

    ra_eq = A_Ra + 1.43 * A_Th + 0.077 * A_K
    if ra_eq >= 370:
        if risk_tier != "RED":
            risk_tier = "RED"
        risk_flags.append(f"Ra-eq {ra_eq:.0f} ≥ 370 Bq/kg")

    if gamma_nGy_h >= 1000:
        risk_tier = "RED"
        risk_flags.append(f"gamma {gamma_nGy_h:.0f} ≥ 1000 nGy/h")

    # ── Step 10: Confidence ──
    measured_count = sum(1 for v in [k_pct, eU_ppm, eTh_ppm, radon_measured] if v is not None)
    conf_score = min(95, 20 + measured_count * 20)
    conf_level = "high" if conf_score >= 75 else "medium-high" if conf_score >= 50 else "medium" if conf_score >= 30 else "low"
    conf_reason = f"{measured_count}/4 layers measured"

    # ── Step 11: Short report (8 lines) ──
    dominant = "radon" if radon_mSv_yr >= thoron_mSv_yr and radon_mSv_yr >= gamma_mSv_yr else \
               "thoron" if thoron_mSv_yr >= gamma_mSv_yr else "gamma"
    dom_arm = {"radon": radon_mSv_yr, "thoron": thoron_mSv_yr, "gamma": gamma_mSv_yr}[dominant]
    dom_pct = dom_arm / total * 100 if total > 0 else 0

    report = [
        f"1. {dominant.capitalize()} is {dom_pct:.0f}% of total dose ({dom_arm:.2f} mSv/yr).",
        f"2. Total terrestrial dose: {total:.2f} mSv/yr — {risk_tier}.",
        f"3. Lithology: {lith_key} ({lith_info['name']}). Ra={A_Ra:.0f}, Th={A_Th:.0f}, K={A_K:.0f} Bq/kg.",
        f"4. Indoor radon: {C_Rn:.0f} Bq/m³{' — ⚠ EXCEEDS Irish 200 Bq/m³ action level' if C_Rn >= 200 else ''}.",
        f"5. {(total / UNSCEAR_WORLD_AVG_MSV_YR):.1f}× UNSCEAR world average ({UNSCEAR_WORLD_AVG_MSV_YR} mSv/yr).",
        f"6. Ra-eq: {ra_eq:.0f} Bq/kg{' — ⚠ exceeds 370 threshold' if ra_eq >= 370 else ''}.",
        f"7. Gamma: {gamma_nGy_h:.0f} nGy/h → {gamma_mSv_yr:.2f} mSv/yr.",
        f"8. Confidence: {conf_level} ({conf_score}%) — {conf_reason}.",
    ]

    return DoseResult(
        lat=lat, lon=lon, cell_m=cell_m,
        arms_mSv_yr={"radon": round(radon_mSv_yr, 3), "thoron": round(thoron_mSv_yr, 3), "gamma": round(gamma_mSv_yr, 3)},
        total_terrestrial_mSv_yr=total,
        risk={"tier": risk_tier, "flags": risk_flags},
        factors=factors,
        report_short=report,
        confidence={"score": conf_score, "level": conf_level, "reason": conf_reason},
        activities={"Ra226_Bq_kg": round(A_Ra, 1), "Th232_Bq_kg": round(A_Th, 1), "K40_Bq_kg": round(A_K, 1)},
        gamma_rate_nGy_h=gamma_nGy_h,
        radon_Bq_m3=C_Rn,
        ra_eq_Bq_kg=ra_eq,
        provenance=provenance,
        season=season,
        data_sources=data_sources,
    )


# ======================================================================
# FASTAPI APP
# ======================================================================

app = FastAPI(title="Irish Terrestrial Dose Indicator", version="3.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health():
    layers = get_layers()
    available = {k: v.available for k, v in layers.items()}
    return {
        "status": "ok",
        "data_dir": str(DATA_DIR),
        "layers": available,
        "season": get_season(),
        "faults_loaded": get_faults() is not None,
    }


@app.get("/dose")
def dose_endpoint(
    lat: float = Query(..., ge=-90, le=90, description="Latitude WGS84"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude WGS84"),
):
    # Ireland bounds check
    if not (51.4 <= lat <= 55.4 and -10.6 <= lon <= -5.3):
        raise HTTPException(400, "Coordinates outside Ireland (51.4-55.4°N, 10.6-5.3°W)")

    cache_key = (round(lat, 4), round(lon, 4))
    if cache_key in DOSE_CACHE:
        return DOSE_CACHE[cache_key]

    result = compute_dose(lat, lon)
    response = result.to_dict()
    DOSE_CACHE[cache_key] = response
    return response


@app.get("/dose/bbox")
def dose_bbox(
    lat_min: float = Query(..., ge=51.4, le=55.4),
    lat_max: float = Query(..., ge=51.4, le=55.4),
    lon_min: float = Query(..., ge=-10.6, le=-5.3),
    lon_max: float = Query(..., ge=-10.6, le=-5.3),
    step_km: float = Query(2.0, ge=0.5, le=20, description="Grid spacing in km"),
):
    if lat_min >= lat_max or lon_min >= lon_max:
        raise HTTPException(400, "Invalid bounding box")

    step_deg = step_km / 111.0  # rough conversion
    lats = np.arange(lat_min, lat_max, step_deg)
    lons = np.arange(lon_min, lon_max, step_deg)

    results = []
    for lat in lats:
        for lon in lons:
            try:
                r = compute_dose(float(lat), float(lon))
                results.append(r.to_dict())
            except Exception:
                continue

    return {"count": len(results), "step_km": step_km, "results": results}
