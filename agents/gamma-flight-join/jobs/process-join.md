# Gamma / Flight-Log Join — Drive-Scan Processing Pipeline

Process gamma spectrogram + Airdata flight-log jobs that clients submit through the
public web form. **No Docker, no server** — the form posts to a Google Apps Script
backend (`web/gas-backend.js`) that saves the two input files and a `job-manifest.json`
into a per-job subfolder inside the project Drive folder. This job downloads pending
jobs, runs the join, and uploads the results back into the same folder.

Execute every step autonomously — never ask for input.

## Trigger

- **Batch cron** `gamma-flight-join-batch` (scan for pending jobs), or
- **Manual** — a chat request to process a specific job or all pending jobs.

Working directory when scoped: `agents/gamma-flight-join/`. Repo root is two levels up.

## Google Drive layout

- Project folder: `18fSXEOVp8D039BUXWMiYrPuIeIXOxgt3`
- Each job = one subfolder named `{job_id}` containing:
  - after processing: the joined CSV, calibration.txt, summary.json (only outputs remain)
  - the spectrogram (`.txt`), the flight log (`.csv`), and `job-manifest.json` are deleted after successful processing

A job is **pending** when its folder has a `job-manifest.json` but no `*_summary.json`.

## Step 0 — Credentials

```bash
export GOOGLE_DRIVE_OAUTH=$(node skills/agent-job-secrets/agent-job-secrets.js get GOOGLE_DRIVE_OAUTH 2>/dev/null || echo "")
[ -z "$GOOGLE_DRIVE_OAUTH" ] && { echo "FATAL: no Google Drive credentials"; exit 1; }
```

## Step 1 — Find pending job folders

Use `scripts/drive_utils.sh list-jobs` to list subfolders of the project folder and
their contents. For each folder that has a manifest but no summary, process it.
Work in a scratch dir under `/tmp` (never write job data into the git workspace).

```bash
WORK=/tmp/gamma-join-$$; mkdir -p "$WORK"
bash scripts/drive_utils.sh list-jobs
```

## Step 2 — For each pending job

```bash
JOB_DIR="$WORK/$JOB_ID"; mkdir -p "$JOB_DIR/input" "$JOB_DIR/output"

# Download the manifest + both input files from the job's Drive folder.
bash scripts/drive_utils.sh download --folder "$FOLDER_ID" --name job-manifest.json --out "$JOB_DIR/job-manifest.json"
# (download the .txt and .csv named in the manifest into $JOB_DIR/input/)
```

Read the manifest for `project_name`, `time_tolerance` (default 1), `factory_a0..a3`,
`spectrogram_file`, `flightlog_file`.

### Verify inputs (NEVER FABRICATE DATA)

- Both input files present and non-empty.
- Spectrogram first line begins with `FORMAT:`.

If verification fails, broadcast the error via Telegram and skip this job.

### Ensure Python dependencies

```bash
python3 -c "import numpy, pandas, scipy" 2>/dev/null || \
  python3 -m pip install --user --break-system-packages -q numpy pandas scipy
```

### Run the join

```bash
python3 scripts/join_gamma_flight.py \
  --spectrogram "$JOB_DIR/input/$SPECTRO" \
  --flightlog   "$JOB_DIR/input/$FLIGHT" \
  --project-name "$PROJECT" \
  --output-dir  "$JOB_DIR/output" \
  --output-csv  "${PROJECT}_joined_gamma_flight.csv" \
  --time-tolerance "$TOL" \
  --factory-a0 "$A0" --factory-a1 "$A1" --factory-a2 "$A2" --factory-a3 "$A3"
```

Outputs: `{project}_joined_gamma_flight.csv`, `{project}_calibration.txt`, `{project}_summary.json`.

### Upload results back to the SAME job folder

```bash
for f in "$JOB_DIR/output"/*; do
  bash scripts/drive_utils.sh upload --file "$f" --folder "$FOLDER_ID" | tail -1
done
```

### Clean up input files from Drive

Only output files should remain in the Drive job folder. Remove the input files and manifest:

```bash
bash scripts/drive_utils.sh delete --folder "$FOLDER_ID" --name "$SPECTRO"
bash scripts/drive_utils.sh delete --folder "$FOLDER_ID" --name "$FLIGHT"
bash scripts/drive_utils.sh delete --folder "$FOLDER_ID" --name "job-manifest.json"
```

### Notify via Telegram

Read the summary JSON and broadcast a concise result:

```bash
SUMMARY=$(python3 -c "
import json
d=json.load(open('$JOB_DIR/output/${PROJECT}_summary.json'))
print(f\"Spectra: {d['n_spectra']} | Matched within {d['time_tolerance_seconds']}s: {d['n_matched']}/{d['n_spectra']} ({d['match_rate']*100:.1f}%)\")
bf=d['best_fit_calibration']
print(f\"Best-fit cal: E = {bf['b0']:.3f} + {bf['b1']:.5f}·ch + {bf['b2']:.2e}·ch²\")
" 2>/dev/null || echo "Results available")

node skills/agent-job-dm/agent-job-dm.js send "📡 Gamma/Flight Join — Results Ready

Job: $JOB_ID
Project: $PROJECT

$SUMMARY

Outputs added to Drive folder:
https://drive.google.com/drive/folders/$FOLDER_ID" --broadcast
```

## Step 3 — Cleanup

```bash
rm -rf "$WORK"
```

## Critical rules

- NEVER fabricate or substitute data. Process only the exact uploaded files for each job.
- If a low match rate is reported (e.g. near 0%), suspect a timezone/clock offset between
  the two files — flag it in the Telegram message rather than presenting the result as sound.
- Do NOT write job data into the git workspace — use `/tmp`. Only agent code/config is version-controlled.
- Keep Telegram messages to the summary; never paste CSV contents.
