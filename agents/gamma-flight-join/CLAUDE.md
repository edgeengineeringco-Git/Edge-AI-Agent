# Gamma / Flight-Log Join Portal Agent

Time-synchronises airborne gamma spectrograms with Airdata drone flight logs. Produces a joined CSV plus dual calibration metadata.

**Architecture: Form → upload server (disk) → agent → Drive (outputs only).**

Input files are saved to disk by the upload server. They NEVER touch Google Drive. Only processed output files are uploaded to Drive.

## Directory Structure

- `SYSTEM.md` — Agent identity and instructions
- `CLAUDE.md` — This file
- `jobs/process-join.md` — Processing job prompt
- `scripts/join_gamma_flight.py` — Core join + calibration engine
- `scripts/drive_utils.sh` — Google Drive helper (upload outputs only)
- `web/index.html`, `web/style.css` — Branded upload form (GitHub Pages)
- `web/gas-backend.js` — Legacy GAS backend (no longer used for main flow)
- `skills/` — `agent-job-dm`, `agent-job-secrets`

## Pipeline Flow

1. Client fills form at GitHub Pages URL, selects spectrogram + flight log
2. Form POSTs multipart to upload server (`https://pbot.edgeengineers.net/api/gamma-join/upload`)
3. Upload server saves input files to disk (`edge-kuth-portal/jobs/{job_id}/input/`)
4. Upload server triggers agent via `create-agent-job` API
5. Agent reads files from disk, runs `join_gamma_flight.py`
6. Agent uploads ONLY outputs to a new Google Drive folder
7. Agent broadcasts summary via Telegram

**Inputs are NEVER in Drive.** Only outputs (joined CSV, calibration.txt, summary.json).

## Deploy

1. Merge PR (activates upload server route + Traefik config)
2. Upload server restarts with new route `/api/gamma-join/upload`
3. Form at GitHub Pages posts directly to upload server — no GAS needed

## Dependencies

Python: `numpy`, `pandas`, `scipy` (auto-installed if missing).
