# Gamma / Flight-Log Join — Immediate Processing Pipeline

Process a gamma spectrogram + Airdata flight-log job submitted through the public
web form. **Processing starts IMMEDIATELY via webhook trigger — no batch delay.**

The web form posts to the Google Apps Script backend (`web/gas-backend.js`), which
saves the input files to a temporary `_pending` folder in Drive and triggers this
agent via webhook. The agent downloads the inputs, runs the join, uploads ONLY the
output files to a new job folder in the main Drive folder, and deletes the temp folder.

Execute every step autonomously — never ask for input.

## Trigger

- **Webhook** `/gamma-join/upload` (immediate) — the GAS backend fires this trigger
  as soon as a client submits the form.
- **Manual** — a chat request to process a specific job.

## Parameters (from webhook payload)

These are provided by the trigger:

| Parameter | Description |
|-----------|-------------|
| `job_id` | Unique job identifier (e.g. `Q12_survey_20260819_120000`) |
| `project_name` | Human-readable project name |
| `client_name` | Client/organisation (optional) |
| `email` | Notification email (optional) |
| `time_tolerance` | Max seconds for time matching (default: 1) |
| `factory_a0..a3` | Factory calibration coefficients |
| `spectrogram_file` | Filename of the spectrogram (.txt) |
| `flightlog_file` | Filename of the flight log (.csv) |
| `pending_folder_id` | Google Drive folder ID containing the input files |

## Google Drive layout

- **Main project folder:** `18fSXEOVp8D039BUXWMiYrPuIeIXOxgt3`
- **Temp pending folder:** `_pending/{job_id}/` — contains input files + manifest (DELETED after processing)
- **Output job folder:** `{job_id}/` — created in the main folder, contains ONLY outputs:
  - `{project}_joined_gamma_flight.csv`
  - `{project}_calibration.txt`
  - `{project}_summary.json`

**Inputs NEVER stay in Drive.** The `_pending` folder is deleted after processing.

## Step 0 — Credentials

```bash
export GOOGLE_DRIVE_OAUTH=$(node skills/agent-job-secrets/agent-job-secrets.js get GOOGLE_DRIVE_OAUTH 2>/dev/null || echo "")
[ -z "$GOOGLE_DRIVE_OAUTH" ] && { echo "FATAL: no Google Drive credentials"; exit 1; }
```

## Step 1 — Set up working directory

```bash
WORK=/tmp/gamma-join-$$; mkdir -p "$WORK/input" "$WORK/output"
```

## Step 2 — Download inputs from the _pending folder

The `pending_folder_id` points to the temp Drive folder containing the input files
and `job-manifest.json`.

```bash
# Download manifest
bash scripts/drive_utils.sh download --folder "$PENDING_FOLDER_ID" --name job-manifest.json --out "$WORK/job-manifest.json"

# Read manifest for filenames and settings
SPECTRO=$(python3 -c "import json;print(json.load(open('$WORK/job-manifest.json'))['spectrogram_file'])")
FLIGHT=$(python3 -c "import json;print(json.load(open('$WORK/job-manifest.json'))['flightlog_file'])")
PROJECT=$(python3 -c "import json;print(json.load(open('$WORK/job-manifest.json'))['project_name'])")
TOL=$(python3 -c "import json;print(json.load(open('$WORK/job-manifest.json')).get('time_tolerance',1))")
A0=$(python3 -c "import json;print(json.load(open('$WORK/job-manifest.json')).get('factory_a0',0))")
A1=$(python3 -c "import json;print(json.load(open('$WORK/job-manifest.json')).get('factory_a1',0.739863))")
A2=$(python3 -c "import json;print(json.load(open('$WORK/job-manifest.json')).get('factory_a2',0))")
A3=$(python3 -c "import json;print(json.load(open('$WORK/job-manifest.json')).get('factory_a3',0))")

# Download input files
bash scripts/drive_utils.sh download --folder "$PENDING_FOLDER_ID" --name "$SPECTRO" --out "$WORK/input/$SPECTRO"
bash scripts/drive_utils.sh download --folder "$PENDING_FOLDER_ID" --name "$FLIGHT" --out "$WORK/input/$FLIGHT"
```

## Step 3 — Verify inputs (NEVER FABRICATE DATA)

- Both input files present and non-empty.
- Spectrogram first line begins with `FORMAT:`.

If verification fails, broadcast the error via Telegram and skip this job.

```bash
[ -s "$WORK/input/$SPECTRO" ] || { echo "FAIL: spectrogram empty/missing"; exit 1; }
[ -s "$WORK/input/$FLIGHT" ] || { echo "FAIL: flight log empty/missing"; exit 1; }
head -1 "$WORK/input/$SPECTRO" | grep -q "^FORMAT:" || { echo "FAIL: not a FORMAT 3 spectrogram"; exit 1; }
```

## Step 4 — Ensure Python dependencies

```bash
python3 -c "import numpy, pandas, scipy" 2>/dev/null || \
  python3 -m pip install --user --break-system-packages -q numpy pandas scipy
```

## Step 5 — Run the join

```bash
python3 scripts/join_gamma_flight.py \
  --spectrogram "$WORK/input/$SPECTRO" \
  --flightlog   "$WORK/input/$FLIGHT" \
  --project-name "$PROJECT" \
  --output-dir  "$WORK/output" \
  --output-csv  "${PROJECT}_joined_gamma_flight.csv" \
  --time-tolerance "$TOL" \
  --factory-a0 "$A0" --factory-a1 "$A1" --factory-a2 "$A2" --factory-a3 "$A3"
```

Outputs: `{project}_joined_gamma_flight.csv`, `{project}_calibration.txt`, `{project}_summary.json`.

## Step 6 — Create output folder and upload ONLY outputs

Create a new job folder in the main Drive folder. Upload ONLY the processed output
files — never upload the input files.

```bash
OUTPUT_FOLDER_ID=$(bash scripts/drive_utils.sh create-folder --name "$JOB_ID")
# $OUTPUT_FOLDER_ID now points to the new folder in the main project Drive

for f in "$WORK/output"/*; do
  bash scripts/drive_utils.sh upload --file "$f" --folder "$OUTPUT_FOLDER_ID" | tail -1
done
```

## Step 7 — Delete the _pending temp folder (inputs cleaned up)

```bash
bash scripts/drive_utils.sh delete-folder --folder "$PENDING_FOLDER_ID"
```

This removes the input files from Drive permanently. Only the output folder remains.

## Step 8 — Notify via Telegram

Read the summary JSON and broadcast a concise result:

```bash
SUMMARY=$(python3 -c "
import json
d=json.load(open('$WORK/output/${PROJECT}_summary.json'))
print(f\"Spectra: {d['n_spectra']} | Matched within {d['time_tolerance_seconds']}s: {d['n_matched']}/{d['n_spectra']} ({d['match_rate']*100:.1f}%)\")
bf=d['best_fit_calibration']
print(f\"Best-fit cal: E = {bf['b0']:.3f} + {bf['b1']:.5f}·ch + {bf['b2']:.2e}·ch²\")
" 2>/dev/null || echo "Results available")

node skills/agent-job-dm/agent-job-dm.js send "📡 Gamma/Flight Join — Results Ready

Job: $JOB_ID
Project: $PROJECT

$SUMMARY

Outputs in Drive folder:
https://drive.google.com/drive/folders/$OUTPUT_FOLDER_ID" --broadcast
```

## Step 9 — Cleanup

```bash
rm -rf "$WORK"
```

## Critical rules

- **ONLY output files go to Drive.** Input files are deleted from the _pending folder after processing.
- NEVER fabricate or substitute data. Process only the exact uploaded files.
- If a low match rate is reported (e.g. near 0%), suspect a timezone/clock offset between
  the two files — flag it in the Telegram message rather than presenting the result as sound.
- Do NOT write job data into the git workspace — use `/tmp`. Only agent code/config is version-controlled.
- Keep Telegram messages to the summary; never paste CSV contents.
