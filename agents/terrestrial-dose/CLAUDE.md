# Irish Terrestrial Dose Indicator — Agent Context

## Purpose
Commercial-grade interactive web application estimating terrestrial radiation dose (radon, thoron, gamma) for every point in Ireland at 100m resolution. Built for MDPI Air journal special issue "Radon in the Environment".

## Architecture

**Backend API** (`api/dose_backend.py`):
- FastAPI serving `/dose`, `/dose/bbox`, `/health`
- Loads real GeoTIFF raster data (rasterio)
- Tellus radiometric K/U/Th, EPA radon, Teagasc soils, GSI faults
- Falls back to lithology priors when rasters missing
- Proper UNSCEAR 2024 dose conversion coefficients
- TTLCache for computed results

**Frontend** (`irish-dose-standalone.html`):
- MapLibre satellite basemap
- Connects to backend `/dose` endpoint on click
- WMS overlays for map display (toggleable)
- Bottom panel: data sources + dose summary
- Confidence meter with provenance trail
- Short report (8 templated lines)

```
agents/terrestrial-dose/
├── dose_core/
│   └── dose_calculation_core.py   # Core dose formulas (legacy, used by tests)
├── api/
│   └── dose_backend.py            # FastAPI backend — THE MAIN API
├── models/
│   ├── sample_point.py            # Assembles raw data table (legacy)
│   └── analyze_point.py           # Steps A–H (legacy)
├── analysis/
│   └── short_report.py            # Templated ≤8-line report (legacy)
├── data/                          # Runtime raster data (not committed)
│   ├── gsi_bedrock_100k.tif
│   ├── tellus_radiometric_k.tif
│   ├── tellus_radiometric_u.tif
│   ├── tellus_radiometric_th.tif
│   ├── epa_radon_map.tif
│   ├── teagasc_soil_permeability.tif
│   ├── gsi_faults.geojson
│   ├── corine_landcover.tif
│   └── era5_season.json
├── irish-dose-standalone.html     # Frontend HTML (deployed)
├── tests/
│   └── test_dose_core.py
├── Dockerfile
├── requirements.txt
├── SYSTEM.md
├── CLAUDE.md
└── README.md
```

## Key Rules
1. **Ireland only** — bounding box: 51.4–55.4°N, 10.6–5.3°W
2. **Backend does all dose math** — frontend just displays results
3. **Real raster data** — loads GeoTIFF/GeoJSON, falls back to priors
4. **No invented values** — None = unavailable, shown honestly
5. **No LLM free-text** — templates only
6. **Irish 200 Bq/m³** action level (stricter than EU 300)
7. **Paper-ready** — every number traceable to UNSCEAR/ICRP/EU BSS

## Risk Classification
- GREEN: ≤ 2.2 mSv/yr (≤ UNSCEAR world average)
- AMBER: 2.2–6.6 mSv/yr (1–3× average)
- RED: > 6.6 mSv/yr OR radon ≥ 200 Bq/m³ OR Ra-eq ≥ 370 OR gamma ≥ 1000 nGy/h

## Data Sources
| Layer | File | Source | Resolution |
|-------|------|--------|-----------|
| Bedrock | gsi_bedrock_100k.tif | GSI Bedrock 1:100k | 100m |
| K | tellus_radiometric_k.tif | Tellus airborne | ~200m |
| U | tellus_radiometric_u.tif | Tellus airborne | ~200m |
| Th | tellus_radiometric_th.tif | Tellus airborne | ~200m |
| Radon | epa_radon_map.tif | EPA Radon Risk | 1km |
| Soils | teagasc_soil_permeability.tif | Teagasc SIS | mapped |
| Faults | gsi_faults.geojson | GSI structural | vector |
| Land cover | corine_landcover.tif | Corine | 100m |
| NDVI | sentinel2_ndvi.tif | Sentinel-2 | 10m (opt) |
| Moisture | esa_cci_soil_moisture.tif | ESA CCI | 25km (opt) |
| Season | era5_season.json | ERA5 | seasonal |

## Standalone HTML
The file `irish-dose-standalone.html` is deployed to:
https://edgeengineeringco-git.github.io/edge-ai-agent-site/irish-dose.html

To update: copy the file to the public repo and push.
