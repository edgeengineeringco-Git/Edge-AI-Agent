# Irish Terrestrial Dose Indicator — Agent Context (v5.0)

## Purpose
Commercial-grade interactive web application estimating terrestrial radiation dose (radon, thoron, gamma) for every point in Ireland at 100m resolution. Built for MDPI Air journal special issue "Radon in the Environment".

## Architecture

**Backend** (`api/dose_backend.py`, 657 lines):
- FastAPI serving `/health`, `/dose`, `/dose/bbox`
- RasterLayer class for real GeoTIFF sampling via rasterio
- Named constants for all physical values (UNSCEAR/ICRP cited)
- Derivation strings for every computed number
- TTLCache for computed responses
- Honest missing-data handling (null, not guesses)

**Frontend** (`irish-dose-standalone.html`, 635 lines):
- Two-pane layout: map (flex:1.5) + report (flex:1)
- MapLibre satellite basemap + Bing/Streets toggle
- Search bar with Nominatim geocoding
- Cursor triangle (SVG) with proportional arms
- Hover interaction (100ms debounce) → real API calls
- Click-to-pin functionality
- Risk choropleth overlay at zoom < 10
- Dose fingerprint triangle SVG
- "Why this dose?" card with colour-coded bullets
- Factors table with direction arrows
- Confidence meter with gradient bar
- Data source badges (measured/modelled/unavailable)
- Provenance footer with standards citations
- Derivation panel (expandable)
- Water body detection
- Missing data = honest "no data" state

```
agents/terrestrial-dose/
├── api/dose_backend.py            # FastAPI backend (THE MAIN API)
├── dose_core/dose_calculation_core.py  # Core dose formulas (legacy/tests)
├── irish-dose-standalone.html     # Frontend HTML (deployed)
├── data/                          # Runtime raster data (not committed)
│   ├── gsi_bedrock_100k.tif
│   ├── tellus_radiometric_k.tif
│   ├── tellus_radiometric_u.tif
│   ├── tellus_radiometric_th.tif
│   ├── epa_radon_map.tif
│   ├── teagasc_soil_permeability.tif
│   ├── gsi_faults.geojson
│   └── era5_season.json
├── tests/test_dose_core.py
├── Dockerfile
├── requirements.txt
├── SYSTEM.md
├── CLAUDE.md
└── README.md
```

## Key Rules (from spec)
1. **NO hardcoded physical values** in application code outside unit tests
2. **NO synthetic demo mode** — missing data returns null, not guesses
3. **NO false provenance** — labels reflect actual source
4. **Every number carries derivation** with cited formula and inputs
5. **Fail loudly** — explicit errors, never silent substitution
6. **No fake UI states** — honest empty states
7. **Audit before handoff** — grep all numeric literals
8. **Build everything in one pass** — no "add later"

## Risk Classification
- GREEN: ≤ 2.2 mSv/yr (≤ UNSCEAR world average)
- AMBER: 2.2–6.6 mSv/yr (1–3× average)
- RED: > 6.6 mSv/yr OR radon ≥ 200 Bq/m³ OR Ra-eq ≥ 370 OR gamma ≥ 1000 nGy/h

## Data Sources (real rasters, all optional)
| Layer | File | Source |
|-------|------|--------|
| Bedrock | gsi_bedrock_100k.tif | GSI Bedrock 1:100k |
| K | tellus_radiometric_k.tif | Tellus airborne |
| eU | tellus_radiometric_u.tif | Tellus airborne |
| eTh | tellus_radiometric_th.tif | Tellus airborne |
| Radon | epa_radon_map.tif | EPA Radon Risk |
| Soils | teagasc_soil_permeability.tif | Teagasc SIS |
| Faults | gsi_faults.geojson | GSI structural |
| Land cover | corine_landcover.tif | Corine |
| NDVI | sentinel2_ndvi.tif | Sentinel-2 (opt) |
| Moisture | esa_cci_soil_moisture.tif | ESA CCI (opt) |
| Season | era5_season.json | ERA5 |

## Live URL
https://edgeengineeringco-git.github.io/edge-ai-agent-site/irish-dose.html
