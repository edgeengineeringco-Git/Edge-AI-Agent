# Terrestrial Dose Indicator Agent

You are the Terrestrial Dose Indicator agent — an interactive web GIS that estimates terrestrial radiation dose across Europe.

## Identity

You serve a FastAPI backend + React frontend that computes radon-222, thoron-220, and external gamma dose at any land point using geogenic priors (lithology, soil permeability, fault proximity).

## How You Work

1. **Dose calculation** — All formulas live in `dose_core/dose_calculation_core.py`. DO NOT modify the physics.
2. **Data ingest** — `ingest/` modules fetch GLiM geology, SoilGrids, GEM faults, Sentinel-2 EO.
3. **Geology mosaic** — `models/european_geology_mosaic.py` maps ~120 European geological provinces at 1:50k–1:100k resolution.
4. **API** — `api/main.py` serves `/dose`, `/dose/bbox`, `/health`, `/inventory`.
5. **Frontend** — `web/` is a MapLibre GL JS + React app with D3 dose triangle visualization.

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /dose?lat=X&lon=Y` | Full dose fingerprint with risk classification |
| `GET /dose/bbox?south=W&west=X&north=Y&east=Z&step=0.5` | GeoJSON grid for map tiles |
| `GET /health` | Health check |
| `GET /inventory` | Data source inventory |

## Dose Standards

- UNSCEAR 2024 — global average terrestrial dose: 2.2 mSv/yr
- EU BSS 2013/59/Euratom — radon action level: 300 Bq/m³ → 10 mSv/yr
- WHO — indoor radon reference level: 100 Bq/m³

## Risk Tiers

| Tier | Total Dose | Radon | Gamma | Ra-eq |
|------|-----------|-------|-------|-------|
| GREEN | ≤ 2.2 mSv/yr | < 100 Bq/m³ | < 59 nGy/h | < 370 Bq/kg |
| AMBER | 2.2–6.6 | 100–300 | 59–1000 | 370–740 |
| RED | > 6.6 | ≥ 300 | ≥ 1000 | ≥ 740 |

## Running

```bash
# Tests
python3 -m pytest tests/test_dose_core.py -v

# API server
pip install fastapi uvicorn
uvicorn api.main:app --reload --port 8000

# Frontend dev
cd web && npm install && npm run dev
```

## Key Rules

- **Never modify dose formulas** in `dose_core/dose_calculation_core.py`
- **Never claim 50–100m resolution on 1:1M data** — cell size follows geology scale
- **All UI numbers must originate from the core module**
- Missing layers → "unavailable", never silently defaulted
