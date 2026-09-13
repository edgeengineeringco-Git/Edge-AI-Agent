# Edge's Geo-Eire Agent

Scoped agent for the Ireland **ITM (EPSG:2157)** geospatial viewer.

## Repository split (intentional)

- **This repo (private `Edge-AI-Agent`)** — the agent *definition* only:
  - `SYSTEM.md` — agent system prompt (ITM CRS standard, data sources, reporting rules)
  - `CLAUDE.md` — this file
- **Public repo (`edge-ai-agent-site`)** — the *live viewer* and its assets:
  - `ireland-geology-map.html` — published viewer (satellite + GSI 100K bedrock + Tellus radiometrics)
  - `data/geology-100k.geojson` — GSI 100K bedrock polygons (WGS84 lon/lat)
  - `data/radiometrics/` — airborne γ rasters (dose, eU, eTh, K) + meta/values

The viewer is served from GitHub Pages on `edge-ai-agent-site`; this folder only defines the agent.
Do **not** keep a copy of `ireland-geology-map.html` or its data in this repo — they live in `edge-ai-agent-site`.

## Constraints

- CRS requirement: EPSG:2157 ITM end-to-end for map display. (⚠️ Open item: the live `ireland-geology-map.html`
  currently renders in Leaflet Web-Mercator/WGS84, not ITM — re-projection is a pending edit.)
- Do not mix this agent's viewer work into `terrestrial-dose` or `edge-kuth-portal`.
- Do not modify terrestrial-dose physics.
