# Gamma / Flight-Log Join Portal Agent

This agent time-synchronises airborne gamma spectrograms with Airdata drone flight logs and produces a joined CSV plus dual calibration metadata.

## Directory Structure

- `SYSTEM.md` — Agent identity and instructions
- `CLAUDE.md` — This file (agent-specific context)
- `jobs/process-join.md` — Immediate processing job prompt
- `scripts/join_gamma_flight.py` — Core join + calibration engine (numpy/pandas/scipy)
- `scripts/drive_utils.sh` — Google Drive OAuth helper (per-job folder create + upload)
- `scripts/upload-server.mjs` — Zero-dependency Node.js multipart upload receiver
- `web/index.html`, `web/style.css` — Branded upload form (portal + static-hostable)
- `input/` — Sample inputs / placeholder
- `skills/` — `agent-job-dm`, `agent-job-secrets` (symlinks to skills-library)

## Pipeline Flow

1. Client submits `web/index.html` form → POSTs multipart to the upload server (`/gamma-join/upload-page`).
2. Upload server saves the spectrogram (.txt, FORMAT 3) + flight log (.csv) to `data/gamma-flight-join/jobs/{job_id}/input/` and writes `webhook-payload.json`.
3. Upload server calls `create-agent-job`, scoping to `agents/gamma-flight-join`.
4. Agent reads `jobs/process-join.md`, runs `scripts/join_gamma_flight.py`.
5. Agent creates a `{job_id}` folder in the project Google Drive folder and uploads all outputs + inputs.
6. Agent broadcasts a summary via Telegram (`agent-job-dm`).

## Outputs (per job)

- `{project}_joined_gamma_flight.csv` — one row per spectrum, all channels + SI flight parameters
- `{project}_calibration.txt` — factory (Cs-check) + best-fit survey calibration
- `{project}_summary.json` — spectra/flight counts, match rate, calibration coefficients

## Dependencies

Python engine requires `numpy`, `pandas`, `scipy`. The job prompt installs them via
`pip --user --break-system-packages` (or apt) if missing.

## Deployment notes

- The upload server is optional wiring. To run it as a service, add a container to
  `docker-compose.custom.yml` (node:22-alpine, command `node /project/agents/gamma-flight-join/scripts/upload-server.mjs`, Traefik path `/gamma-join/upload-page`, port 3002) and, if desired, a TRIGGERS.json entry. Not enabled by default.
- The web form can also be published to a public/static repo (GitHub Pages); point it at the
  portal with `?endpoint=https://<host>/gamma-join/upload-page`.

## Google Drive

- Project folder: `18fSXEOVp8D039BUXWMiYrPuIeIXOxgt3` (from the user's Drive URL).
- Auth: `GOOGLE_DRIVE_OAUTH` secret via `agent-job-secrets` (auto-refreshed OAuth).

## Security

The upload endpoint uses a shared access password (`UPLOAD_PASSWORD`, default `Edge12345`).
This is a demo-grade control. For commercial use, issue per-client API keys or front the
endpoint with thepopebot's platform auth.
