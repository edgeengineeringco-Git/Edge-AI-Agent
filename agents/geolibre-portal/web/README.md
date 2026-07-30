# GeoLibre Planetary Atlas — Web

A single, self-contained `index.html` that renders interactive **MapLibre GL JS** globes of the
Moon, Mars and more, using real open tile services. **No backend, no API keys, no build step.**

## Open it

| How | Steps |
|---|---|
| **Directly** | Open `index.html` in any modern browser (it loads MapLibre from a CDN and tiles from public servers — only needs internet). |
| **Local host** | `cd web && python3 -m http.server 8123` → http://localhost:8123/ |
| **Live URL (thepopebot)** | Served by the `geolibre-web` nginx container at `https://<your-app-host>/geolibre/`. See deploy below. |

## Deploy the live route

The `geolibre-web` service is defined in `docker-compose.custom.yml` (a Traefik-routed nginx
container mounting this folder). It is **not** running by default.

```bash
# from the repo root (vars APP_HOSTNAME / SSL_DOMAIN come from .env)
docker compose up -d geolibre-web
```

Then visit **`https://${APP_HOSTNAME}/geolibre/`**.

Traefik strips the `/geolibre` prefix, so nginx serves `index.html` at `/`. The page is fully
self-contained (MapLibre from CDN, all tiles via absolute public URLs), so it works identically
whether served at `/geolibre/`, at the root of any static host, or opened from `file://`.

## Tile sources (verified 2026-07-30)

| Body | Basemap | URL | Scheme | maxZoom |
|---|---|---|---|---|
| Moon | OpenPlanetary Basemap | `https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-moon-basemap-v0-1/all/{z}/{x}/{y}.png` | xyz | 6 |
| Moon | LOLA Hillshaded Albedo | `https://tiles.geolibre.app/opm/moon-hillshaded-albedo/{z}/{x}/{y}.png` | tms | 6 |
| Mars | OpenPlanetary Basemap | `…/opm-mars-basemap-v0-2/all/{z}/{x}/{y}.png` | xyz | 6 |
| Mars | MOLA variants + Viking MDIM2.1 | `https://tiles.geolibre.app/opm/mars-*` | tms | 6–9 |
| Mercury/Venus/Io/Europa/Ganymede/Callisto/Titan | USGS mosaics | `https://tiles.geolibre.app/wms/<body>-<style>/{z}/{x}/{y}.png` | xyz | 6–7 |
| Earth | OpenStreetMap / CARTO | public raster tiles | xyz | 19 |

Full provenance, attributions and planetary radii: see `../SYSTEM.md`.

## Verify tiles are still alive

```bash
curl -sS -L -o /dev/null -w "%{http_code} %{content_type}\n" \
  "https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-moon-basemap-v0-1/all/0/0/0.png"
# expect: 200 image/png
```

## Regenerating

`index.html` is hand-authored but structured. Make targeted edits; keep it key-free and
self-contained (CDN for MapLibre only). Run the `jobs/maintain-atlas.md` checklist for a full
verify-and-refresh pass.
