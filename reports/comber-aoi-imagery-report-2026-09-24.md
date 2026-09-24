# Geospatial Imagery Evidence Report — Newtownards Road, Comber, Co. Down, BT23 5ZP

**Prepared by:** Geospatial intelligence agent (automated)
**Date of report:** 2026-09-24 (UTC)
**AOI subject:** Shoreline/marsh parcel adjoining Strangford Lough, Comber, Co. Down, Northern Ireland
**Event of interest (context only):** Item reportedly placed in an oil drum and buried in 2005. Critical imagery window ~2002–2008, with monitoring through present.

> **Scope & limits of this report.** This report only *identifies and records what imagery evidence could and could not be obtained*, and confirms the search coordinate from source. It performs **no determination** about burial, concealment, or any human intent. No change detection was possible because no confirmed, dated, georeferenced image was successfully retrieved for this AOI (see §4 and §6). Every claim below is separated into **CONFIRMED FROM SOURCE DATA** vs **INFERENCE / ASSESSMENT**.

---

## 0. CONFIRMED FROM SOURCE DATA vs INFERENCE / ASSESSMENT (summary)

**CONFIRMED FROM SOURCE DATA**
- The what3words location `///magnetic.deeply.orbited` resolves (per what3words.com's own server-rendered metadata) to **WGS84 54.544375, −5.729841**, described by what3words as "a 3 metre square location near Comber, Co. Down."
- Current web-basemap imagery (Esri World Imagery / ArcGIS Online) **does cover** this coordinate — a valid 256×256 px tile was retrieved (saved as `reports/evidence/comber_current_basemap_z18_evidence.jpg`). The source **does not expose a capture date** for that tile.
- Copernicus Data Space / OData API and the OpenDataNI portal are network-reachable; Google Earth (kh.google.com) and SciHub (scihub.copernicus.eu) were **not** reachable/usable in this environment.
- No reference photograph and no ground-truth layers (VR-dog indication points, GPR/magnetometry extents, known dumping areas) were present in the supplied workspace.

**INFERENCE / ASSESSMENT (not source-confirmed)**
- That the resolved coordinate sits on the Strangford Lough shoreline/marsh parcel outlined in the *unsupplied* reference photo. The coordinate is confirmed "near Comber, Co. Down" but the precise AOI polygon cannot be delineated here because the reference photograph was not provided.
- The Irish National Grid reference is *computed* (approximate) and should be re-checked with an authoritative OSNI grid converter before operational use.
- That any historical or commercial archive actually contains a frame centred on this AOI. Coverage is *plausible* for several sources (general knowledge) but **no specific frame or date was confirmed**.

---

## 1. AOI Definition & Confirmed Coordinate

| Field | Value | Basis |
|---|---|---|
| what3words | `///magnetic.deeply.orbited` | As supplied in task |
| **WGS84 latitude** | **54.544375° N** | what3words.com Open Graph `og:image` minimap URL parameter `lat=54.544375` (server-generated from the words) |
| **WGS84 longitude** | **−5.729841° E** | what3words.com Open Graph `og:image` minimap URL parameter `lng=-5.729841` |
| what3words description | "a 3 metre square location near Comber, Co. Down" | `og:description` meta tag on what3words.com page for the words |
| **Irish National Grid (EPSG:29902, computed/approx.)** | **J 47000 74333**  (E 347000 m, N 374333 m) | Custom forward transform (WGS84→TM75 Helmert + OSNI Transverse Mercator). *Relative geometry validated against Belfast City Hall and Dublin; absolute value to be confirmed with official OSNI converter.* |
| Irish Transverse Mercator (EPSG:2157) | Not computed (pyproj unavailable) | — |

**Context buffer (search extent).** The task requires extending the search 100–250 m beyond the AOI boundary. Because the reference photograph was not supplied, a precise AOI polygon could not be digitised. As a planning aid, an **approximate 250 m bounding box** around the confirmed point is:

- Latitude: **54.542125° to 54.546625° N**
- Longitude: **−5.733741° to −5.725941° E**

(This is a simple ±250 m rectangle around the point, not the true shoreline parcel; it is a search guide only.)

---

## 2. Source Inventory

**How to read this table.** No *specific dated image* for this AOI was retrieved in this session. Therefore every row is a **source/feasibility** entry, not a confirmed image. The "Specific scene retrieved & dated?" column is **NO (UNVERIFIED)** for all rows except the two current-basemap sources, whose *coverage* is confirmed but whose *dates are unknown*.

| # | Source | Type / region | Known coverage window (general program knowledge — NOT a confirmed scene for this AOI) | Plausibly covers this AOI? | Specific scene for this AOI retrieved & dated? | Resolution (confirmed?) | Direct reference / ordering page | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | **OSNI / Land & Property Services orthophotography** | NI government orthophoto | Periodic national orthophoto captures of Northern Ireland (program exists; specific survey years NOT confirmed in this session) | Yes (LPS is the authoritative NI mapping body) | **NO — UNVERIFIED** | Not confirmed for this AOI | https://www.opendatani.gov.uk/ (CKAN API returned 404/500 in session; OSNI/LPS is the authoritative source) | Source exists; specific frame/date NOT retrieved |
| 2 | **Bluesky / OSNI historical aerial archive (oldaerialphotos.com)** | Commercial historical air photos (UK & Ireland) | Historical coverage from mid-20th century through 2000s (program-general; specific frame/date NOT confirmed) | Yes (UK/NI coverage offered) | **NO — UNVERIFIED** | Not confirmed | https://www.oldaerialphotos.com/ (page reachable, 302/301; ordering required) | Coverage plausible; no frame confirmed |
| 3 | **Getmapping historical archive** | Commercial national aerial archive | UK national surveys (first seamless UK mosaic late-1990s/2000; later surveys) — specific years NOT confirmed | Yes (national UK coverage incl. NI) | **NO — UNVERIFIED** | Not confirmed | https://www.getmapping.com/our-data/historical-aerial-archive (301) | Coverage plausible; no frame confirmed |
| 4 | **UK Aerial Photos (ukaerialphotos.com)** | Commercial historical air photos | UK-wide historical photos (program-general; specific frame/date NOT confirmed) | Yes (UK coverage) | **NO — UNVERIFIED** | Not confirmed | https://www.ukaerialphotos.com/ (200) | Coverage plausible; no frame confirmed |
| 5 | **NCAP (National Collection of Aerial Photography)** | Declassified military/survey archives (APRT, JARIC, etc.) | Varies by collection; NI coverage uncertain | Uncertain | **NO — UNVERIFIED** | Not confirmed | https://www.ncap.org.uk/ (301) | Coverage for this AOI uncertain; not confirmed |
| 6 | **Google Earth Pro — historical imagery** | Desktop EO client (global) | Global, incl. NI; multiple historical layers (dates vary by location) | Yes | **NOT QUERIED** — requires desktop app; headless environment unusable (kh.google.com → 404) | Not applicable | Google Earth Pro desktop client | Source exists; **not queried in this session** |
| 7 | **Bing Maps aerial tiles** | Global web basemap | Global current imagery (mosaic of varying dates) | Yes | **COVERAGE CONFIRMED, DATE UNKNOWN** — tile fetched, date not exposed | Not exposed | Bing Maps (tile service) | Undated; excluded from change detection |
| 8 | **Esri World Imagery (ArcGIS Online)** | Global web basemap | Global current imagery (mosaic of varying dates) | Yes | **COVERAGE CONFIRMED, DATE UNKNOWN** — valid 256×256 px tile retrieved & saved (`reports/evidence/comber_current_basemap_z18_evidence.jpg`); date not exposed | Not exposed (typical 0.3–1 m but NOT confirmed for this tile) | https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer | Undated; excluded from change detection |
| 9 | **Sentinel-2 (Copernicus)** | Optical satellite, global | Global from **2015-06-23** (program-general fact) | Yes | **NO — UNVERIFIED** (OData reachable 200 but product download requires OAuth; not authenticated) | Program-typical 10/20/60 m, NOT confirmed for a specific scene here | https://dataspace.copernicus.eu/ | Source reachable; no scene retrieved/dated |
| 10 | **Landsat (USGS EarthExplorer)** | Optical satellite, global | Global from **1984** (program-general fact) | Yes | **NO — UNVERIFIED** (EarthExplorer reachable 200 but requires account to download) | Program-typical 15–30 m, NOT confirmed for a specific scene here | https://earthexplorer.usgs.gov/ | Source reachable; no scene retrieved/dated |
| 11 | **PlanetScope / RapidEye (Planet)** | Commercial satellite | RapidEye 2009–2011 (archive to 2020); PlanetScope from 2016 (program-general) | Possibly | **NO — UNVERIFIED** (commercial account required; not accessible) | Not confirmed | https://www.planet.com/ | Not accessible |
| 12 | **Maxar (WorldView / GeoEye / IKONOS)** | Commercial high-res satellite | Archive from late 1990s (program-general) | Possibly | **NO — UNVERIFIED** (commercial licence required; not accessible) | Not confirmed | https://www.maxar.com/ | Not accessible |
| 13 | **Airbus (SPOT / Pléiades)** | Commercial high-res satellite | SPOT from 1986, Pléiades from 2012 (program-general) | Possibly | **NO — UNVERIFIED** (commercial licence required; not accessible) | Not confirmed | https://www.intelligence-airbusds.com/ | Not accessible |

**Key conclusion from the inventory:** Of the 13 candidate sources, **none** yielded a confirmed, dated, georeferenced image for this AOI in this session. Two current-basemap sources confirm *coverage exists* but expose no dates. The historical archives most relevant to the 2002–2008 window (OSNI, Bluesky, Getmapping, UK Aerial Photos, NCAP) are commercial/ordering services or require desktop/account tools that were not usable here.

---

## 3. Flagged Changes (visible defensible differences between image dates)

**NONE — change detection was not performed.**

Reason (per the task's own rule): *"Do not proceed to comparison or analysis using any image whose date or location coverage is unconfirmed."* No image in this session met the bar of **confirmed, georeferenced, and dated**. Therefore:

- No coordinates of disturbed soil, excavation, mounding, infill, vehicle tracks, vegetation change, drainage alteration, shoreline change, or dumped-material appearance/removal are reported.
- No confidence levels are assigned, because assigning any would require image evidence that was not obtained.
- No statement is made linking any observation to burial, digging, or concealment. This report makes **no such determination**.

If/when dated, georeferenced images are obtained (e.g., via OSNI ordering, Google Earth Pro, or an authenticated Copernicus/Sentinel-2 pull), the comparison step (earliest → ~2005 → most-recent) can be executed and this section populated.

---

## 4. Ranked Shortlist of Priority Locations

**NOT PRODUCED.**

A ranked shortlist must be derived from the *number and clarity of independent evidence layers that coincide at each location* (imagery change + proximity to dog indication + absence of alternative explanation). Because:
- zero imagery-change evidence layers exist (§3), and
- no ground-truth layers were supplied (VR-dog points, GPR/magnetometry extents, known dumping areas — see §5),

there is **no basis** on which to rank candidate locations. Producing a ranked list now would require fabricating evidence, which is prohibited. This section is intentionally empty.

---

## 5. Ground-Truth Cross-Reference

**NOT PERFORMED — no ground-truth layers were supplied.**

The task specifies cross-referencing flagged locations against:
- VR-dog indication points,
- prior GPR / magnetometry survey extents,
- known dumping areas.

A search of the workspace found **none** of these layers (no GeoJSON/KML/Shapefile, no dog/GPR/dumping inputs; the only imagery present was unrelated `edge-smart-video` output). Per the instruction *"Do not alter or reinterpret those input layers"* and *"If data does not exist or cannot be retrieved, state that plainly"*, I record that no such layers were available to cross-reference, and their proximity (in metres) to any flagged location therefore **cannot be reported**.

---

## 6. What Could NOT Be Determined, and Why

| # | Gap | Why it could not be determined |
|---|---|---|
| 1 | **Any imagery for the critical 2002–2008 window** | Historical archives (OSNI, Bluesky/oldaerialphotos, Getmapping, UK Aerial Photos, NCAP) are commercial/ordering services or require desktop/account tools not usable in this headless sandbox. No frame or date was retrieved or confirmed. |
| 2 | **Specific capture dates for any source at this AOI** | No image was downloaded; dates could not be read from metadata. Where coverage was confirmed (Esri/Bing), the source does not expose per-tile dates. |
| 3 | **Resolution, cloud/shadow cover, and tidal state per image** | No image pixels were obtained; these attributes cannot be measured. |
| 4 | **Change detection / flagged differences** | Requires ≥2 confirmed, dated, georeferenced, analysable images. None were obtained. |
| 5 | **Precise AOI polygon (shoreline/marsh parcel)** | The reference photograph was not supplied in the workspace, so the parcel could not be digitised. Only an approximate 250 m bounding box around the point is provided. |
| 6 | **Ground-truth proximity (dog / GPR / dumping)** | No such layers were supplied (see §5). |
| 7 | **Sentinel-2 / Landsat scene retrieval** | Copernicus Data Space and USGS EarthExplorer require authentication/account for product download; not performed in this session. OData root returned 200 but product queries need a Bearer token. |
| 8 | **Google Earth Pro historical imagery** | Requires the desktop client; `kh.google.com` returned 404 and no headless GE interface is available. Not queried. |
| 9 | **Authoritative Irish National Grid reference** | Computed via a custom transform (validated for relative geometry) but not confirmed against an official OSNI grid converter; treat as approximate. |
| 10 | **OpenDataNI CKAN API access** | The standard CKAN API paths (`/api/3/action/package_search`, `/api/action/package_search`) returned 404/500 in this session; the portal may use a different backend. OSNI/LPS remains the authoritative NI source but specific datasets were not enumerated here. |

---

## 7. Methods Attempted & Provenance (for reviewer transparency)

What was actually done in this session (so a human can distinguish confirmed actions from assumptions):

1. **Workspace inventory** — searched for any supplied reference photograph or ground-truth layers. None found.
2. **Coordinate confirmation** — fetched `https://what3words.com/magnetic.deeply.orbited`; extracted the server-rendered Open Graph `og:image` minimap URL (`…minimap?lat=54.544375&lng=-5.729841…`) and `og:description` ("a 3 metre square location near Comber, Co. Down"). This is generated by what3words from the words, so it is treated as **source-confirmed**, not estimated.
3. **Irish Grid conversion** — implemented EPSG:29902 forward transform (WGS84→TM75 Helmert + OSNI Transverse Mercator) in pure Python (no pyproj/numpy available). Validated relative geometry against Belfast City Hall (plots ~12.8 km W and ~4.5 km N of Comber — matches geography) and Dublin (easting within 11 m of expected). Absolute value flagged approximate.
4. **Network reachability probes** — what3words.com (307/200), api.what3words.com (401, needs key — no key present in environment), oldaerialphotos.com (302, TLS name mismatch noted), OpenDataNI (404/500), Copernicus Data Space (200), Sentinel-Hub (503), SciHub (unreachable), USGS EarthExplorer (200), Esri/ArcGIS (tile 200), Google Earth (404), Getmapping/Bluesky/NCAP (301), UK Aerial Photos (200).
5. **Current-imagery evidence retrieval** — fetched one Esri World Imagery tile at z=18 for the coordinate; verified it is a valid 256×256 JPEG; saved to `reports/evidence/comber_current_basemap_z18_evidence.jpg`. Date NOT exposed by source → recorded as undated.
6. **No fabrication** — no coordinates of disturbance, no dates, no resolutions, and no change findings were invented. Where data is absent, it is stated as absent.

---

## 8. Explicit Non-Determination Statement

In accordance with the task rules, I make **no autonomous determination** regarding burial, concealment, or criminal activity. This report documents only (a) the confirmed search coordinate, (b) which imagery sources plausibly/explicitly cover the AOI and whether any specific dated image was obtained, and (c) the gaps that prevented analysis. All flagged-change, ranking, and causal-inference outputs are explicitly withheld because the underlying evidence was not obtainable in this environment.

---

*End of report. Any section marked UNVERIFIED or NOT PERFORMED reflects a genuine gap, not a completed search.*
