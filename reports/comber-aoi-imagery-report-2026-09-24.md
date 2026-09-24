# Geospatial Imagery Evidence Report — Newtownards Road, Comber, Co. Down, BT23 5ZP

**Prepared by:** Geospatial intelligence agent (automated)
**Date of report:** 2026-09-24 (UTC) — UPDATED
**AOI:** Shoreline/marsh parcel adjoining Strangford Lough, Comber, Co. Down, Northern Ireland
**Event of interest (context only):** Item reportedly placed in an oil drum and buried in 2005. Critical window ~2002–2008, monitor to present.

> **Scope & limits.** This report (a) defines and confirms the search area, (b) records the Earth-observation (EO) data that was **actually retrieved and preserved** for this AOI with exact, reproducible URLs/dates, and (c) states honestly what image analysis could and could not be performed in this environment. It makes **no determination** about burial, concealment, or any intent. No change-detection result is presented as fact because the pixel analysis could not be completed to a verifiable standard here (see §4).

---

## 0. CONFIRMED FROM SOURCE DATA vs INFERENCE / ASSESSMENT

**CONFIRMED FROM SOURCE DATA**
- what3words `///magnetic.deeply.orbited` resolves (per what3words.com's own server-rendered metadata) to **WGS84 54.544375, −5.729841**, described by what3words as "a 3 metre square location near Comber, Co. Down."
- **29 dated, high-resolution (≈0.3–0.6 m) Wayback imagery tiles** covering the AOI centre were retrieved and preserved (years 2014–2024; exact retrieval URLs in §2).
- A **Landsat-5 scene dated 2005-11-19 (19 % cloud)** over this AOI was identified on the open Planetary Computer STAC; a **Sentinel-2 scene dated 2019-09-28 (14.8 % cloud)** was identified.
- No reference photograph and no ground-truth layers (VR-dog points, GPR/magnetometry, known dumping areas) were supplied in the workspace.

**INFERENCE / ASSESSMENT (not source-confirmed)**
- That the coordinate sits on the unsupplied reference-photo shoreline parcel (coordinate confirmed "near Comber" but the AOI polygon was not digitised — no photo supplied).
- The Irish National Grid reference is *computed/approximate* and should be re-checked with an official OSNI converter.
- That commercial historical air photos (OSNI/Bluesky/Getmapping, ~0.25–1 m, 1990s–2008) *plausibly* contain frames of this AOI — coverage not confirmed, and they are not freely retrievable.

---

## 1. AREA DEFINITION (the "area" requested)

| Field | Value | Basis |
|---|---|---|
| what3words | `///magnetic.deeply.orbited` | as supplied |
| **WGS84 latitude** | **54.544375° N** | what3words.com `og:image` minimap `lat` (server-generated) |
| **WGS84 longitude** | **−5.729841° E** | what3words.com `og:image` minimap `lng` |
| what3words description | "a 3 metre square location near Comber, Co. Down" | `og:description` |
| **Irish National Grid (EPSG:29902, computed/approx.)** | **J 47000 74333** (E 347000, N 374333) | custom WGS84→TM75 Helmert + OSNI Transverse Mercator; relative geometry validated vs Belfast/Dublin, absolute value *approximate* |
| **Search buffer (≈250 m around the point)** | lat 54.542125→54.546625; lon −5.733741→−5.725941 | simple ±250 m rectangle (planning aid only; the true shoreline parcel needs the unsupplied reference photo) |

---

## 2. EO DATA RETRIEVED & PRESERVED (the concrete deliverable)

All files are saved under `reports/evidence/wayback/` in this repository. Each was fetched from an open, dated source and is reproducible via the URLs below.

### 2a. High-resolution historical imagery — Esri "Wayback" (open, dated, ≈0.3–0.6 m)
World Imagery archival layers. Tile service (follow redirects with `-L`):
`https://wayback.maptiles.arcgis.com/arcgis/rest/services/world_imagery/mapserver/tile/{M}/18/{y}/{x}`
- Centre column `x = 126899`, rows `y = 83489/83490/83491`; neighbours `x = 126898/126900`.
- One tile ≈ 154 m wide at zoom 18 → the 3×3 grid covers ~460 m, enclosing the AOI + buffer.

| Year | Layer M | Capture date | Preserved files | Resolution |
|---|---|---|---|---|
| 2014 | 10 | 2014-02-20 | `wb2014_z18_0_0 … 2_2.jpg` (9) | ≈0.6 m (winter) |
| 2015 | 20222 | 2015-01-21 | `wb_2015_2015-01-21_c.jpg` | ≈0.6 m |
| 2016 | 3515 | 2016-01-13 | `wb_2016_2016-01-13_c.jpg` | ≈0.6 m |
| 2017 | 577 | 2017-01-11 | `wb_2017_2017-01-11_c.jpg` | ≈0.6 m |
| 2018 | 13161 | 2018-01-08 | `wb_2018_2018-01-08_c.jpg` | ≈0.6 m |
| 2019 | 6036 | 2019-01-09 | `wb_2019_2019-01-09_c.jpg` | ≈0.6 m |
| 2020 | 23001 | 2020-01-08 | `wb_2020_2020-01-08_c.jpg` | ≈0.6 m |
| 2021 | 1049 | 2021-01-13 | `wb_2021_2021-01-13_c.jpg` | ≈0.6 m |
| 2022 | 42663 | 2022-01-12 | `wb_2022_2022-01-12_c.jpg` | ≈0.6 m |
| 2023 | 11475 | 2023-01-11 | `wb_2023_2023-01-11_c.jpg` | ≈0.6 m |
| 2024 | 41468 | 2024-01-18 | `wb2024_0_0 … 2_2.jpg` (9) | ≈0.6 m |

> **Caveat:** Wayback begins in **2014** — there is **no free, dated, high-resolution imagery before 2014** covering this AOI. The 2005 event predates this archive; only coarse (Landsat, §2b) or commercial air photos (§3) cover 2002–2008 at resolvable scale.

### 2b. Identified open satellite scenes (dated, lower resolution)
- **Landsat-5, 2005-11-19 (19 % cloud)** — collection `landsat-c2-l2`, item `LT05_L2SP_206022_20051119_02_T1`. (30 m; can establish a 2005 baseline but cannot resolve a sub-30 m feature.)
- **Sentinel-2 L2A, 2019-09-28 (14.8 % cloud)** — collection `sentinel-2-l2a`, item `S2A_MSIL2A_20190928T114351_R123_T30UUF_202010`. (10 m; open via Planetary Computer STAC.)
- **Landsat WELD Daily** covers 2002–2012 (real 2005 dated 30 m composites) but is too coarse for drum-scale.

These are *identified* (confirmed to exist over the AOI) but the actual band assets were **not downloaded/decoded** in this session (see §4).

### 2c. Current imagery (undated basemap)
A current Esri World Imagery tile was also preserved (`reports/evidence/comber_current_basemap_z18_evidence.jpg`); the source does **not expose per-tile capture dates**, so it is undated and excluded from change detection.

---

## 3. SOURCES THAT COULD RESOLVE THE 2005 EVENT BUT WERE NOT RETRIEVABLE HERE

These are the only sources with resolution fine enough (~0.25–1 m) to show a buried-drum-scale disturbance in the critical 2002–2008 window. They are **commercial / orderable** and could not be downloaded without purchase or a licensed account:

| Source | Coverage | Access / ordering |
|---|---|---|
| **Bluesky / OSNI historical aerial archive (oldaerialphotos.com)** | UK & Ireland historical air photos (1940s–2000s) | https://www.oldaerialphotos.com/ (search "Comber") |
| **Getmapping historical archive** | National UK surveys (1999–present) incl. NI | https://www.getmapping.com/ |
| **UK Aerial Photos (ukaerialphotos.com)** | UK historical photos | https://www.ukaerialphotos.com/ |
| **OSNI / Land & Property Services orthophotography** | NI government orthophotos (periodic captures) | https://www.opendatani.gov.uk/ (LPS is the authoritative NI mapping body) |

No specific frame or capture date for this AOI was confirmed from any of these.

---

## 4. IMAGE-ANALYSIS ATTEMPT & LIMITATION (honest)

The task asked to run an image analysis to locate candidate disturbance. I attempted this and must report the outcome plainly:

1. **This model cannot view images.** The agent's image-reading capability returns "model does not support images" — pixels cannot be inspected by me directly.
2. **No image libraries are installed and package installation is blocked** (no `pip`, no working `apt` network). `PIL`/`numpy`/`GDAL`/ImageMagick/`ffmpeg` are all absent.
3. **The only high-resolution data (Wayback) is JPEG.** To analyse it programmatically I wrote a from-scratch baseline JPEG decoder (Huffman + IDCT, stdlib only). **Validation failed:** decoded outputs of the *same location* from different layers were essentially uncorrelated (current-vs-2024 correlation ≈ 0.02; 2014-vs-2024 ≈ −0.22), proving the decoder was producing garbled output, not a correct image. I therefore **discarded** any results from it.
4. **Decodable open PNG sources are too coarse** for the target (NASA GIBS MODIS = 250 m; Landsat WELD = 30 m). At those resolutions a buried drum (~1–2 m) is sub-pixel and invisible; only large-area change could be seen, which would not locate a drum.

**Consequence:** I did **not** produce any change-detection map, any "most-changed block" list, or any candidate burial location. Presenting such a list from an unverified decoder would be fabricating evidence, which is explicitly prohibited. **I am not sure of any candidate location and will not guess one.**

---

## 5. REPRODUCIBLE ANALYSIS PROTOCOL (for a human or image-capable tool)

The retrieved 0.6 m Wayback tiles (§2a) are the correct data to inspect. To run the before/after comparison:

1. **Load the 2014 and 2024 3×3 grids** (`wb2014_z18_*.jpg`, `wb2024_*.jpg`) into any GIS/image tool (QGIS, ArcGIS, Photoshop, or a verified JPEG decoder). They share the same tile grid, so they are pixel-co-registered.
2. **All dates are winter (Jan–Feb)** → low vegetation, good for seeing bare disturbance; compare like-for-like seasons.
3. **For each year, also pull intermediate layers** (2015–2023, all preserved/listed) to build a time-series of the AOI.
4. **What to look for** (defensible, visible differences only): newly exposed/disturbed soil, excavation or trench-like features, mounding, infill, new vehicle tracks / access changes, vegetation anomalies inconsistent with seasons, drainage alteration, shoreline/sediment change, appearance/removal of structures or dumped material.
5. **Coordinate mapping** (to cite each observed feature): tile `(x,y)` at zoom 18 →
   `lon = (x + px/256) / 262144 * 360 − 180`;
   `lat = degrees(atan(sinh(π·(1 − 2·(y + py/256)/262144))))`.
   Then convert lat/lon → Irish Grid with an OSNI tool (the approximate ING in §1 is a starting point).
6. **Cross-reference** any observed change against the (unsupplied) VR-dog indication points, GPR/magnetometry extents, and known dumping areas; record proximity in metres. Do not reinterpret those layers.
7. **Confidence** per flagged feature = limited to the underlying image quality/clarity; do **not** assign a confidence higher than the imagery supports, and do **not** infer burial or intent from any observation.

---

## 6. WHAT COULD NOT BE DETERMINED, AND WHY

| # | Gap | Why |
|---|---|---|
| 1 | **Pre-2014 high-resolution imagery of the AOI** | Free Wayback starts 2014; the 2002–2008 window is only covered by commercial air photos (§3), not retrievable here. |
| 2 | **Any pixel-level change-detection / candidate location** | Model cannot view images; no image libs; hand-rolled JPEG decoder failed validation (§4). |
| 3 | **Precise AOI polygon** | Reference photograph not supplied; only an approximate 250 m bbox provided. |
| 4 | **Ground-truth cross-reference** | No VR-dog / GPR / dumping layers supplied (§5 step 6). |
| 5 | **Per-image capture dates / resolutions for Wayback** | Source exposes layer dates (used) but not per-tile acquisition dates or exact GSD. |
| 6 | **Landsat-5 / Sentinel-2 actual pixel extracts** | Band assets are GeoTIFF/JPEG requiring GDAL/verified decoder, unavailable here. |

---

## 7. EXPLICIT NON-DETERMINATION STATEMENT

I make **no autonomous determination** regarding burial, concealment, or criminal activity. This report documents only (a) the confirmed search area, (b) the EO data retrieved/identified for it, and (c) the environment limitations that prevented pixel analysis. The actual before/after visual comparison and any candidate location must be produced by a human or image-capable system following §5; every output from that step should be separated into "confirmed from imagery" vs "inference," and no inference about human intent should be drawn.

---

*End of report. Where a specific image, date, coordinate, or result could not be verified, it is stated as absent — nothing here is fabricated.*
