# Gamma / Flight-Log Join Portal Agent

This agent time-synchronises airborne gamma spectrograms with Airdata drone flight logs and produces a joined CSV plus dual calibration metadata.

**Architecture:** The public form posts to a Google Apps Script Web App (GAS), which saves inputs to a temporary `_pending` folder in Drive and calls `/api/create-agent-job` to trigger this agent. The agent downloads inputs, processes them, uploads ONLY outputs to a new job folder, verifies outputs exist, then deletes `_pending`.

## Directory Structure

- `SYSTEM.md` — Agent identity and instructions
- `CLAUDE.md` — This file (agent-specific context)
- `jobs/process-join.md` — Processing job prompt (API-triggered)
- `scripts/join_gamma_flight.py` — Core join + calibration engine (numpy/pandas/scipy)
- `scripts/drive_utils.sh` — Google Drive OAuth helper (create folder / upload / download / list / delete)
- `web/gas-backend.js` — Google Apps Script Web App backend (v4 — saves to _pending, calls API)
- `web/index.html`, `web/style.css` — Branded upload form (GitHub Pages)
- `input/` — Optional local drop zone for manual CLI runs
- `skills/` — `agent-job-dm`, `agent-job-secrets` (symlinks to skills-library)

## Pipeline Flow

1. Client fills `web/index.html` (hosted on GitHub Pages) and selects the two files.
2. The page encodes both files as base64 and POSTs a JSON payload to the GAS backend.
3. The GAS backend:
   - Checks the access password
   - Saves input files to `_pending/{job_id}/` in Drive
   - Shares the temp folder with the agent's Drive account (`edgeengineering.co@gmail.com`)
   - Calls `/api/create-agent-job` with `x-api-key` header
4. This agent fires **immediately**:
   - Fetches `GOOGLE_DRIVE_OAUTH` secret
   - Downloads inputs from the `_pending` folder
   - Bootstraps pip if needed, installs numpy/pandas/scipy
   - Runs `join_gamma_flight.py`
   - Creates a new `{job_id}/` output folder in the main Drive
   - Uploads **ONLY** the output files (joined CSV, calibration.txt, summary.json)
   - **Verifies outputs exist** in Drive before proceeding
   - Deletes the `_pending` folder (inputs cleaned up)
   - Cleans up `/tmp`
5. Agent broadcasts a summary via Telegram (`agent-job-dm`).

## API Trigger

The GAS backend calls `/api/create-agent-job` with:
- `x-api-key` header for authentication
- `agent_job` — the job description with all parameters
- `scope` — `agents/gamma-flight-join`
- `agent_backend` — `claude-code`
- `llm_model` — `deepseek-chat`

This bypasses NextAuth session auth (same pattern as edge-kuth-portal).

## Outputs (per job, in Drive)

- `{project}_joined_gamma_flight.csv` — one row per spectrum, all channels + SI flight parameters
- `{project}_calibration.txt` — factory (Cs-check) + best-fit survey calibration
- `{project}_summary.json` — spectra/flight counts, match rate, calibration coefficients

## Deploying the backend (one-time)

1. Open https://script.google.com → New project, paste `web/gas-backend.js`.
2. Deploy → New deployment → Web app (Execute as: Me, Access: Anyone).
3. Authorize Drive + UrlFetch permissions when Google asks.
4. Copy the `/exec` URL and paste it into `DEFAULT_ENDPOINT` in `web/index.html`.
5. Publish `web/index.html` + `web/style.css` to the public Pages repo under `gamma-flight-join/`.

## Dependencies

Python engine requires `numpy`, `pandas`, `scipy`. The job prompt bootstraps pip via `get-pip.py` if `python3 -m pip` is not available, then installs the packages.

## Google Drive

- Main project folder: `18fSXEOVp8D039BUXWMiYrPuIeIXOxgt3`
- Temp pending folder: `_pending/{job_id}/` — inputs + manifest (deleted after processing)
- Output folders: `{job_id}/` in the main folder, containing only outputs
- Agent auth: `GOOGLE_DRIVE_OAUTH` secret via `agent-job-secrets`.
- GAS auth: the Apps Script runs under its deploying Google account.

## Time-match tolerance

Default is **1 s** (suits typical 1–10 Hz Airdata logs, ≈1–5 m position error). It is
adjustable per job via the form field / `--time-tolerance`. A near-zero match rate
signals a possible timezone/clock offset — flag it, don't trust the result.

## Security

The form uses a shared access password (`ACCESS_PASSWORD` in `gas-backend.js`, default
`Edge12345`). Demo-grade. For commercial use, issue per-client keys or restrict the
Apps Script deployment access.
