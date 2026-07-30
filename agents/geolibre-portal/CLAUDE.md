# GeoLibre Planetary Atlas Agent

Agent that renders and serves an interactive **MapLibre GL JS** globe of the **Moon and Mars**
(plus bonus worlds) — mirroring GeoLibre's planetary mapping, natively in thepopebot.

## What it does

- Curates a single self-contained `web/index.html` that visualizes the Moon & Mars (and Mercury,
  Venus, Io, Europa, Ganymede, Callisto, Titan) via real OpenPlanetaryMap + USGS tile services.
- Planet switcher, multiple basemap styles per body, globe ↔ mercator projection toggle,
  graticule, notable-locations (Apollo sites, Mars rover sites, Olympus Mons, Valles Marineris…),
  coordinate readout, auto-rotate, mobile responsive.
- Loads MapLibre GL JS + CSS from a CDN and tiles from public servers — **no backend, no API keys**.

## Layout

```
agents/geolibre-portal/
├── SYSTEM.md
├── CLAUDE.md
├── jobs/
│   └── maintain-atlas.md
└── web/
    ├── index.html     ← the atlas (single file, self-contained)
    └── README.md      ← deploy + access instructions
```

## Access

| Method | How |
|---|---|
| **Live URL** (recommended) | `https://${APP_HOSTNAME}/geolibre/` — served by the `geolibre-web` nginx container in `docker-compose.custom.yml`. Run `docker compose up -d geolibre-web`. |
| **Direct file** | Open `agents/geolibre-portal/web/index.html` in any browser (or serve the folder). |

## Verified tile sources

Moon: `opm-moon-basemap-v0-1` (CARTO, xyz) + `moon-hillshaded-albedo` (tms).
Mars: `opm-mars-basemap-v0-2` (CARTO, xyz) + MOLA/Viking variants (tms).
Bonus worlds: `tiles.geolibre.app/wms/<body>-<style>` (xyz).
Reference: OpenStreetMap + CARTO for Earth.
Full provenance + radii in `SYSTEM.md`. **Always `curl`-verify a tile is `image/png` before trusting it.**

## Triggering

Manual/chat ("open the atlas", "verify Mars tiles") or the `maintain-atlas.md` job. Cron
`geolibre-refresh-atlas` exists but is **disabled** — enable for weekly tile-health checks.

## Related agents

- **edge-kuth-portal** — K/U/Th gamma spectra; complementary field instrument for the same
  critical-minerals programme.
- **geosync-expert** — geochemical survey processing; this atlas can display geosync anomalies
  as an overlay if given GeoJSON.
