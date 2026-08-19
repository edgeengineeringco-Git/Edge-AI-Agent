# Gamma / Flight-Log Join Portal Agent

This agent time-synchronises airborne gamma spectrograms with Airdata drone flight logs and produces a joined CSV plus dual calibration metadata.

**Architecture: fully serverless — NO Docker, NO server. Input files NEVER touch Drive.** The public form posts to a Google Apps Script Web App, which sends file data as base64 inline in the webhook payload to trigger this agent for **immediate processing**. Only processed output files land in Google Drive.

## Directory Structure

- `SYSTEM.md` — Agent identity and instructions
- `CLAUDE.md` — This file (agent-specific context)
- `jobs/process-join.md` — Immediate processing job prompt (webhook-triggered)
- `scripts/join_gamma_flight.py` — Core join + calibration engine (numpy/pandas/scipy)
- `scripts/drive_utils.sh` — Google Drive OAuth helper (create folder / upload outputs)
- `web/gas-backend.js` — Google Apps Script Web App backend (v3 — inline base64, no Drive)
- `web/index.html`, `web/style.css` — Branded upload form (GitHub Pages)
- `input/` — Optional local drop zone for manual CLI runs
- `skills/` — `agent-job-dm`, `agent-job-secrets` (symlinks to skills-library)

## Pipeline Flow (immediate, serverless, no Drive for inputs)

1. Client fills `web/index.html` (hosted on GitHub Pages) and selects the two files.
2. The page encodes both files as base64 and POSTs a JSON payload to the Google Apps Script Web App (`web/gas-backend.js`).
3. The Apps Script backend:
   - Checks the access password
   - Sends file data as **base64 inline in the webhook payload** to thepopebot (`/gamma-join/upload`)
   - **No files are saved to Drive**
4. This agent fires **immediately** via the webhook trigger:
   - Decodes the base64 files from the payload to `/tmp`
   - Runs `join_gamma_flight.py`
   - Creates a new `{job_id}/` folder in the main Drive folder
   - Uploads **ONLY** the output files (joined CSV, calibration.txt, summary.json)
   - Cleans up `/tmp`
5. Agent broadcasts a summary via Telegram (`agent-job-dm`).

## Why this architecture

- **No Docker, no server** — everything runs on Google's infrastructure (Apps Script + Drive) plus this agent.
- **Immediate processing** — webhook trigger fires the agent instantly on form submission.
- **Clean Drive** — only processed outputs exist in Drive. Input files NEVER touch Drive — they arrive inline and are decoded to `/tmp`.

## Webhook Trigger

Added to `event-handler/TRIGGERS.json`:
```json
{
  "name": "gamma-join-upload",
  "watch_path": "/gamma-join/upload",
  "actions": [{ "type": "agent", "job": "...", "scope": "agents/gamma-flight-join" }],
  "enabled": true
}
```

The webhook payload includes `spectrogram_b64` and `flightlog_b64` (base64-encoded file data) plus metadata. The GAS backend must be configured with `WEBHOOK_URL` set to the thepopebot server's public URL + `/gamma-join/upload`.

## Outputs (per job, in Drive)

- `{project}_joined_gamma_flight.csv` — one row per spectrum, all channels + SI flight parameters
- `{project}_calibration.txt` — factory (Cs-check) + best-fit survey calibration
- `{project}_summary.json` — spectra/flight counts, match rate, calibration coefficients

## Deploying the backend (one-time)

1. Open https://script.google.com → New project, paste `web/gas-backend.js`.
2. Set `WEBHOOK_URL` in the config to your thepopebot server URL (e.g. `https://bot.example.com/gamma-join/upload`).
3. Deploy → New deployment → Web app (Execute as: Me, Access: Anyone). Authorize Drive access.
4. Copy the `/exec` URL into `DEFAULT_ENDPOINT` in `web/index.html` (or pass `?endpoint=`).
5. Publish `web/index.html` + `web/style.css` to the public Pages repo `edge-ai-agent-site` under `gamma-flight-join/`.

## Dependencies

Python engine requires `numpy`, `pandas`, `scipy` (installed by the job prompt via
`pip --user --break-system-packages` if missing).

## Google Drive

- Main project folder: `18fSXEOVp8D039BUXWMiYrPuIeIXOxgt3`
- Output folders: `{job_id}/` in the main folder, containing only outputs
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
