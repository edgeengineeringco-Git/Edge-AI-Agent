# Gamma / Flight-Log Join Portal Agent

This agent time-synchronises airborne gamma spectrograms with Airdata drone flight logs and produces a joined CSV plus dual calibration metadata.

**Architecture: fully serverless — NO Docker, NO server.** The public form posts to a Google Apps Script Web App, which stores each job in Google Drive. This agent scans Drive for pending jobs and processes them.

## Directory Structure

- `SYSTEM.md` — Agent identity and instructions
- `CLAUDE.md` — This file (agent-specific context)
- `jobs/process-join.md` — Drive-scan processing job prompt
- `scripts/join_gamma_flight.py` — Core join + calibration engine (numpy/pandas/scipy)
- `scripts/drive_utils.sh` — Google Drive OAuth helper (list-jobs / download / create-folder / upload)
- `web/gas-backend.js` — Google Apps Script Web App backend (serverless receiver)
- `web/index.html`, `web/style.css` — Branded upload form (GitHub Pages)
- `input/` — Optional local drop zone for manual CLI runs
- `skills/` — `agent-job-dm`, `agent-job-secrets` (symlinks to skills-library)

## Pipeline Flow (serverless)

1. Client fills `web/index.html` (hosted on GitHub Pages) and selects the two files.
2. The page encodes both files as base64 and POSTs a JSON payload to the Google Apps Script Web App (`web/gas-backend.js`).
3. The Apps Script backend checks the access password, creates a per-job subfolder named `{job_id}` in the project Drive folder, saves the spectrogram + flight log + `job-manifest.json` (status `pending`), and notifies Telegram.
4. This agent (cron `gamma-flight-join-batch`, or manual) runs `drive_utils.sh list-jobs`, downloads each pending job to `/tmp`, runs `join_gamma_flight.py`, and uploads the outputs back into the same Drive folder.
5. Agent broadcasts a summary via Telegram (`agent-job-dm`).

## Why serverless

The user's constraint: do not add or change anything in Docker. So there is no
`upload-server.mjs` and no `docker-compose.custom.yml` service. Everything runs on
Google's infrastructure (Apps Script + Drive) plus this scheduled agent. `docker-compose.custom.yml` is left exactly as it was.

## Outputs (per job, written into the job's Drive folder)

After processing, **only output files remain** in the Drive job folder. Input files (spectrogram, flight log) and the manifest are deleted after successful processing.

- `{project}_joined_gamma_flight.csv` — one row per spectrum, all channels + SI flight parameters
- `{project}_calibration.txt` — factory (Cs-check) + best-fit survey calibration
- `{project}_summary.json` — spectra/flight counts, match rate, calibration coefficients

## Deploying the backend (one-time)

1. Open https://script.google.com → New project, paste `web/gas-backend.js`.
2. Deploy → New deployment → Web app (Execute as: Me, Access: Anyone). Authorize Drive access.
3. Copy the `/exec` URL into `DEFAULT_ENDPOINT` in `web/index.html` (or pass `?endpoint=`).
4. Publish `web/index.html` + `web/style.css` to the public Pages repo `edge-ai-agent-site` under `gamma-flight-join/`.

## Dependencies

Python engine requires `numpy`, `pandas`, `scipy` (installed by the job prompt via
`pip --user --break-system-packages` if missing).

## Google Drive

- Project folder: `18fSXEOVp8D039BUXWMiYrPuIeIXOxgt3` (one subfolder per job).
- Agent auth: `GOOGLE_DRIVE_OAUTH` secret via `agent-job-secrets`.
- Backend auth: the Apps Script runs under its deploying Google account (independent of the secret).

## Time-match tolerance

Default is **1 s** (suits typical 1–10 Hz Airdata logs, ≈1–5 m position error). It is
adjustable per job via the form field / `--time-tolerance`. It cannot be 0 (the two device
clocks never align to the exact millisecond). A near-zero match rate signals a possible
timezone/clock offset — flag it, don't trust the result.

## Security

The form uses a shared access password (`ACCESS_PASSWORD` in `gas-backend.js`, default
`Edge12345`). Demo-grade. For commercial use, issue per-client keys or restrict the
Apps Script deployment access.
