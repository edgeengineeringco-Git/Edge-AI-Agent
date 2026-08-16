# Irish Terrestrial Dose Indicator

**Commercial-grade interactive web application** estimating terrestrial radiation dose (radon, thoron, gamma) for every point in Ireland at 100m resolution.

Built for: MDPI Air journal special issue "Radon in the Environment"
Regulatory: EU BSS 2013/59/Euratom, Irish action level 200 Bq/m³

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

## Data Layout

```
data/
  gsi_bedrock_100k.tif           # lithology class raster, EPSG:4326, ~100m
  tellus_radiometric_k.tif       # K (%) raster
  tellus_radiometric_u.tif       # eU (ppm) raster
  tellus_radiometric_th.tif      # eTh (ppm) raster
  epa_radon_map.tif              # predicted radon Bq/m3, 1km grid
  teagasc_soil_permeability.tif  # permeability class raster
  gsi_faults.geojson             # fault lines, EPSG:4326
  corine_landcover.tif           # land cover code
  sentinel2_ndvi.tif             # NDVI, 10m (optional)
  esa_cci_soil_moisture.tif      # volumetric soil moisture (optional)
  era5_season.json               # {"season": "winter"} - updated externally
```

## Quick Start

```bash
pip install -r requirements.txt
pytest tests/
uvicorn api.dose_backend:app --reload --port 8000
```

## Risk Classification

| Tier | Criteria |
|------|----------|
| GREEN | ≤ 2.2 mSv/yr (≤ UNSCEAR world average) |
| AMBER | 2.2–6.6 mSv/yr (1–3× average) |
| RED | > 6.6 mSv/yr OR radon ≥ 200 Bq/m³ (Irish) OR Ra-eq ≥ 370 OR gamma ≥ 1000 nGy/h |

**Irish action level: 200 Bq/m³** (stricter than EU BSS 300 Bq/m³)

## WMS Overlays (map display only)

| # | Source | Endpoint | Layer |
|---|--------|----------|-------|
| 1 | GSI Bedrock 1:100k | gsi.geodata.gov.ie/server/services/Bedrock/.../WMSServer | IE_GSI_Bedrock_Geology_100K_IE26_ITM |
| 2 | GSI Quaternary | gsi.geodata.gov.ie/server/services/Quaternary/.../WMSServer | IE_GSI_Quaternary_Sediments_50K_IE26_ITM |
| 3 | GSI Groundwater | gsi.geodata.gov.ie/server/services/Groundwater/.../WMSServer | IE_GSI_Groundwater_Recharge_40K_IE26_ITM |
| 4 | GSI Geochemistry | gsi.geodata.gov.ie/server/services/Geochemistry/.../WMSServer | C_XRFS_Lanthanum_(La)_(mg_kg¯¹)52276 |
| 5 | GSI Faults | gsi.geodata.gov.ie/server/services/Bedrock/.../WMSServer | IE_GSI_Geological_Lines_100K_IE26_ITM |
| 6 | EPA Radon Risk | gis.epa.ie/geoserver/EPA/wms | EPA:RadonRiskMapofIreland |
| 7 | Teagasc Soils | gis.epa.ie/geoserver/EPA/wms | EPA:SOIL_SISNationalSoils |

## Standards

- UNSCEAR 2024, ICRP 137, EU BSS 2013/59/Euratom
- Every number traceable to source (provenance trail)
- No invented values (None = unavailable, shown honestly)
- No LLM free-text (templates only)
