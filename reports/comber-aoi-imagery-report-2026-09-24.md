# Geospatial Imagery Evidence Report — Newtownards Road, Comber, Co. Down, BT23 5ZP

**Prepared by:** Geospatial intelligence agent (automated)
**Dates of work:** 2026-09-24 (UTC) — updated after active data retrieval pass
**AOI subject:** Shoreline/marsh parcel adjoining Strangford Lough, Comber, Co. Down, Northern Ireland
**Event of interest (context only):** Item reportedly placed in an oil drum and buried in 2005. Critical imagery window ~2002–2008, monitor to present.

> **Scope & limits.** This report identifies, retrieves, and records available EO/aerial data for the area, and confirms the search coordinate from source. It makes **no determination** about burial, concealment, or intent. Per the task rules, no image whose date/location is unconfirmed is used for analysis, and no conclusion about human activity is drawn.

---

## 0. CONFIRMED FROM SOURCE DATA vs INFERENCE / ASSESSMENT

**CONFIRMED FROM SOURCE DATA (verified this session)**
- what3words `///magnetic.deeply.orbited` → **WGS84 54.544375, −5.729841** (what3words.com server-generated `og:image` minimap `lat`/`lng`; description: "a 3 metre square location near Comber, Co. Down").
- **Real, dated, high-resolution imagery was retrieved and preserved** for this exact coordinate: Esri **Wayback** historical World Imagery, **2014-02-20 through 2024-01-18**, ~0.3–1 m (commonly ~0.6 m at z=18), 29 tiles saved to `reports/evidence/wayback/`.
- A real **2005 Landsat-5** scene over the AOI was identified on Planetary Computer: `LT05_L2SP_206022_20051119_02_T1`, **2005-11-19, 19% cloud** (30 m).
- A real **Sentinel-2** scene was identified: `S2A_MSIL2A_20190928T114351_R123_T30UUF_202010`, **2019-09-28, 14.8% cloud** (10 m).
- NASA GIBS / EOX WMS services are reachable and return dated PNG; MODIS (250 m) and Landsat WELD (30 m, 2002–2012 daily) are available but too coarse for sub-30 m features.

**INFERENCE / ASSESSMENT (not source-confirmed)**
- That the point lies on the unsupplied reference-photo shoreline parcel — coordinate is confirmed "near Comber" but the precise AOI polygon was not digitised (no photo supplied).
- Irish National Grid reference is *computed/approximate* (custom EPSG:29902 transform; validate with official OSNI converter).
- That any historical/commercial archive holds a frame centred here — coverage is plausible but specific frames/dates for OSNI/Bluesky/Getmapping 2002–2008 were **not** obtainable (commercial).

---

## 1. AOI Definition & Confirmed Coordinate

| Field | Value | Basis |
|---|---|---|
| what3words | `///magnetic.deeply.orbited` | supplied |
| **WGS84 latitude** | **54.544375° N** | what3words.com `og:image` minimap (server-generated) |
| **WGS84 longitude** | **−5.729841° E** | what3words.com `og:image` minimap |
| w3w description | "a 3 metre square location near Comber, Co. Down" | `og:description` |
| **Irish National Grid (EPSG:29902, computed/approx.)** | **J 47000 74333** (E 347000, N 374333) | custom WGS84→TM75 Helmert + OSNI TM; relative geometry validated vs Belfast/Dublin; absolute value *approximate* |
| **Search area (250 m buffer bbox, approx.)** | lat **54.542125 → 54.546625** N; lon **−5.733741 → −5.725941** E | simple ±250 m rectangle around the point (planning aid; not the true parcel) |
| Centre tile (Web Mercator z=18) | x=126899, y=83490 | derived from coordinate |

---

## 2. Source Inventory (updated with retrieval results)

| # | Source | Coverage window | Covers AOI? | Status this session | Resolution | Reference |
|---|---|---|---|---|---|---|
| 1 | **Esri Wayback (World Imagery historical)** | **2014-02-20 → 2024-01-18** (11 annual layers retrieved) | **YES** | **RETRIEVED & PRESERVED** (29 tiles, real dated imagery; ~0.3–1 m) | ~0.6 m at z=18 (service does not expose exact per-tile res) | `reports/evidence/wayback/`; tile URL template below |
| 2 | **Landsat-5 (USGS/Planetary Computer)** | Global from 1984; scene **2005-11-19** over AOI | YES | **IDENTIFIED (real 2005 dated scene)**; not downloaded as pixels here | 30 m | PC STAC `landsat-c2-l2` / `LT05_L2SP_206022_20051119_02_T1` |
| 3 | **Sentinel-2 (Planetary Computer)** | Global from 2015-06-23; scene **2019-09-28** | YES | **IDENTIFIED** (10 m, 14.8% cloud); tile fetch blocked by data-API slug mismatch | 10 m | PC STAC `sentinel-2-l2a` / `S2A_MSIL2A_20190928T114351_R123_T30UUF_202010` |
| 4 | **Landsat WELD (NASA GIBS)** | Daily 2002-04-29 → 2012-04-08 (incl. 2005); annual only 1983–2000 | YES | **IDENTIFIED** (30 m; decodable PNG) | 30 m | GIBS WMS `Landsat_WELD_*` |
| 5 | **MODIS Corrected Reflectance (NASA GIBS)** | Global, daily, dated | YES | **RETRIEVED (PNG, decodable)** but 250 m — too coarse | 250 m | GIBS WMS `MODIS_Terra_CorrectedReflectance_TrueColor` |
| 6 | **EOX s2cloudless (yearly mosaics)** | 2017 → 2025 yearly | YES | REACHABLE (JPEG, not decodable here) | ~10 m (mosaic) | `tiles.maps.eox.at/wms` |
| 7 | **OSNI / LPS orthophotography** | Periodic NI captures | YES | **NOT RETRIEVED** (commercial/ordering; CKAN API 404/500 this session) | typically 0.25 m | opendatani.gov.uk |
| 8 | **Bluesky / oldaerialphotos.com** | Historical UK/Ireland air photos (1940s–2000s) | Likely | **NOT RETRIEVED** (commercial; preview API 404) | ~0.25–1 m | oldaerialphotos.com |
| 9 | **Getmapping historical archive** | UK national surveys | Likely | **NOT RETRIEVED** (commercial) | ~0.25–0.5 m | getmapping.com |
| 10 | **UK Aerial Photos** | UK historical | Likely | **NOT RETRIEVED** (commercial) | varies | ukaerialphotos.com |
| 11 | **NCAP** | Declassified archives | Uncertain | **NOT RETRIEVED** | varies | ncap.org.uk |
| 12 | **Google Earth Pro historical** | Global incl. NI | YES | **NOT QUERIED** (desktop app; headless unusable) | 0.3–1 m | GE Pro desktop |
| 13 | **Maxar / Airbus (Pléiades/SPOT)** | High-res archive | Possibly | **NOT ACCESSIBLE** (commercial licence) | 0.3–0.5 m | maxar.com / intelligence-airbusds.com |

**Key point:** The freely/openly retrievable imagery that actually covers the critical 2002–2008 window at resolvable scale is **limited to Landsat (30 m, too coarse for a buried drum)**. The high-resolution archives that *could* show a drum-scale disturbance (OSNI, Bluesky, Getmapping, GE Pro, Maxar/Airbus) are **commercial or desktop-only** and were not obtainable in this environment. The **best open high-res evidence is Esri Wayback from 2014 onward (0.6 m)** — preserved herein.

---

## 3. Imagery Retrieved & Preserved (the concrete deliverable)

All files are saved under `reports/evidence/wayback/` (29 tiles). These are the exact data a human or image-capable tool must inspect.

**Area of every tile:** Web Mercator **z=18**, centre tile **x=126899, y=83490** (≈ the confirmed coordinate). 3×3 grids use x ∈ {126898,126899,126900}, y ∈ {83489,83490,83491}.

**Retrieval URL template (reproducible & verifiable):**
```
https://wayback.maptiles.arcgis.com/arcgis/rest/services/world_imagery/mapserver/tile/{M}/18/{y}/{x}
```
(use `curl -L`; some layers 301-redirect to a normalised tile — follow redirects)

**Layer `M` values and dates retrieved:**

| Year | Date | M | File(s) saved |
|---|---|---|---|
| 2014 | 2014-02-20 | 10 | `wb_2014_2014-02-20_c.jpg` + `wb2014_z18_{0,1,2}_{0,1,2}.jpg` (full 3×3 grid) |
| 2015 | 2015-01-21 | 20222 | `wb_2015_2015-01-21_c.jpg` |
| 2016 | 2016-01-13 | 3515 | `wb_2016_2016-01-13_c.jpg` |
| 2017 | 2017-01-11 | 577 | `wb_2017_2017-01-11_c.jpg` |
| 2018 | 2018-01-08 | 13161 | `wb_2018_2018-01-08_c.jpg` |
| 2019 | 2019-01-09 | 6036 | `wb_2019_2019-01-09_c.jpg` |
| 2020 | 2020-01-08 | 23001 | `wb_2020_2020-01-08_c.jpg` |
| 2021 | 2021-01-13 | 1049 | `wb_2021_2021-01-13_c.jpg` |
| 2022 | 2022-01-12 | 42663 | `wb_2022_2022-01-12_c.jpg` |
| 2023 | 2023-01-11 | 11475 | `wb_2023_2023-01-11_c.jpg` |
| 2024 | 2024-01-18 | 41468 | `wb_2024_2024-01-18_c.jpg` + `wb2024_{0,1,2}_{0,1,2}.jpg` (full 3×3 grid) |

All dates are **winter (Jan/Feb)** — low vegetation, which is *favourable* for seeing bare/disturbed ground when comparing years.

**Other identified dated sources (not pixel-downloaded here):**
- Landsat-5 `LT05_L2SP_206022_20051119_02_T1` — 2005-11-19, 19% cloud, 30 m (Planetary Computer, open).
- Sentinel-2 `S2A_MSIL2A_20190928T114351_R123_T30UUF_202010` — 2019-09-28, 14.8% cloud, 10 m (Planetary Computer, open).
- Landsat WELD daily (2002–2012) and MODIS (250 m) via NASA GIBS WMS — open, PNG.

---

## 4. Flagged Changes (visible defensible differences)

**NOT PERFORMED BY THIS AGENT — with explicit reasons.**

The task requires comparing confirmed, dated, georeferenced images and flagging only visible defensible differences. I **retrieved and preserved** the imagery (§3) but could **not perform the pixel-level visual comparison myself** in this environment, because:

1. **The model cannot view image attachments** — the `read` tool returns "Current model does not support images" for the retrieved JPEGs.
2. **No raster/image libraries are installed** — `PIL`/`numpy` absent; `pip` and `apt` have no network/availability to install them; no `convert`/`ffmpeg`/`djpeg`/GDAL CLI present.
3. **The high-value data is JPEG** (Wayback, ~0.6 m) — JPEG cannot be decoded with the Python standard library alone (no stdlib JPEG decoder), so even a programmatic difference computation is not possible here.
4. The only **decodable** dated sources (NASA GIBS/MODIS PNG) are **250 m** — far too coarse to resolve a buried-drum disturbance, so they cannot serve as the change-detection evidence.

Therefore **no coordinates of disturbed soil, excavation, mounding, tracks, vegetation change, or structures are reported by me**, and **no confidence levels are assigned** (assigning any would require evidence I could not examine). No statement links any observation to burial or concealment.

**What a human / image-capable tool should do next (reproducible protocol):**
1. Open the preserved 2014 and 2024 **3×3 grids** (`reports/evidence/wayback/wb2014_z18_*.jpg`, `wb2024_*.jpg`) — same geometry, ~0.6 m/pixel, both winter.
2. Visually compare the centre tile and neighbours year-over-year; also scroll the annual centre tiles (2015–2023).
3. Look specifically for: exposed/disturbed soil; trench/excavation marks; mounding; infill; new vehicle tracks/access; vegetation anomalies; drainage or shoreline change; appearance/removal of structures or dumped material.
4. If a candidate feature is found, record its **pixel offset** within the tile, convert to WGS84 using the tile's Web-Mercator geometry (tile 126899/83490 at z=18 centres on ≈54.5444, −5.7298), and assign a confidence bounded by the ~0.6 m resolution.
5. For the true 2002–2008 window, order/obtain OSNI, Bluesky, Getmapping, or GE Pro historical imagery (commercial/desktop) — the only sources fine enough to resolve a drum-scale event in that period.

---

## 5. Ranked Shortlist of Priority Locations

**NOT PRODUCED.** A ranking requires coincident evidence layers (imagery change + dog-indication proximity + absence of alternative explanation). With (a) no imagery analysis completed (§4) and (b) no ground-truth layers supplied (§6), there is no basis to rank. Producing one would require fabricating evidence, which is prohibited.

---

## 6. Ground-Truth Cross-Reference

**NOT PERFORMED — no ground-truth layers were supplied.** A workspace search found no VR-dog indication points, GPR/magnetometry extents, or known dumping-area layers. Their proximity (in metres) to any flagged location therefore **cannot be reported**. Input layers were neither altered nor reinterpreted.

---

## 7. What Could NOT Be Determined, and Why

| # | Gap | Why |
|---|---|---|
| 1 | **Pixel-level visual change detection** | Model cannot view images; no PIL/numpy/CLI; pip/apt blocked; Wayback JPEG not stdlib-decodable (see §4). |
| 2 | **High-res imagery for 2002–2008** | Only commercial/desktop sources (OSNI, Bluesky, Getmapping, GE Pro, Maxar/Airbus) reach drum-scale resolution for that window; none retrievable here. Free 2005 data is Landsat (30 m) — too coarse. |
| 3 | **Exact per-tile resolution of Wayback layers** | Esri Wayback tile service does not expose a resolution metadata field; "~0.6 m at z=18" is typical, not confirmed per tile. |
| 4 | **Precise AOI polygon** | Reference photograph not supplied; only an approximate 250 m bbox provided. |
| 5 | **Cloud/shadow/tidal state per image** | Not measured (no pixel analysis); Wayback dates are winter (low sun, leaf-off). |
| 6 | **Sentinel-2 / Landsat pixel download** | PC data-API item endpoint 404'd (collection-slug mismatch); full-scene COG download + crop needs tooling unavailable here. |
| 7 | **Authoritative Irish National Grid reference** | Computed; not confirmed against official OSNI converter (treat as approximate). |

---

## 8. Methods Actually Performed (provenance)

1. Confirmed coordinate from what3words.com `og:` metadata. 2. Network-reachability probes of all candidate sources. 3. Enumerated Esri Wayback catalog (196 dated layers) and **retrieved 29 real dated tiles (2014–2024)** for the AOI, preserved to `reports/evidence/wayback/`. 4. Located real 2005 Landsat-5 and 2019 Sentinel-2 scenes via Planetary Computer STAC. 5. Confirmed NASA GIBS/MODIS and EOX WMS reachable (dated PNG/JPEG). 6. Attempted pixel analysis; discovered the sandbox cannot view/decode images (no libs, no package install, model can't view) — reported honestly rather than fabricating findings. 7. Computed Irish Grid via custom validated transform.

---

## 9. Explicit Non-Determination Statement

I make **no autonomous determination** regarding burial, concealment, or criminal activity. This report documents the confirmed search area, the EO/aerial data that genuinely covers it (retrieved where open, identified where commercial), and the specific environment limitations that prevented me from completing the visual change-detection step. All flagged-change, ranking, and causal outputs are withheld because the underlying imagery could not be examined in this environment. The preserved 0.4 m-class Wayback tiles (2014–2024) are provided so that inspection can be completed by an image-capable tool or human.

---

*End of report. Sections §3 (retrieved data) and §4 (analysis limitation) are the substantive updates from the active retrieval pass.*
