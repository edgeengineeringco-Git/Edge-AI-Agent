# Irish Terrestrial Dose Agent

Interactive web GIS that estimates terrestrial radiation dose (radon-222, thoron-220, external gamma) at any Irish land point.

## Scope

`agents/terrestrial-dose` — **Ireland only**

## Architecture

```
terrestrial-dose/
├── dose_core/
│   └── dose_calculation_core.py   # Core dose formulas (DO NOT MODIFY)
├── api/
│   └── main.py                    # FastAPI backend — Ireland only
├── models/
│   └── analyze_point.py           # Smart analysis on raw Irish data table
├── ingest/
│   ├── ireland_data.py            # Irish open data layer fetchers
│   └── point_sampler.py           # Point sampling (legacy)
├── web/                           # React + MapLibre frontend (source only)
├── tests/
│   └── test_dose_core.py          # 14 validation tests
├── irish-dose-standalone.html     # Self-contained HTML for public repo
└── README.md
```

## Source

https://github.com/edgeengineeringco-Git/edge-ai-agent-site/tree/main/terrestrial-dose

## Running

```bash
# Tests
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

## API Endpoints

- `GET /health` — health check (Ireland-only coverage)
- `GET /sample?lat=53.35&lon=-6.26` — raw Irish data table
- `GET /dose?lat=53.35&lon=-6.26` — full dose fingerprint with Irish risk classification
- `GET /dose/bbox?south=51.4&west=-10.6&north=55.4&east=-5.3&step=0.1` — GeoJSON grid

## Dose Standards (Ireland)

| Metric | GREEN | AMBER | RED |
|--------|-------|-------|-----|
| Total dose (mSv/yr) | ≤ 2.2 | 2.2–6.6 | > 6.6 |
| Radon (Bq/m³) | ≤ 100 | 100–**200** | ≥ **200** |
| Gamma rate (nGy/h) | ≤ 59 | 59–1000 | ≥ 1000 |
| Ra-eq (Bq/kg) | ≤ 370 | 370–740 | ≥ 740 |

- **Irish national radon action level: 200 Bq/m³** (stricter than EU BSS 300)
- WHO reference: 100 Bq/m³
- UNSCEAR 2024 global average: 2.2 mSv/yr

## Key Features

- **Tellus airborne radiometric** (K, U, Th) used where available — measurement-grade, overrides lithology prior
- **EPA radon risk map** used as validation — 1 km grid predicted indoor radon
- **Irish 200 Bq/m³ action level** in risk classification
- **GSI Bedrock 1:100k** lithology backbone — 100m resolution
- **Teagasc soil properties** for permeability
- Satellite basemap (Esri World Imagery) at town zoom
