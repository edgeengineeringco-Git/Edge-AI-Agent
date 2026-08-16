# Irish Terrestrial Dose Indicator

**Commercial-grade interactive web application** that estimates and visualises terrestrial radiation dose (radon, thoron, gamma) for every point in Ireland at 100m resolution.

Built for: MDPI Air journal special issue "Radon in the Environment"
Regulatory: EU BSS 2013/59/Euratom, Irish action level 200 Bq/m³

## Data Architecture

| Layer | Source | Resolution | Role |
|-------|--------|-----------|------|
| Bedrock geology | GSI Bedrock 1:100k ITM | 100m | Lithology backbone |
| Tellus radiometric | GSI Tellus (K/U/Th) | ~200m | Measured activities — overrides prior |
| EPA radon risk map | EPA Ireland | 1km grid | Predicted radon — validation |
| Teagasc soil system | Teagasc Irish SIS | mapped | Soil class, permeability, drainage |
| GSI faults | GSI structural | vector | Radon migration pathways |

### Data Hierarchy (best source wins)
1. **Tellus airborne radiometric** (measured K/U/Th, ~200m) — measurement grade
2. **GSI stream sediment geochemistry** (measured U/Th/K, point)
3. **Lithology prior** from GSI 1:100k (estimated, 100m)

## Risk Classification

| Tier | Criteria |
|------|----------|
| GREEN | ≤ 2.2 mSv/yr (≤ UNSCEAR world average) |
| AMBER | 2.2–6.6 mSv/yr (1–3× average) |
| RED | > 6.6 mSv/yr OR radon ≥ 200 Bq/m³ (Irish) OR Ra-eq ≥ 370 OR gamma ≥ 1000 nGy/h |

**Irish action level: 200 Bq/m³** (stricter than EU BSS 300 Bq/m³)

## Quick Start

```bash
pip install -r requirements.txt
pytest tests/
uvicorn api.main:app --reload --port 8000
```

## API Endpoints

- `GET /health` — Status check
- `GET /dose?lat=52.98&lon=-6.3` — Dose analysis at point
- `GET /dose/bbox?lat_min=52.5&lat_max=53.5&lon_min=-7&lon_max=-6&step_km=2` — Grid analysis

## Standalone HTML

`irish-dose-standalone.html` — self-contained HTML with inline CSS/JS, MapLibre from CDN. Open directly in browser or deploy to any static host.

## Docker

```bash
docker build -t irish-dose .
docker run -p 8000:8000 irish-dose
```

## Standards

- UNSCEAR 2024, ICRP 137, EU BSS 2013/59/Euratom
- Every number traceable to source (provenance trail visible)
- No invented values (None = unavailable, shown honestly)
- No LLM free-text analysis (templates only)
