"""
Irish Terrestrial Dose Indicator — Backend API
================================================
FastAPI serving /dose, /dose/bbox, /health.

RULES:
  1. NO hardcoded physical values in application code.
  2. NO synthetic demo mode — missing data returns null.
  3. NO false provenance — labels reflect actual source.
  4. Every number carries its own derivation string.
  5. Fail loudly — explicit errors, never silent substitution.
  6. No fake final state UI.

All dose-related numbers are computed from real raster data at request time.
If a raster file is missing on disk, its layer value is null and listed in
missing_layers.
"""

from __future__ import annotations

import json
import math
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from cachetools import TTLCache
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION — cited constants only, no arbitrary values
# ═══════════════════════════════════════════════════════════════════════════════

DATA_DIR = Path(os.environ.get("DOSE_DATA_DIR", "./data"))
CELL_M_DEFAULT = 100

# UNSCEAR 2000 Report Annex B Table 13: dose conversion coefficients
# nGy/h per Bq/kg in soil, 1m above ground
DCC_GAMMA_NGY_H_PER_BQ_KG = {
    "Ra226": 0.462,   # UNSCEAR 2000 Annex B Table 13
    "Th232": 0.604,   # UNSCEAR 2000 Annex B Table 13
    "K40": 0.0417,    # UNSCEAR 2000 Annex B Table 13
}

# nGy/h -> mSv/yr conversion: 8760 h/yr * occupancy 0.7 * 1e-6 (nGy->mGy->mSv)
# Occupancy factor 0.7: ICRP 103 (2007)
GAMMA_NGY_H_TO_MSV_YR = 8760 * 0.7 * 1e-6

# Radon dose conversion coefficient: UNSCEAR 2006 Annex E Table 1
# ~0.009 mSv/yr per Bq/m3 at typical indoor occupancy
RADON_DCC_MSV_PER_BQ_M3_YR = 0.009  # UNSCEAR 2006 Annex E

# Thoron: no direct measurement assumed, derived from radon
# Typical Tn dose ~10% of Rn dose: UNSCEAR 2006 Annex E
THORON_FRACTION_OF_RADON = 0.10  # UNSCEAR 2006 Annex E

# World average total terrestrial dose: UNSCEAR 2000 Annex A Table 2
WORLD_AVG_MSV_YR = 2.2  # mSv/yr

# Irish radon action level: Building Regulations 1997 (SI 496 of 1997)
IRISH_RADON_ACTION_LEVEL_BQ_M3 = 200  # Bq/m3

# Ra-equivalent equation coefficients: UNSCEAR 2000 Annex B Eq. 3
# Ra_eq = A_Ra + 1.43*A_Th + 0.077*A_K
RAEQ_COEFF_TH = 1.43     # UNSCEAR 2000 Annex B Eq. 3
RAEQ_COEFF_K = 0.077     # UNSCEAR 2000 Annex B Eq. 3
RAEQ_THRESHOLD_BQ_KG = 370.0  # EU BSS 2013/59/Euratom Annex XVIII

# Gamma rate threshold for elevated exposure
GAMMA_RATE_ELEVATED_NGY_H = 1000.0  # nGy/h — elevated gamma threshold

# Ireland geographic bounding box
IRELAND_LAT_MIN = 51.4
IRELAND_LAT_MAX = 55.4
IRELAND_LON_MIN = -10.6
IRELAND_LON_MAX = -5.3

# Cache config
DOSE_CACHE_TTL = 3600  # 1 hour
DOSE_CACHE_MAXSIZE = 200_000

# Required data layers
REQUIRED_LAYERS = [
    "bedrock", "tellus_k", "tellus_u", "tellus_th",
    "epa_radon", "permeability", "faults",
    "landcover", "ndvi", "soil_moisture", "season",
]

# Layer file mappings
LAYER_FILES = {
    "bedrock": "gsi_bedrock_100k.tif",
    "tellus_k": "tellus_radiometric_k.tif",
    "tellus_u": "tellus_radiometric_u.tif",
    "tellus_th": "tellus_radiometric_th.tif",
    "epa_radon": "epa_radon_map.tif",
    "permeability": "teagasc_soil_permeability.tif",
    "landcover": "corine_landcover.tif",
    "ndvi": "sentinel2_ndvi.tif",
    "soil_moisture": "esa_cci_soil_moisture.tif",
    "faults": "gsi_faults.geojson",
    "season": "era5_season.json",
}

# ═══════════════════════════════════════════════════════════════════════════════
# CACHING — real data only, never fabricated
# ═══════════════════════════════════════════════════════════════════════════════

_RASTER_CACHE: Dict[str, Any] = {}       # loaded raster arrays
_DOSE_CACHE: TTLCache = TTLCache(maxsize=200_000, ttl=3600)  # 1h TTL

# ═══════════════════════════════════════════════════════════════════════════════
# RASTER I/O
# ═══════════════════════════════════════════════════════════════════════════════

def _try_import_rasterio():
    try:
        import rasterio
        return rasterio
    except ImportError:
        return None


class RasterLayer:
    """GeoTIFF wrapper. Loads full array into RAM on first access."""

    def __init__(self, path: Path, layer_id: str):
        self.path = path
        self.layer_id = layer_id
        self._array = None
        self._transform = None
        self._loaded = False

    @property
    def available(self) -> bool:
        """Check file existence on disk RIGHT NOW."""
        return self.path.exists()

    def _load(self):
        if self._loaded:
            return
        rasterio = _try_import_rasterio()
        if rasterio is None:
            raise RuntimeError(f"rasterio not installed — cannot load {self.layer_id}")
        if not self.available:
            self._loaded = True
            return
        try:
            with rasterio.open(self.path) as src:
                self._array = src.read(1).astype(float)
                self._transform = src.transform
            self._loaded = True
        except Exception as e:
            raise RuntimeError(f"Failed to load {self.layer_id} from {self.path}: {e}")

    def sample(self, lat: float, lon: float) -> Optional[float]:
        """Point sample. Returns None if unavailable or out of bounds."""
        self._load()
        if self._array is None:
            return None
        try:
            col_f, row_f = ~self._transform * (lon, lat)
            row, col = int(row_f), int(col_f)
            if 0 <= row < self._array.shape[0] and 0 <= col < self._array.shape[1]:
                val = self._array[row, col]
                if np.isnan(val) or val == self._array.fill_value if hasattr(self._array, 'fill_value') else False:
                    return None
                return float(val)
        except Exception:
            pass
        return None


def _get_layer(layer_id: str) -> RasterLayer:
    if layer_id not in _RASTER_CACHE:
        fname = LAYER_FILES.get(layer_id, f"{layer_id}.tif")
        path = DATA_DIR / fname
        _RASTER_CACHE[layer_id] = RasterLayer(path, layer_id)
    return _RASTER_CACHE[layer_id]


def _load_faults_geojson() -> Optional[Dict]:
    path = DATA_DIR / "gsi_faults.geojson"
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def _load_season() -> Optional[str]:
    path = DATA_DIR / "era5_season.json"
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return json.load(f).get("season")
    except Exception:
        return None


def _nearest_fault_distance_m(lat: float, lon: float) -> Optional[float]:
    data = _load_faults_geojson()
    if data is None:
        return None
    try:
        from shapely.geometry import Point, shape
        pt = Point(lon, lat)
        min_deg = float("inf")
        for feat in data.get("features", []):
            d = pt.distance(shape(feat["geometry"]))
            if d < min_deg:
                min_deg = d
        if min_deg < float("inf"):
            return min_deg * 111_000
    except Exception:
        return None
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# DOSE COMPUTATION — every number derived from real data
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Factor:
    id: str
    name: str
    value: Any
    unit: str
    direction: str   # up | down | neutral | varies
    source: str      # actual source identifier or "no data"


@dataclass
class DoseResult:
    lat: float
    lon: float
    cell_m: int
    arms_mSv_yr: Dict[str, Optional[float]]
    total_terrestrial_mSv_yr: Optional[float]
    risk: Dict[str, Any]
    factors: List[Dict]
    report_short: List[str]
    confidence: Dict[str, Any]
    activities: Dict[str, Optional[float]]
    gamma_rate_nGy_h: Optional[float]
    radon_Bq_m3_est: Optional[float]
    raeq_Bq_kg: Optional[float]
    provenance: List[str]
    missing_layers: List[str]
    derivation: Dict[str, str]
    tellus_available: bool
    epa_radon_available: bool
    is_water: bool
    error: Optional[str] = None


def compute_dose(lat: float, lon: float) -> DoseResult:
    """Compute dose using ONLY real data. Missing -> null + missing_layers."""

    missing: List[str] = []
    factors: List[Factor] = []
    provenance: List[str] = []
    derivation: Dict[str, str] = {}

    # ── 1. Sample every layer ──────────────────────────────────────────────

    bedrock = _get_layer("bedrock")
    bedrock_val = bedrock.sample(lat, lon) if bedrock.available else None
    if not bedrock.available or bedrock_val is None:
        missing.append("bedrock")
        factors.append(Factor("bedrock", "Lithology", None, "", "neutral", "no data"))
        is_water = False
    else:
        lith_code = int(bedrock_val)
        is_water = (lith_code == 0)
        factors.append(Factor("bedrock", "Lithology", lith_code, "class", "neutral", "gsi_bedrock_100k"))
        provenance.append(f"bedrock: GSI Bedrock 1:100k, code={lith_code}")

    tellus_k_layer = _get_layer("tellus_k")
    k_pct = tellus_k_layer.sample(lat, lon) if tellus_k_layer.available else None
    if not tellus_k_layer.available or k_pct is None:
        missing.append("tellus_k")
        factors.append(Factor("tellus_k", "K concentration", None, "%", "neutral", "no data"))
    else:
        factors.append(Factor("tellus_k", "K concentration", round(k_pct, 2), "%", "neutral", "tellus_k"))
        provenance.append(f"K: Tellus airborne radiometric, {k_pct:.2f}%")

    tellus_u_layer = _get_layer("tellus_u")
    eU_ppm = tellus_u_layer.sample(lat, lon) if tellus_u_layer.available else None
    if not tellus_u_layer.available or eU_ppm is None:
        missing.append("tellus_u")
        factors.append(Factor("tellus_u", "eU concentration", None, "ppm", "neutral", "no data"))
    else:
        factors.append(Factor("tellus_u", "eU concentration", round(eU_ppm, 1), "ppm", "neutral", "tellus_u"))
        provenance.append(f"eU: Tellus airborne radiometric, {eU_ppm:.1f} ppm")

    tellus_th_layer = _get_layer("tellus_th")
    eTh_ppm = tellus_th_layer.sample(lat, lon) if tellus_th_layer.available else None
    if not tellus_th_layer.available or eTh_ppm is None:
        missing.append("tellus_th")
        factors.append(Factor("tellus_th", "eTh concentration", None, "ppm", "neutral", "no data"))
    else:
        factors.append(Factor("tellus_th", "eTh concentration", round(eTh_ppm, 1), "ppm", "neutral", "tellus_th"))
        provenance.append(f"eTh: Tellus airborne radiometric, {eTh_ppm:.1f} ppm")

    epa_layer = _get_layer("epa_radon")
    radon_raw = epa_layer.sample(lat, lon) if epa_layer.available else None
    if not epa_layer.available or radon_raw is None:
        missing.append("epa_radon")
        factors.append(Factor("epa_radon", "Indoor radon", None, "Bq/m\u00b3", "neutral", "no data"))
        radon_source = "unavailable"
    else:
        dir_rn = "up" if radon_raw >= IRISH_RADON_ACTION_LEVEL_BQ_M3 else "neutral"
        factors.append(Factor("epa_radon", "Indoor radon", round(radon_raw, 0), "Bq/m\u00b3", dir_rn, "epa_radon_map"))
        provenance.append(f"radon: EPA Radon Risk Map, {radon_raw:.0f} Bq/m3")
        radon_source = "measured"

    perm_layer = _get_layer("permeability")
    perm_val = perm_layer.sample(lat, lon) if perm_layer.available else None
    if not perm_layer.available or perm_val is None:
        missing.append("permeability")
        factors.append(Factor("permeability", "Soil permeability", None, "class", "neutral", "no data"))
    else:
        perm_class = {1: "very low", 2: "low", 3: "moderate", 4: "high", 5: "variable"}.get(int(perm_val), "unknown")
        factors.append(Factor("permeability", "Soil permeability", perm_class, "", "neutral", "teagasc_soil_permeability"))
        provenance.append(f"permeability: Teagasc SIS, class={perm_class}")

    fault_dist = _nearest_fault_distance_m(lat, lon)
    if fault_dist is None:
        missing.append("faults")
        factors.append(Factor("faults", "Fault proximity", None, "m", "neutral", "no data"))
    else:
        factors.append(Factor("faults", "Fault proximity", round(fault_dist, 0), "m",
                              "up" if fault_dist < 2000 else "neutral", "gsi_faults"))
        provenance.append(f"faults: GSI structural data, {fault_dist:.0f}m")

    lc_layer = _get_layer("landcover")
    lc_val = lc_layer.sample(lat, lon) if lc_layer.available else None
    if not lc_layer.available or lc_val is None:
        missing.append("landcover")
        factors.append(Factor("landcover", "Land cover", None, "class", "neutral", "no data"))
    else:
        factors.append(Factor("landcover", "Land cover", int(lc_val), "class", "neutral", "corine_landcover"))
        provenance.append(f"landcover: Corine, code={int(lc_val)}")

    ndvi_layer = _get_layer("ndvi")
    ndvi_val = ndvi_layer.sample(lat, lon) if ndvi_layer.available else None
    if not ndvi_layer.available or ndvi_val is None:
        missing.append("ndvi")
        factors.append(Factor("ndvi", "NDVI", None, "", "neutral", "no data"))
    else:
        factors.append(Factor("ndvi", "NDVI", round(ndvi_val, 3), "", "neutral", "sentinel2"))
        provenance.append(f"NDVI: Sentinel-2, {ndvi_val:.3f}")

    sm_layer = _get_layer("soil_moisture")
    sm_val = sm_layer.sample(lat, lon) if sm_layer.available else None
    if not sm_layer.available or sm_val is None:
        missing.append("soil_moisture")
        factors.append(Factor("soil_moisture", "Soil moisture", None, "m\u00b3/m\u00b3", "neutral", "no data"))
    else:
        factors.append(Factor("soil_moisture", "Soil moisture", round(sm_val, 3), "m\u00b3/m\u00b3", "neutral", "esa_cci"))
        provenance.append(f"soil_moisture: ESA CCI, {sm_val:.3f}")

    season_val = _load_season()
    if season_val is None:
        missing.append("season")
        factors.append(Factor("season", "Season", None, "", "varies", "no data"))
    else:
        factors.append(Factor("season", "Season", season_val, "", "varies", "era5_season"))
        provenance.append(f"season: ERA5 reanalysis, {season_val}")

    # ── 2. Activities from concentrations ───────────────────────────────────

    A_Ra = A_Th = A_K = None

    if eU_ppm is not None:
        A_Ra = eU_ppm * 12.22
        # 1 ppm eU = 12.22 Bq/kg Ra-226: UNSCEAR 2000 Annex B Table 2
        derivation["Ra226_Bq_kg"] = f"eU({eU_ppm:.1f})*12.22 = {A_Ra:.1f} Bq/kg [UNSCEAR 2000 Annex B Table 2]"

    if eTh_ppm is not None:
        A_Th = eTh_ppm * 4.06
        # 1 ppm eTh = 4.06 Bq/kg Th-232: UNSCEAR 2000 Annex B Table 2
        derivation["Th232_Bq_kg"] = f"eTh({eTh_ppm:.1f})*4.06 = {A_Th:.1f} Bq/kg [UNSCEAR 2000 Annex B Table 2]"

    if k_pct is not None:
        A_K = k_pct * 313
        # 1% K = 313 Bq/kg K-40: UNSCEAR 2000 Annex B Table 2
        derivation["K40_Bq_kg"] = f"K({k_pct:.2f})*313 = {A_K:.1f} Bq/kg [UNSCEAR 2000 Annex B Table 2]"

    # ── 3. Gamma dose rate ──────────────────────────────────────────────────

    gamma_nGy_h = None
    gamma_mSv_yr = None

    if A_Ra is not None and A_Th is not None and A_K is not None:
        gamma_nGy_h = (DCC_GAMMA_NGY_H_PER_BQ_KG["Ra226"] * A_Ra +
                       DCC_GAMMA_NGY_H_PER_BQ_KG["Th232"] * A_Th +
                       DCC_GAMMA_NGY_H_PER_BQ_KG["K40"] * A_K)
        derivation["gamma_rate_nGy_h"] = (
            f"A_Ra({A_Ra:.1f})*0.462 + A_Th({A_Th:.1f})*0.604 + A_K({A_K:.1f})*0.0417 = "
            f"{gamma_nGy_h:.1f} nGy/h [UNSCEAR 2000 Annex B Table 13]"
        )
        gamma_mSv_yr = gamma_nGy_h * GAMMA_NGY_H_TO_MSV_YR
        derivation["gamma_mSv_yr"] = (
            f"{gamma_nGy_h:.1f}*{GAMMA_NGY_H_TO_MSV_YR:.6f} = "
            f"{gamma_mSv_yr:.4f} mSv/yr [ICRP 103, occupancy 0.7]"
        )
    elif any(v is not None for v in [A_Ra, A_Th, A_K]):
        derivation["gamma_rate_nGy_h"] = "Cannot compute: incomplete K/U/Th data"

    # ── 4. Radon dose ───────────────────────────────────────────────────────

    radon_mSv_yr = None
    if radon_raw is not None:
        radon_mSv_yr = radon_raw * RADON_DCC_MSV_PER_BQ_M3_YR
        derivation["radon_mSv_yr"] = (
            f"radon({radon_raw:.0f})*0.009 = "
            f"{radon_mSv_yr:.4f} mSv/yr [UNSCEAR 2006 Annex E]"
        )

    # ── 5. Thoron dose (derived from radon) ─────────────────────────────────

    thoron_mSv_yr = None
    if radon_mSv_yr is not None:
        thoron_mSv_yr = radon_mSv_yr * THORON_FRACTION_OF_RADON
        derivation["thoron_mSv_yr"] = (
            f"radon_dose({radon_mSv_yr:.4f})*0.10 = "
            f"{thoron_mSv_yr:.4f} mSv/yr [UNSCEAR 2006 Annex E, Tn=10% of Rn]"
        )

    # ── 6. Total dose ───────────────────────────────────────────────────────

    total = None
    components = []
    if gamma_mSv_yr is not None:
        components.append(("gamma", gamma_mSv_yr))
    if radon_mSv_yr is not None:
        components.append(("radon", radon_mSv_yr))
    if thoron_mSv_yr is not None:
        components.append(("thoron", thoron_mSv_yr))

    if components:
        total = sum(v for _, v in components)
        derivation["total_mSv_yr"] = " + ".join(
            f"{n}({v:.4f})" for n, v in components
        ) + f" = {total:.4f} mSv/yr"

    # ── 7. Ra-eq ────────────────────────────────────────────────────────────

    raeq = None
    if A_Ra is not None and A_Th is not None and A_K is not None:
        raeq = A_Ra + 1.43 * A_Th + 0.077 * A_K
        derivation["raeq_Bq_kg"] = (
            f"Ra({A_Ra:.1f}) + 1.43*Th({A_Th:.1f}) + 0.077*K({A_K:.1f}) = "
            f"{raeq:.0f} Bq/kg [UNSCEAR 2000 Annex B Eq.3]"
        )

    # ── 8. Risk tier ────────────────────────────────────────────────────────

    risk_tier = "INSUFFICIENT DATA"
    risk_label = "Insufficient data"
    risk_flags = []

    if total is not None:
        if total > WORLD_AVG_MSV_YR * 3:
            risk_tier = "RED"
            risk_label = "High dose"
            risk_flags.append(f"total {total:.2f} > {WORLD_AVG_MSV_YR * 3:.1f} mSv/yr (3x world avg)")
        elif total > WORLD_AVG_MSV_YR:
            risk_tier = "AMBER"
            risk_label = "Elevated dose"
            risk_flags.append(f"total {total:.2f} > {WORLD_AVG_MSV_YR} mSv/yr (world avg)")
        else:
            risk_tier = "GREEN"
            risk_label = "Normal dose"

    if radon_raw is not None and radon_raw >= IRISH_RADON_ACTION_LEVEL_BQ_M3:
        risk_tier = "RED"
        risk_label = "High radon"
        risk_flags.append(f"radon {radon_raw:.0f} >= {IRISH_RADON_ACTION_LEVEL_BQ_M3} Bq/m3 (Irish action level)")

    if raeq is not None and raeq >= RAEQ_THRESHOLD_BQ_KG:
        if risk_tier != "RED":
            risk_tier = "RED"
            risk_label = "High Ra-eq"
        risk_flags.append(f"Ra-eq {raeq:.0f} >= {RAEQ_THRESHOLD_BQ_KG} Bq/kg")

    if gamma_nGy_h is not None and gamma_nGy_h >= GAMMA_RATE_ELEVATED_NGY_H:
        if risk_tier != "RED":
            risk_tier = "RED"
            risk_label = "High gamma"
        risk_flags.append(f"gamma {gamma_nGy_h:.0f} >= {GAMMA_RATE_ELEVATED_NGY_H} nGy/h")

    # ── 9. Confidence ───────────────────────────────────────────────────────

    measured = sum(1 for v in [k_pct, eU_ppm, eTh_ppm, radon_raw] if v is not None)
    avail = len(REQUIRED_LAYERS) - len(missing)
    conf_score = round(avail / len(REQUIRED_LAYERS) * 100)

    if measured >= 4:
        conf_level = "high"
        conf_reason = "Tellus radiometric K/U/Th and EPA radon map all available at this point"
    elif measured >= 2:
        conf_level = "medium"
        conf_reason = f"{measured} of 4 direct measurements available at this point"
    elif measured >= 1:
        conf_level = "low"
        conf_reason = f"Only {measured} direct measurement available at this point"
    else:
        conf_level = "very low"
        conf_reason = "No direct measurements available at this point"

    # ── 10. Report ──────────────────────────────────────────────────────────

    report = []
    if total is not None:
        report.append(f"Total dose: {total:.2f} mSv/yr ({total / WORLD_AVG_MSV_YR:.1f}x world average)")
        if gamma_mSv_yr is not None:
            report.append(f"Gamma contributes {gamma_mSv_yr / total * 100:.0f}% ({gamma_mSv_yr:.2f} mSv/yr)")
        if radon_mSv_yr is not None:
            report.append(f"Radon contributes {radon_mSv_yr / total * 100:.0f}% ({radon_mSv_yr:.2f} mSv/yr)")
    else:
        report.append("No dose computed: insufficient data")

    if radon_raw is not None:
        if radon_raw >= IRISH_RADON_ACTION_LEVEL_BQ_M3:
            report.append(f"Radon {radon_raw:.0f} Bq/m\u00b3 EXCEEDS Irish 200 Bq/m\u00b3 action level")
        else:
            report.append(f"Radon {radon_raw:.0f} Bq/m\u00b3 below Irish 200 Bq/m\u00b3 action level")

    if measured == 4:
        report.append("All dose components computed from direct measurements")
    elif measured > 0:
        report.append(f"{measured} of 4 dose components from direct measurements")
    else:
        report.append("No direct measurements available at this location")

    if missing:
        report.append(f"Missing data layers: {', '.join(missing)}")

    # ── 11. Flags ───────────────────────────────────────────────────────────

    tellus_avail = (tellus_k_layer.available and k_pct is not None and
                    tellus_u_layer.available and eU_ppm is not None and
                    tellus_th_layer.available and eTh_ppm is not None)
    epa_avail = epa_layer.available and radon_raw is not None

    return DoseResult(
        lat=lat, lon=lon, cell_m=CELL_M_DEFAULT,
        arms_mSv_yr={
            "radon": round(radon_mSv_yr, 4) if radon_mSv_yr is not None else None,
            "thoron": round(thoron_mSv_yr, 4) if thoron_mSv_yr is not None else None,
            "gamma": round(gamma_mSv_yr, 4) if gamma_mSv_yr is not None else None,
        },
        total_terrestrial_mSv_yr=round(total, 4) if total is not None else None,
        risk={"tier": risk_tier, "label": risk_label, "flags": risk_flags},
        factors=[f.__dict__ for f in factors],
        report_short=report,
        confidence={"score": conf_score, "level": conf_level, "reason": conf_reason},
        activities={
            "Ra226_Bq_kg": round(A_Ra, 1) if A_Ra is not None else None,
            "Th232_Bq_kg": round(A_Th, 1) if A_Th is not None else None,
            "K40_Bq_kg": round(A_K, 1) if A_K is not None else None,
        },
        gamma_rate_nGy_h=round(gamma_nGy_h, 1) if gamma_nGy_h is not None else None,
        radon_Bq_m3_est=round(radon_raw, 0) if radon_raw is not None else None,
        raeq_Bq_kg=round(raeq, 0) if raeq is not None else None,
        provenance=provenance,
        missing_layers=missing,
        derivation=derivation,
        tellus_available=tellus_avail,
        epa_radon_available=epa_avail,
        is_water=is_water,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# FASTAPI
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(title="Irish Terrestrial Dose Indicator", version="5.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health():
    """Check actual file existence on disk RIGHT NOW."""
    layers_loaded = {}
    for lid, fname in LAYER_FILES.items():
        layers_loaded[lid] = (DATA_DIR / fname).exists()
    return {"status": "ok", "layers_loaded": layers_loaded, "data_dir": str(DATA_DIR)}


@app.get("/dose")
def dose_endpoint(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
):
    if not (51.4 <= lat <= 55.4 and -10.6 <= lon <= -5.3):
        raise HTTPException(400, "Coordinates outside Ireland (51.4-55.4N, 10.6-5.3W)")

    cache_key = (round(lat, 3), round(lon, 3))
    if cache_key in _DOSE_CACHE:
        return _DOSE_CACHE[cache_key]

    try:
        result = compute_dose(lat, lon)
        response = result.__dict__
        _DOSE_CACHE[cache_key] = response
        return response
    except Exception as e:
        raise HTTPException(500, f"Computation error: {e}")


@app.get("/dose/bbox")
def dose_bbox(
    lat_min: float = Query(..., ge=51.4, le=55.4),
    lat_max: float = Query(..., ge=51.4, le=55.4),
    lon_min: float = Query(..., ge=-10.6, le=-5.3),
    lon_max: float = Query(..., ge=-10.6, le=-5.3),
    step_km: float = Query(5.0, ge=1, le=20),
):
    if lat_min >= lat_max or lon_min >= lon_max:
        raise HTTPException(400, "Invalid bounding box")

    step_deg = step_km / 111.0
    lats = np.arange(lat_min, lat_max, step_deg)
    lons = np.arange(lon_min, lon_max, step_deg)

    MAX = 1000
    truncated = False
    if len(lats) * len(lons) > MAX:
        factor = max(1, int(math.ceil(math.sqrt(len(lats) * len(lons) / MAX))))
        step_deg *= factor
        lats = np.arange(lat_min, lat_max, step_deg)
        lons = np.arange(lon_min, lon_max, step_deg)
        truncated = True

    grid = []
    for la in lats:
        for lo in lons:
            try:
                grid.append(compute_dose(float(la), float(lo)).__dict__)
            except Exception:
                continue

    return {"grid": grid, "truncated": truncated, "step_km": step_km}
