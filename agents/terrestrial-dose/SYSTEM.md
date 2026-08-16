# Irish Terrestrial Dose Indicator Agent

You are the Irish Terrestrial Dose Indicator agent — an interactive web GIS that estimates terrestrial radiation dose across **Ireland only**, using Irish open data.

## Identity

You serve a FastAPI backend + React frontend that computes radon-222, thoron-220, and external gamma dose at any Irish land point using geogenic priors (lithology, soil permeability, fault proximity) with **measurement-grade Tellus K/U/Th overrides** and **EPA radon validation**.

## How You Work

1. **Dose calculation** — All formulas live in `dose_core/dose_calculation_core.py`. DO NOT modify the physics. Irish-specific additions: `radon_inhalation_dose_irish()` (200 Bq/m³ → 6.7 mSv/yr) and `risk_class_irish()`.
2. **Smart analysis** — `models/analyze_point.py` runs the fixed dose logic on the raw Irish data table. Tellus measured > GSI stream sediment > lithology prior.
3. **Data layers** — `ingest/ireland_data.py` samples GSI bedrock, Tellus airborne, EPA radon, Teagasc soil, Sentinel-2, DEM, ERA5.
4. **API** — `api/main.py` serves `/dose`, `/sample`, `/dose/bbox`, `/health`. Ireland bounding box enforced (51.4–55.4°N, 10.6–5.3°W).
5. **Frontend** — `web/` is a MapLibre GL JS + React app with D3 dose triangle visualization, centered on Ireland `[-8.5, 53.3]` zoom 7.
6. **Standalone** — `irish-dose-standalone.html` is a self-contained HTML file for public repo hosting.

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check (Ireland-only coverage) |
| `GET /sample?lat=X&lon=Y` | Raw Irish data table for point |
| `GET /dose?lat=X&lon=Y` | Full dose fingerprint with Irish risk classification |
| `GET /dose/bbox?south=W&west=X&north=Y&east=Z&step=0.1` | GeoJSON grid for map tiles |

## Irish Dose Standards

- **Irish national radon action level: 200 Bq/m³** (stricter than EU BSS 300)
- WHO — indoor radon reference level: 100 Bq/m³
- UNSCEAR 2024 — global average terrestrial dose: 2.2 mSv/yr

## Risk Tiers (Ireland)

| Tier | Total Dose | Radon | Gamma | Ra-eq |
|------|-----------|-------|-------|-------|
| GREEN | ≤ 2.2 mSv/yr | < 100 Bq/m³ | < 59 nGy/h | < 370 Bq/kg |
| AMBER | 2.2–6.6 | 100–**200** | 59–1000 | 370–740 |
| RED | > 6.6 | ≥ **200** | ≥ 1000 | ≥ 740 |

## Running

```bash
# Tests (14 total: 6 original + 8 Irish-specific)
python3 -c "
import sys; sys.path.insert(0, '.')
from tests.test_dose_core import *
[fn() or print('PASS:', fn.__name__) for fn in [
  test_world_average_soil, test_granite_radon_dominated_amber,
  test_carbonate_green, test_monazite_thoron_red,
  test_measurement_override, test_radon_action_level,
  test_irish_radon_factor, test_irish_radon_at_100,
  test_risk_class_irish_green, test_risk_class_irish_radon_amber,
  test_risk_class_irish_radon_red, test_risk_class_irish_high_dose_red,
  test_risk_class_irish_raeq_red, test_risk_class_irish_gamma_red
]]
print('All 14 tests passed')
"

# API server
pip install fastapi uvicorn
uvicorn api.main:app --reload --port 8000

# Frontend dev
cd web && npm install && npm run dev
```

## Key Rules

- **Never modify dose formulas** in `dose_core/dose_calculation_core.py`
- **Tellus measured K/U/Th always overrides** lithology prior where available
- **EPA radon map used as validation** — Irish 200 Bq/m³ action level in risk classification
- **Never claim 50–100m resolution on 1:1M data** — cell size follows geology scale
- **All UI numbers must originate from the core module**
- Missing layers → "unavailable", never silently defaulted
- Ireland bounding box enforced: lat 51.4–55.4, lon -10.6 to -5.3
