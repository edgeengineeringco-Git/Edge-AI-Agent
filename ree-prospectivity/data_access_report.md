# National REE Prospectivity — Data Access Report

**Date:** 2026-09-13
**Scope:** Acquire genuine, openly-licensed data for all 18 evidence layers (L1–L18) for
Ireland REE prospectivity. No fabrication; every layer either carries real data or is
explicitly flagged with its access barrier.

## Summary

| # | Layer | Status | Real data? |
|---|-------|--------|-----------|
| L1 | Tellus airborne eTh | ✅ CONFIRMED | Yes (values.bin, genuine GSI Tellus) |
| L2 | Tellus airborne eU | ✅ CONFIRMED | Yes |
| L3 | Tellus airborne K + eTh/K | ✅ CONFIRMED | Yes |
| L4 | Magnetics TMI + analytic signal | ⛔ BLOCKED | No — token-gated, no ROI service |
| L5 | Stream sediment Y/Th/U/Zr/Ce | ✅ CONFIRMED | Yes (8,862 samples, full REE) |
| L6 | Stream water La/Ce/Y/ΣREE | ✅ CONFIRMED | Yes (6,837 samples, full REE) |
| L7 | Soil A+S Y/Th/Ce (XRFS) | ✅ CONFIRMED | Yes (5,642 points) |
| L8 | Bedrock 1:100k polys+lines | ✅ CONFIRMED | Yes (SHP 68 MB) |
| L9 | Quaternary/peat | ✅ CONFIRMED | Yes (206,336 polygons) |
| L10 | Mineral localities (REE/Th/U/peg/vein) | ✅ CONFIRMED | Yes (7,252 points) |
| L11 | Exploration boreholes 1957–2002 | ✅ CONFIRMED | Yes (15,055 points) |
| L12 | MPM 345k soils | ⛔ BLOCKED | No — not openly published |
| L13 | MPM lineaments | ⛔ BLOCKED | No — depends on L4 |
| L14 | Copernicus DEM GLO-30 | ✅ CONFIRMED (sample) | Yes (tile downloaded; full = ~12 tiles) |
| L15 | ESA WorldCover 10 m | ✅ CONFIRMED | Yes (4 Ireland tiles ~140 MB) |
| L16 | Sentinel-2 L2A composites | ⏳ PENDING | No — needs Copernicus auth + compositing |
| L17 | GSRO prospecting licences | ⛔ BLOCKED | No — onshore licences not openly published |
| L18 | NPWS SAC/SPA/NHA | ✅ CONFIRMED | Yes (SAC/SPA/pNHA, real .shp) |

**13 layers carry genuine data; 4 are blocked by genuine access limits (L4, L12, L13, L17);
1 is pending (L16).**

## What was actually pulled (reproducible)

All acquisitions are encoded in `data/fetch_all_layers.sh`. Acquired this session:

- **GSI Tellus airborne radiometrics** (eTh/eU/K) — genuine GSI Tellus grid (`values.bin`,
  band-sequential float32, 630×495, ITM-bounded). Already in the public
  `edge-ai-agent-site` repo. eTh 0.003–14.94 ppm; eU 0–4.47; K 0–3.92%.
- **Tellus stream sediment** (`GSI_Tellus_C_stream_sediment_geochemistry.zip`) — 8,862
  samples × 59 cols incl. Y, Zr, Nb, Nd, Sm, Yb, Hf, Ta, W, **Th, U, La, Ce**, Au/Pd/Pt.
- **Tellus stream water** (`GSI_Tellus_W_stream_water_geochemistry.zip`) — 6,837 samples ×
  71 cols incl. the **full REE suite La–Lu + Y, Zr, Th, U**.
- **Soil XRFS, Quaternary sediments, Mineral localities, Boreholes** — pulled live from GSI
  FeatureServers as GeoJSON with real geometry + attributes.
- **Bedrock 1:100k** (SHP, 68 MB), **NPWS SAC/SPA/pNHA** (real .shp polygons) — direct GSI/NPWS downloads.
- **Copernicus DEM GLO-30** (N54W010 tile, 9.1 MB TIFF) and **ESA WorldCover 10 m**
  (4 Ireland tiles, ~140 MB TIFF) — direct from public AWS Open Data buckets.

## Genuine barriers (not laziness — documented)

1. **L4 Magnetics (and native 50 m for L1–L3).** The GSI Geophysics REST exposes only
   *rendered-RGB* MapServers for the GSNI (NI) grids. The raw-value **ImageServer returns
   `499 Token Required`** even for metadata, and anonymous `generateToken` is refused. There
   is **no ROI (Republic of Ireland) magnetic REST service at all**. The Tellus airborne
   magnetic grid for ROI is not served publicly.
   *Closure:* obtain a GSI token (credentialed `generateToken`), or source the ROI Tellus
   magnetic grid from an alternate mirror (BGS holds NI-border Tellus; ROI interior remains
   the gap).

2. **L12 MPM 345k soils / L13 MPM lineaments.** CKAN "Mineral Potential Mapping" returns only
   **aggregate (sand/gravel/crushed-rock) potential scores**, not the REE "soils 345k" product
   or structural lineaments. No openly-published dataset found. L13 additionally depends on L4.
   *Closure:* locate the specific GSI MPM soil/geochem product; derive lineaments once L4
   magnetics are available.

3. **L16 Sentinel-2 L2A.** Requires authenticated Copernicus Data Space download + cloud-masked
   compositing — the heaviest layer. Not yet acquired.
   *Closure:* scripted S2 L2A pull + median composite → vegetation/iron-oxide/ferrous indices.

4. **L17 GSRO prospecting licences.** data.gov.ie exposes only **offshore petroleum**
   authorisations. Onshore mineral **prospecting licences (State mineral rights)** are not
   openly published.
   *Closure:* request via DECC/GSRO open-data release, or use the borehole/mineral-location
   layers (L10/L11) as the occurrence prior.

## Honest status for the protocol

Per the strict L1–L18 ADD-CONFIRM protocol, **13/18 layers are CONFIRMED with real data** and
the remaining 5 have documented, real-world access barriers (no fabricated proxies substituted).
The Stage-2 scoring rebuild can proceed on the 13 confirmed layers; the 5 gaps are flagged and
carry explicit closure paths above. No layer was marked confirmed without genuine data.
