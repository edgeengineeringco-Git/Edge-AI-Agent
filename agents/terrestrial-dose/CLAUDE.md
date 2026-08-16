# Irish Terrestrial Dose Indicator — Agent Context

## Purpose
Commercial-grade interactive web application estimating terrestrial radiation dose (radon, thoron, gamma) for every point in Ireland at 100m resolution. Built for MDPI Air journal special issue "Radon in the Environment".

## Architecture

```
agents/terrestrial-dose/
├── dose_core/
│   └── dose_calculation_core.py   # SINGLE SOURCE OF TRUTH — do not modify
├── models/
│   ├── sample_point.py            # Assembles fixed raw data table at lat/lon
│   └── analyze_point.py           # Steps A–H (the smart agent analysis)
├── analysis/
│   └── short_report.py            # Templated ≤8-line report (no LLM)
├── api/
│   └── main.py                    # FastAPI: /dose, /dose/bbox, /health
├── web/src/                       # React + TypeScript + MapLibre
│   ├── dose_core.ts               # TypeScript port of dose core
│   ├── lithology.ts               # Ireland GSI 1:100k geology regions
│   ├── Map.tsx                    # MapLibre satellite + hover + click
│   ├── Triangle.tsx               # D3 three-arm dose triangle
│   ├── Report.tsx                 # Right panel: triangle + report + factors
│   └── App.tsx                    # Two-pane layout
├── tests/
│   └── test_dose_core.py          # 6 validation tests
├── irish-dose-standalone.html     # Self-contained HTML (deployed)
├── Dockerfile
├── requirements.txt
├── .env.example
├── SYSTEM.md                      # Agent identity and instructions
├── CLAUDE.md                      # This file
└── README.md                      # Project documentation
```

## Key Rules
1. **Ireland only** — bounding box: 51.4–55.4°N, 10.6–5.3°W
2. **No dose math outside dose_calculation_core.py** — import, never rewrite
3. **No invented values** — None = unavailable, shown honestly
4. **No LLM free-text** — templates only (short_report.py)
5. **Data hierarchy**: Tellus measured > GSI stream > lithology prior
6. **EPA radon = validation** — never replaces the model
7. **Irish 200 Bq/m³** action level (stricter than EU 300)
8. **Paper-ready** — every number traceable to UNSCEAR/ICRP/EU BSS

## Risk Classification
- GREEN: ≤ 2.2 mSv/yr (≤ UNSCEAR world average)
- AMBER: 2.2–6.6 mSv/yr (1–3× average)
- RED: > 6.6 mSv/yr OR radon ≥ 200 Bq/m³ OR Ra-eq ≥ 370 OR gamma ≥ 1000 nGy/h

## Data Sources (21 total)

### WMS Connected (6 active)
| # | Source | WMS Endpoint | Role |
|---|--------|--------------|------|
| 1 | GSI Bedrock 1:100k | gsi.geodata.gov.ie/server/services/Bedrock/.../WMSServer | Lithology backbone |
| 2 | GSI Quaternary | gsi.geodata.gov.ie/server/services/Quaternary/.../WMSServer | Cover deposits |
| 3 | GSI Groundwater | gsi.geodata.gov.ie/server/services/Groundwater/.../WMSServer | Aquifer overlay |
| 4 | GSI Geochemistry | gsi.geodata.gov.ie/server/services/Geochemistry/.../WMSServer | Stream sediment trace elements |
| 6 | GSI Faults | gsi.geodata.gov.ie/server/services/Bedrock/.../WMSServer | Geological lines overlay |
| 7 | EPA Radon Risk | gis.epa.ie/geoserver/EPA/wms | Radon risk zone |
| 9 | Teagasc Soils | gis.epa.ie/geoserver/EPA/wms | Soil type, drainage |

### WMS Unavailable (3)
| # | Source | Reason |
|---|--------|--------|
| 5 | GSI Geophysics (Tellus K/U/Th) | Service returning 499 |
| 8 | EPA Radiation Monitoring | No public WMS endpoint |
| 10-15 | Copernicus/NOAA/ISRIC | Need instance IDs or proxy |

### Download Only (6)
| # | Source | Format |
|---|--------|--------|
| 16 | ERA5 | NetCDF/GRIB (cdsapi) |
| 17 | ESA CCI Soil Moisture | NetCDF |
| 18 | WGM Gravity (BGI) | GeoTIFF |
| 19 | Eurostat GEOSTAT | CSV/GeoTIFF |
| 20 | GEM Active Faults | Shapefile/GeoJSON |
| 21 | Copernicus GLO-30 DEM | GeoTIFF |

## Standalone HTML
The file `irish-dose-standalone.html` is deployed to:
https://edgeengineeringco-git.github.io/edge-ai-agent-site/irish-dose.html

To update: copy the file to the public repo and push.
