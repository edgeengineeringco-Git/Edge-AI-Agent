# Irish Terrestrial Dose Indicator

**Commercial-grade interactive web application** estimating terrestrial radiation dose (radon, thoron, gamma) for every point in Ireland at 100m resolution.

Built for: MDPI Air journal special issue "Radon in the Environment"  
Regulatory: EU BSS 2013/59/Euratom, Irish action level 200 Bq/m³  
Live: https://edgeengineeringco-git.github.io/edge-ai-agent-site/irish-dose.html

## Architecture

**Backend** (`api/dose_backend.py`):
- FastAPI serving `/dose`, `/dose/bbox`, `/health`
- RasterLayer class for GeoTIFF sampling (rasterio)
- Checks actual file existence on disk at request time
- If file missing: returns null + `missing_layers` array
- Every dose number carries its own `derivation` string with formula, inputs, and cited coefficient source
- TTLCache for computed responses (1h TTL)

**Frontend** (`irish-dose-standalone.html`):
- MapLibre satellite basemap with toggle (Satellite/Bing/Streets)
- Search bar (Nominatim geocoding)
- Cursor triangle (48x48px SVG) tracking mouse with proportional arms
- 100ms debounced hover → API call
- Click-to-pin toggle
- Risk choropleth overlay (zoom < 10)
- Bottom badges: cell size, Tellus, EPA radon
- Full report panel: dose fingerprint triangle, "Why this dose?", factors table, confidence meter, source badges, provenance footer

## Rules (enforced)

1. **No hardcoded physical values** — every dose number computed from real data
2. **No synthetic demo mode** — missing data shows "No data available"
3. **No false provenance** — labels reflect actual source
4. **Every number carries derivation** — exact formula + coefficient source
5. **Fail loudly** — HTTP errors, never silent substitution
6. **No fake UI** — honest empty state
7. **Audit before handoff** — grep for all numbers, justify each
8. **Build everything in one pass** — all sections present

## Data Files

Place in `data/` directory:

```
data/
  gsi_bedrock_100k.tif           # lithology class raster, EPSG:4326
  tellus_radiometric_k.tif       # K (%) raster
  tellus_radiometric_u.tif       # eU (ppm) raster
  tellus_radiometric_th.tif      # eTh (ppm) raster
  epa_radon_map.tif              # predicted radon Bq/m3
  teagasc_soil_permeability.tif  # permeability class
  gsi_faults.geojson             # fault lines
  corine_landcover.tif           # land cover code
  sentinel2_ndvi.tif             # NDVI (optional)
  esa_cci_soil_moisture.tif      # soil moisture (optional)
  era5_season.json               # {"season": "winter"}
```

**Until these are provided:** `/health` reports them as not loaded. `/dose` returns `missing_layers` listing every one. The UI shows "No data available" for each missing layer. **This is correct behavior — do not "fix" it by inventing data.**

## Quick Start

```bash
pip install -r requirements.txt
pytest tests/
uvicorn api.dose_backend:app --reload --port 8000
```

## Risk Classification

| Tier | Criteria | Source |
|------|----------|--------|
| GREEN | ≤ 2.2 mSv/yr | UNSCEAR 2000 Annex A Table 2 (world average) |
| AMBER | 2.2–6.6 mSv/yr | 1–3× world average |
| RED | > 6.6 mSv/yr | 3× world average |
| RED | Radon ≥ 200 Bq/m³ | Irish Building Regulations 1997 (SI 496) |
| RED | Ra-eq ≥ 370 Bq/kg | UNSCEAR 2000 Annex B |
| RED | Gamma ≥ 1000 nGy/h | ICRP reference level |

## Verification Tests

1. Delete `data/epa_radon_map.tif`, restart → UI shows "No data" for radon only
2. Call `/dose` for Atlantic Ocean point → returns water-body state with zero values
3. Cursor triangle arms visibly change between different geological locations
4. All numbers in UI match numbers in API response

## Standards

- UNSCEAR 2000 (dose coefficients, world average)
- UNSCEAR 2006 Annex E (radon/thoron DCC)
- ICRP 103 (2007) (occupancy factor)
- EU BSS 2013/59/Euratom
- Irish Building Regulations 1997 (SI 496 of 1997)
