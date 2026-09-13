# National REE Prospectivity System for Ireland

> **Status (2026-09-13):** L1 eTh ✅ CONFIRMED · L2 eU ✅ CONFIRMED · L3 K+eTh/K ✅ CONFIRMED · **L4 Magnetics ⛔ NULL (blocked)**.
> Pipeline halted at L4 per protocol (no layer past an unconfirmed/NULL layer).
>
> **Root-cause blocker (environment, not data):** GSI Geophysics REST serves airborne grids
> **only as rendered RGB** — `export`→PNG, `identify`→colormap RGB, WMS `GetFeatureInfo` disabled,
> no `ImageServer`, **WCS not enabled**. GDAL/WCS cannot be installed (non-root container, PEP 668).
> L1–L3 were salvaged because a genuine resampled raw product (`values.bin`) already existed in the
> project; **no magnetic derivative exists**, so L4 raw nT is unretrievable here.
> **Resolution needed for L4 (and native-50 m for L1–L3):** root + GDAL to use WCS/REST, or supply a
> raw grid file/mirror. See `reports/L4.md`.

Built strictly layer-by-layer per the ADD-CONFIRM protocol (L1–L18), then a
critically-rebuilt scoring system (Stage 2, S1–S7). Every layer must carry a
written CONFIRMED status in `layer_confirmation.csv` before Stage 2 begins.

## Layout
- `config.yaml` — single source of weights, priors, thresholds (nothing hardcoded in code)
- `layer_confirmation.csv` — audit trail; one row per layer (ADD-INSPECT-VERIFY-CROSS-CONFIRM)
- `scripts/` — reusable inspect/verify helpers (pure-Python: numpy/pandas/pyproj/pyshp/PIL)
- `reports/` — one short status paragraph per layer / S-step
- `data/` — **NOT committed**. Actual downloaded rasters/tables live in `/tmp/ree_data`
  (ephemeral between turns). Only `config.yaml`, the CSV, scripts and reports are committed.

## Environment
- Python 3.12; pip via `--break-system-packages`; stack: numpy pandas requests pyproj
  pyshp pyyaml scipy Pillow. No GDAL/rasterio (avoided — TIFFs read via Pillow/numpy).
- Data sources: GSI open data (gsi.geodata.gov.ie ArcGIS REST + data.gov.ie), Copernicus
  Data Space (dataspace.copernicus.eu).

## Discipline
- One layer at a time. No batching. No deferred verification. No fabrication.
- A layer is CONFIRMED, FAILED (2 retries then NULL), or NULL. No fourth state.
- Uncertainty is stated explicitly; an honest limitation beats a clean result.
