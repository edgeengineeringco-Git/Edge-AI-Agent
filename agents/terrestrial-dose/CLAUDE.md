# Terrestrial Dose Agent

Interactive web GIS that estimates terrestrial radiation dose (radon-222, thoron-220, external gamma) at any European land point.

## Scope

`agents/terrestrial-dose`

## Architecture

```
terrestrial-dose/
├── dose_core/
│   └── dose_calculation_core.py    # Core dose formulas (DO NOT MODIFY)
├── tests/
│   └── test_dose_core.py           # 6 validation tests
├── models/
│   ├── point_table.py              # Fixed raw-data table schema
│   └── sample_point.py             # sample_raw_data + analyze_point
├── analysis/
│   └── short_report.py             # Templated ≤8-line report
├── api/
│   └── main.py                     # FastAPI backend
├── ingest/                         # Data ingest modules
│   ├── point_sampler.py            # Main sampler entry point
│   ├── data_pipeline.py            # Inventory + provenance
│   ├── cache.py                    # GeoPackage cache
│   ├── glim.py                     # GLiM geology
│   ├── soilgrids.py                # SoilGrids 250m
│   ├── faults.py                   # GEM faults
│   └── ...
├── web/                            # React + MapLibre source
│   ├── src/
│   │   ├── dose_core.ts            # TS port of dose formulas
│   │   ├── lithology.ts            # European geology mosaic
│   │   ├── analysis.ts             # Client-side analyze + report
│   │   ├── Map.tsx                 # MapLibre + hover triangle
│   │   ├── Triangle.tsx            # D3 three-arm dose triangle
│   │   ├── Panel.tsx               # Right-side report panel
│   │   ├── App.tsx                 # Main layout
│   │   └── styles.css              # Dark theme
│   ├── package.json
│   └── vite.config.ts
├── app/                            # Built output → copy to public repo
└── README.md
```

## Two-Repo Setup

- **Agent source** (this repo): `agents/terrestrial-dose/`
- **Public site** (deployed): `https://github.com/edgeengineeringco-Git/edge-ai-agent-site/tree/main/terrestrial-dose/app/`

Build the frontend here (`web/`), then copy `app/` to the public repo.

## Source

https://github.com/edgeengineeringco-Git/edge-ai-agent-site/tree/main/terrestrial-dose

## Running

```bash
# Tests
cd agents/terrestrial-dose
python3 -c "
import sys; sys.path.insert(0, '.')
from tests.test_dose_core import *
test_world_average_soil(); test_granite_amber(); test_carbonate_green()
test_monazite_red(); test_measurement_override(); test_radon_action_level()
print('All passed')
"

# API server (requires fastapi + uvicorn)
python3 -m uvicorn api.main:app --reload --port 8000

# Frontend dev
cd web && npm install && npm run dev

# Frontend build → app/
cd web && npm run build && rm -rf ../app && cp -r dist ../app
```

## API Endpoints

- `GET /dose?lat=53.35&lon=-6.26` — full dose fingerprint + raw table + report
- `GET /dose/bbox?south=48&west=5&north=55&east=15&step=1` — GeoJSON grid for map tiles
- `GET /health` — health check

## Dose Standards

| Metric | GREEN | AMBER | RED |
|--------|-------|-------|-----|
| Total dose (mSv/yr) | ≤ 2.2 | 2.2–6.6 | > 6.6 |
| Radon (Bq/m³) | ≤ 100 | 100–300 | ≥ 300 |
| Gamma rate (nGy/h) | ≤ 59 | 59–1000 | ≥ 1000 |
| Ra-eq (Bq/kg) | ≤ 370 | 370–740 | ≥ 740 |
