# Job: Maintain the GeoLibre Planetary Atlas

Execute this pipeline autonomously. Do not ask for input.

## 1. Verify every tile source is alive

For each planet/basemap entry defined near the top of `web/index.html` (the `PLANETS` object),
`curl` the root tile and one zoomed tile and confirm `content-type: image/png` and a non-trivial
`size_download` (>1 kB for the root, may be small for zoomed edge tiles):

```bash
curl -sS -L -o /tmp/t.bin -w "%{http_code} %{content_type} %{size_download}\n" \
  "https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-moon-basemap-v0-1/all/0/0/0.png"
```

- If a source returns non-PNG / 404 → mark it dead, remove it from `PLANETS`, and note the removal
  in the run report.
- If a dead source is the only basemap for a body → remove the body from the switcher and warn.

## 2. Refresh landmark coordinates

Cross-check the Apollo / Mars-rover / major-feature coordinates against a public reference
(NASA / JPL / IAU). Planetographic longitude is ±180° east-positive, prime-meridian centred.
If anything looks mirrored when you screenshot it (see step 4), flip the longitude sign.

## 3. Regenerate the HTML

`web/index.html` is hand-authored but structured. Make targeted edits only — do not rewrite the
whole file unless a source URL changed. Keep it key-free and self-contained (CDN for MapLibre only).

## 4. Visual QA (if a headless browser is available)

Load `web/index.html` via the Playwright skill, switch to Moon then Mars, screenshot each, and
confirm the globe renders and a landmark (e.g. Apollo 11 / Olympus Mons) sits at the expected spot.
Save screenshots to `/tmp` (not the workspace).

## 5. Confirm the live route

If the `geolibre-web` container is running, `curl -I https://${APP_HOSTNAME}/geolibre/` and confirm
`200`. If the container is absent, remind the operator to run `docker compose up -d geolibre-web`.

## 6. Notify

Broadcast a one-line status to admins via the `agent-job-dm` skill (`--broadcast`), including the
live URL and any dead sources removed. Keep it terse.
