# Gamma / Flight-Log Join Portal Agent

Time-synchronises airborne gamma spectrograms with Airdata drone flight logs.

**Input files stay on disk — NEVER in Drive. Only processed outputs go to Drive.**

## Flow

1. Form (`web/index.html`, GitHub Pages) → POST to upload server
2. Upload server saves files to disk, triggers agent via `create-agent-job`
3. Agent processes from disk, uploads ONLY outputs to Drive
4. Telegram notification with results

## Files

- `SYSTEM.md` — Agent identity
- `CLAUDE.md` — This file
- `jobs/process-join.md` — Processing job prompt (reads from disk, uploads outputs to Drive)
- `scripts/join_gamma_flight.py` — Core join + calibration engine
- `scripts/drive_utils.sh` — Drive helper (create-folder, upload only)
- `web/index.html`, `web/style.css` — Upload form (GitHub Pages)
- `web/gas-backend.js` — Legacy GAS backend (no longer used for new flow)

## Upload server route

Added to `edge-kuth-portal/upload-server.mjs`:
- `POST /api/gamma-join/upload` — receives multipart form, saves to disk, triggers agent

Traefik route in `docker-compose.custom.yml`:
- `PathPrefix(/api/gamma-join)` → upload server

## Drive layout

- Project folder: `18fSXEOVp8D039BUXWMiYrPuIeIXOxgt3`
- Each job gets a subfolder `{job_id}/` containing ONLY outputs:
  - `{project}_joined_gamma_flight.csv`
  - `{project}_calibration.txt`
  - `{project}_summary.json`

## Security

Form password: `Edge12345` (checked by upload server).
