# Terrestrial Dose Agent

Interactive web GIS that estimates terrestrial radiation dose (radon-222, thoron-220, external gamma) at any European land point.

## Architecture

```
terrestrial-dose/
├── dose_core/
│   └── dose_calculation_core.py   # Core dose formulas (DO NOT MODIFY)
├── tests/
│   └── test_dose_core.py          # 6 validation tests
├── api/
│   └── main.py                    # FastAPI backend
├── ingest/                        # Data ingest modules
│   ├── glim.py                    # GLiM geology
│   ├── soilgrids.py               # SoilGrids permeability
│   ├── faults.py                  # GEM faults
│   ├── sentinel2.py               # Sentinel-2 EO
│   └── cache.py                   # Cache management
├── models/
│   ├── european_geology_mosaic.py # ~120 European geological provinces
│   └── assemble_factors.py        # Multi-factor dose driver assembly
├── web/
│   ├── src/
│   │   ├── dose_core.ts           # TypeScript port of dose formulas
│   │   ├── lithology.ts           # European geological provinces
│   │   ├── analysis.ts            # Templated "Why this dose?" generator
│   │   ├── Map.tsx                # MapLibre GL JS satellite map
│   │   ├── Panel.tsx              # Full analysis card
│   │   ├── Triangle.tsx           # D3 three-arm dose triangle
│   │   └── App.tsx                # Main layout
│   └── package.json
├── data/cache/                    # Runtime cache (not committed)
└── README.md
```

## Running

```bash
# Tests
python3 -m pytest tests/test_dose_core.py -v

# API
pip install fastapi uvicorn
uvicorn api.main:app --reload --port 8000

# Frontend
cd web && npm install && npm run dev
```

## API Endpoints

- `GET /dose?lat=53.35&lon=-6.26` — full dose fingerprint
- `GET /dose/bbox?south=48&west=5&north=55&east=15&step=1` — grid for map tiles
- `GET /health` — health check

## Dose Standards

| Metric | GREEN | AMBER | RED |
|--------|-------|-------|-----|
| Total dose (mSv/yr) | ≤ 2.2 | 2.2–6.6 | > 6.6 |
| Radon (Bq/m³) | ≤ 100 | 100–300 | ≥ 300 |
| Gamma rate (nGy/h) | ≤ 59 | 59–1000 | ≥ 1000 |
| Ra-eq (Bq/kg) | ≤ 370 | 370–740 | ≥ 740 |
