# Gamma / Flight-Log Join — Immediate Processing Pipeline

Process a gamma spectrogram + Airdata flight-log pair **immediately** on receipt. Do not wait for batch cycles. Execute every step autonomously — never ask for input.

## Trigger

Runs when a client submits the portal form. The upload server has already saved the files and written a payload. The trigger passes these variables:

| Field | Description |
|-------|-------------|
| `job_id` | Unique job identifier (e.g., `Q12_survey_20260819_141600`) |
| `project_name` | Project name (used in output filenames) |
| `client_name` | Client / organisation (may be blank) |
| `email` | Notification email (may be blank) |
| `time_tolerance` | Nearest-time match tolerance in seconds (default 5) |
| `factory_a0..a3` | Factory (Cs-check) calibration polynomial coefficients |
| `spectrogram_file` | Saved spectrogram filename |
| `flightlog_file` | Saved Airdata flight-log filename |

Working directory when this job runs: `agents/gamma-flight-join/` (scoped). Repo root is two levels up.

## Paths

- Job root: `data/gamma-flight-join/jobs/{job_id}/` (relative to repo root, i.e. `../../data/gamma-flight-join/jobs/{job_id}/`)
- Input files: `<job root>/input/{spectrogram_file}` and `<job root>/input/{flightlog_file}`
- Payload: `<job root>/webhook-payload.json`
- Outputs: write to `<job root>/output/`

## Step 1 — Verify inputs (NEVER FABRICATE DATA)

```bash
JOB_ROOT="../../data/gamma-flight-join/jobs/{job_id}"

if [ ! -f "$JOB_ROOT/webhook-payload.json" ]; then
  echo "FATAL: webhook-payload.json missing for {job_id}"
  node ../../skills/agent-job-dm/agent-job-dm.js send "FATAL: Gamma-join job {job_id} — payload missing. Pipeline stopped." --broadcast
  exit 1
fi

SPECTRO="$JOB_ROOT/input/{spectrogram_file}"
FLIGHT="$JOB_ROOT/input/{flightlog_file}"

for f in "$SPECTRO" "$FLIGHT"; do
  if [ ! -s "$f" ]; then
    echo "FATAL: input file missing or empty: $f"
    node ../../skills/agent-job-dm/agent-job-dm.js send "FATAL: Gamma-join job {job_id} — input file missing ($f). Pipeline stopped." --broadcast
    exit 1
  fi
done

# The spectrogram must be FORMAT 3.
head -1 "$SPECTRO" | grep -q "^FORMAT:" || {
  echo "FATAL: spectrogram is not a FORMAT header file"
  node ../../skills/agent-job-dm/agent-job-dm.js send "FATAL: Gamma-join job {job_id} — spectrogram is not FORMAT 3. Pipeline stopped." --broadcast
  exit 1
}
echo "Inputs verified."
```

## Step 2 — Ensure Python dependencies

The engine needs `numpy`, `pandas`, `scipy`.

```bash
python3 -c "import numpy, pandas, scipy" 2>/dev/null || \
  python3 -m pip install --user --break-system-packages -q numpy pandas scipy 2>&1 | tail -2 || \
  { command -v apt-get >/dev/null && apt-get install -y -qq python3-numpy python3-pandas python3-scipy 2>/dev/null; }
python3 -c "import numpy, pandas, scipy; print('deps OK')"
```

## Step 3 — Run the join

```bash
mkdir -p "$JOB_ROOT/output"
python3 scripts/join_gamma_flight.py \
  --spectrogram "$SPECTRO" \
  --flightlog   "$FLIGHT" \
  --project-name "{project_name}" \
  --output-dir  "$JOB_ROOT/output" \
  --output-csv  "{project_name}_joined_gamma_flight.csv" \
  --time-tolerance {time_tolerance} \
  --factory-a0 {factory_a0} --factory-a1 {factory_a1} \
  --factory-a2 {factory_a2} --factory-a3 {factory_a3}
```

Outputs written to `$JOB_ROOT/output/`:
- `{project_name}_joined_gamma_flight.csv` — one row per spectrum, all channels + SI flight params
- `{project_name}_calibration.txt` — factory + best-fit calibration
- `{project_name}_summary.json` — run summary (spectra count, match rate, calibration)

If the script exits non-zero, broadcast the error via Telegram and stop.

## Step 4 — Upload outputs to Google Drive (per-job folder)

Every job gets its **own folder** named `{job_id}` inside the project Drive folder
`18fSXEOVp8D039BUXWMiYrPuIeIXOxgt3`.

```bash
# Fetch OAuth credentials (auto-refreshed) and export for drive_utils.sh
export GOOGLE_DRIVE_OAUTH=$(node ../../skills/agent-job-secrets/agent-job-secrets.js get GOOGLE_DRIVE_OAUTH 2>/dev/null || echo "")

if [ -z "$GOOGLE_DRIVE_OAUTH" ]; then
  echo "[WARN] No Google Drive credentials — skipping Drive upload (degraded mode)."
  DRIVE_LINK="(Drive not configured)"
else
  FOLDER_ID=$(bash scripts/drive_utils.sh create-folder --name "{job_id}" | tail -1)
  DRIVE_LINK="https://drive.google.com/drive/folders/$FOLDER_ID"
  for f in "$JOB_ROOT/output"/*; do
    bash scripts/drive_utils.sh upload --file "$f" --folder "$FOLDER_ID" | tail -1
  done
  # Also upload the original inputs for provenance.
  bash scripts/drive_utils.sh upload --file "$SPECTRO" --folder "$FOLDER_ID" | tail -1
  bash scripts/drive_utils.sh upload --file "$FLIGHT" --folder "$FOLDER_ID" | tail -1
  echo "Drive folder: $DRIVE_LINK"
fi
```

If Drive upload fails, log the error but still send the Telegram summary (degraded mode).

## Step 5 — Notify via Telegram

Read the summary JSON and broadcast a concise result to all admins.

```bash
SUMMARY=$(python3 -c "
import json
d = json.load(open('$JOB_ROOT/output/{project_name}_summary.json'))
print(f\"Spectra: {d['n_spectra']}  |  Flight fixes: {d['n_flight_records']}\")
print(f\"Matched within {d['time_tolerance_seconds']}s: {d['n_matched']}/{d['n_spectra']} ({d['match_rate']*100:.1f}%)\")
print(f\"Detector: {d['detector']}\")
bf = d['best_fit_calibration']
print(f\"Best-fit cal: E = {bf['b0']:.3f} + {bf['b1']:.5f}·ch + {bf['b2']:.2e}·ch²\")
" 2>/dev/null || echo "Results available")

node ../../skills/agent-job-dm/agent-job-dm.js send "📡 Gamma/Flight Join — Results Ready

Job: {job_id}
Project: {project_name}

$SUMMARY

Outputs (joined CSV + calibration + summary) in Drive folder:
$DRIVE_LINK" --broadcast
```

## Critical rules

- NEVER fabricate or substitute data. Process only the exact uploaded files for this job.
- If any verification fails, broadcast the error via Telegram and stop. Failing is better than wrong results.
- Do not commit job data or outputs — everything under `data/` is git-ignored runtime data. Only the agent code/config is version-controlled.
- Keep the Telegram message to the summary; do not paste CSV contents.
