# Irish Terrestrial Dose Indicator

**Commercial-grade interactive web application** that estimates and visualises terrestrial radiation dose (radon, thoron, gamma) for every point in Ireland at 100m resolution.

Built for: MDPI Air journal special issue "Radon in the Environment"
Regulatory: EU BSS 2013/59/Euratom, Irish action level 200 Bq/m³

## Data Architecture

### 21 Data Sources

#### WMS Connected (6 active)
| # | Source | Endpoint | Role |
|---|--------|----------|------|
| 1 | GSI Bedrock Geology 1:100k | `gsi.geodata.gov.ie/server/services/Bedrock/.../WMSServer` | Lithology backbone |
| 2 | GSI Quaternary Deposits | `gsi.geodata.gov.ie/server/services/Quaternary/.../WMSServer` | Cover deposits |
| 3 | GSI Groundwater & Aquifers | `gsi.geodata.gov.ie/server/services/Groundwater/.../WMSServer` | Aquifer overlay |
| 4 | GSI Geochemistry (Tellus) | `gsi.geodata.gov.ie/server/services/Geochemistry/.../WMSServer` | Stream sediment trace elements |
| 6 | GSI Faults & Lineaments | `gsi.geodata.gov.ie/server/services/Bedrock/.../WMSServer` | Geological lines overlay |
| 7 | EPA Radon Risk Map | `gis.epa.ie/geoserver/EPA/wms` | Radon risk zone validation |
| 9 | Teagasc Irish Soil Info | `gis.epa.ie/geoserver/EPA/wms` | Soil type, drainage |

#### WMS Unavailable (3)
| # | Source | Reason |
|---|--------|--------|
| 5 | GSI Geophysics (Tellus K/U/Th) | Service returning 499 |
| 8 | EPA Radiation Monitoring | No public WMS endpoint |
| 10-15 | Copernicus/NOAA/ISRIC | Need instance IDs or proxy |

#### Download Only (6)
| # | Source | Format |
|---|--------|--------|
| 16 | ERA5 | NetCDF/GRIB (cdsapi) |
| 17 | ESA CCI Soil Moisture | NetCDF |
| 18 | WGM Gravity (BGI) | GeoTIFF |
| 19 | Eurostat GEOSTAT | CSV/GeoTIFF |
| 20 | GEM Active Faults | Shapefile/GeoJSON |
| 21 | Copernicus GLO-30 DEM | GeoTIFF |

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

`irish-dose-standalone.html` — self-contained HTML with:
- Real WMS GetFeatureInfo queries (not hardcoded data)
- All 21 data sources listed with status
- Layer toggle panel for WMS overlays
- Bottom panel: data source table + dose summary
- Irish 200 Bq/m³ action level
- GREEN/AMBER/RED risk classification per EU BSS

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
