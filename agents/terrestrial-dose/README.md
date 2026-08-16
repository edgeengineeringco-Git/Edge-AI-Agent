# Irish Terrestrial Dose Indicator — v5.0

**Commercial-grade interactive web application** estimating terrestrial radiation dose (radon + thoron + gamma) for every point in Ireland at 100m resolution.

Built for: MDPI Air journal special issue "Radon in the Environment"
Regulatory: EU BSS 2013/59/Euratom, Irish action level 200 Bq/m³

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

## Data Layout

```
data/
  gsi_bedrock_100k.tif           # lithology class raster
  tellus_radiometric_k.tif       # K (%) raster
  tellus_radiometric_u.tif       # eU (ppm) raster
  tellus_radiometric_th.tif      # eTh (ppm) raster
  epa_radon_map.tif              # predicted radon Bq/m³
  teagasc_soil_permeability.tif  # permeability class raster
  gsi_faults.geojson             # fault lines
  corine_landcover.tif           # land cover code
  sentinel2_ndvi.tif             # NDVI (optional)
  esa_cci_soil_moisture.tif      # soil moisture (optional)
  era5_season.json               # {"season": "winter"}
```

**Until these files are provided**, `/health` reports them as not loaded, and `/dose` returns `missing_layers` listing every one. The report panel shows the honest "no data" state. This is correct behavior — do not "fix" it by inventing data.

## Quick Start

```bash
pip install fastapi uvicorn numpy rasterio shapely geopandas cachetools requests
pytest tests/
uvicorn api.dose_backend:app --reload --port 8000
```

## Risk Classification

| Tier | Criteria |
|------|----------|
| GREEN | ≤ 2.2 mSv/yr (≤ UNSCEAR world average) |
| AMBER | 2.2–6.6 mSv/yr (1–3× average) |
| RED | > 6.6 mSv/yr OR radon ≥ 200 Bq/m³ OR Ra-eq ≥ 370 OR gamma ≥ 1000 nGy/h |

## Constants & Citations

| Constant | Value | Source |
|----------|-------|--------|
| DCC Ra-226 | 0.462 nGy/h per Bq/kg | UNSCEAR 2000 Annex B Table 13 |
| DCC Th-232 | 0.604 nGy/h per Bq/kg | UNSCEAR 2000 Annex B Table 13 |
| DCC K-40 | 0.0417 nGy/h per Bq/kg | UNSCEAR 2000 Annex B Table 13 |
| eU→Ra-226 | 12.22 Bq/kg per ppm | UNSCEAR 2000 Annex B Table 1 |
| eTh→Th-232 | 4.06 Bq/kg per ppm | UNSCEAR 2000 Annex B Table 1 |
| K→K-40 | 313 Bq/kg per % | UNSCEAR 2000 Annex B Table 1 |
| Occupancy factor | 0.7 | ICRP 103 (2007) |
| Radon DCC | 0.009 mSv/yr per Bq/m³ | UNSCEAR 2006 Annex E |
| Tn/Rn ratio | 0.10 | UNSCEAR 2006 Annex E |
| World average | 2.2 mSv/yr | UNSCEAR 2008 Annex B |
| Irish action level | 200 Bq/m³ | SI No. 310 of 2000 |
| Ra-eq threshold | 370 Bq/kg | EU BSS 2013/59/Euratom |
