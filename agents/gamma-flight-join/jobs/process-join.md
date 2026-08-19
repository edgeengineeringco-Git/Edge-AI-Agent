# Gamma / Flight-Log Join — Immediate Processing Pipeline

Process a gamma spectrogram + Airdata flight-log job submitted through the public
web form. **Processing starts IMMEDIATELY via webhook trigger — no batch delay.**

The web form posts to the Google Apps Script backend (`web/gas-backend.js`), which
sends the input files as **base64 in the webhook payload** — they NEVER touch Drive.
The agent decodes the files locally, runs the join, and uploads ONLY the output
files to a new job folder in Google Drive.

Execute every step autonomously — never ask for input.

## Trigger

- **Webhook** `/gamma-join/upload` (immediate) — the GAS backend fires this trigger
  with file data inline as base64.
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
| `spectrogram_filename` | Original filename of the spectrogram (.txt) |
| `spectrogram_b64` | Base64-encoded spectrogram file data |
| `flightlog_filename` | Original filename of the flight log (.csv) |
| `flightlog_b64` | Base64-encoded flight log file data |

**NO `pending_folder_id`** — input files are NOT in Drive. They arrive inline.

## Google Drive layout

- **Main project folder:** `18fSXEOVp8D039BUXWMiYrPuIeIXOxgt3`
- **Output job folder:** `{job_id}/` — created in the main folder, contains ONLY outputs:
  - `{project}_joined_gamma_flight.csv`
  - `{project}_calibration.txt`
  - `{project}_summary.json`

**Input files NEVER touch Drive.** They are decoded from the webhook payload to `/tmp`.

## Step 0 — Credentials

```bash
export GOOGLE_DRIVE_OAUTH=$(node skills/agent-job-secrets/agent-job-secrets.js get GOOGLE_DRIVE_OAUTH 2>/dev/null || echo "")
[ -z "$GOOGLE_DRIVE_OAUTH" ] && { echo "FATAL: no Google Drive credentials"; exit 1; }
```

## Step 1 — Set up working directory and decode inputs from payload

The input files arrive as base64-encoded strings in the webhook payload.
Decode them to `/tmp` — they never exist in Drive.

```bash
WORK=/tmp/gamma-join-$$; mkdir -p "$WORK/input" "$WORK/output"

# Decode spectrogram from base64 payload
echo "$SPECTROGRAM_B64" | base64 -d > "$WORK/input/$SPECTROGRAM_FILENAME"

# Decode flight log from base64 payload
echo "$FLIGHTLOG_B64" | base64 -d > "$WORK/input/$FLIGHTLOG_FILENAME"
```

## Step 2 — Verify inputs (NEVER FABRICATE DATA)

- Both input files present and non-empty.
- Spectrogram first line begins with `FORMAT:`.

If verification fails, broadcast the error via Telegram and skip this job.

```bash
[ -s "$WORK/input/$SPECTROGRAM_FILENAME" ] || { echo "FAIL: spectrogram empty/missing"; exit 1; }
[ -s "$WORK/input/$FLIGHTLOG_FILENAME" ] || { echo "FAIL: flight log empty/missing"; exit 1; }
head -1 "$WORK/input/$SPECTROGRAM_FILENAME" | grep -q "^FORMAT:" || { echo "FAIL: not a FORMAT 3 spectrogram"; exit 1; }
```

## Step 3 — Ensure Python dependencies

```bash
python3 -c "import numpy, pandas, scipy" 2>/dev/null || \
  python3 -m pip install --user --break-system-packages -q numpy pandas scipy
```

## Step 4 — Run the join

```bash
python3 scripts/join_gamma_flight.py \
  --spectrogram "$WORK/input/$SPECTROGRAM_FILENAME" \
  --flightlog   "$WORK/input/$FLIGHTLOG_FILENAME" \
  --project-name "$PROJECT_NAME" \
  --output-dir  "$WORK/output" \
  --output-csv  "${PROJECT_NAME}_joined_gamma_flight.csv" \
  --time-tolerance "$TIME_TOLERANCE" \
  --factory-a0 "$FACTORY_A0" --factory-a1 "$FACTORY_A1" --factory-a2 "$FACTORY_A2" --factory-a3 "$FACTORY_A3"
```

Outputs: `{project}_joined_gamma_flight.csv`, `{project}_calibration.txt`, `{project}_summary.json`.

## Step 5 — Create output folder and upload ONLY outputs

Create a new job folder in the main Drive folder. Upload ONLY the processed output
files — input files are not in Drive and never will be.

```bash
OUTPUT_FOLDER_ID=$(bash scripts/drive_utils.sh create-folder --name "$JOB_ID")
# $OUTPUT_FOLDER_ID now points to the new folder in the main project Drive

for f in "$WORK/output"/*; do
  bash scripts/drive_utils.sh upload --file "$f" --folder "$OUTPUT_FOLDER_ID" | tail -1
done
```

## Step 6 — Notify via Telegram

Read the summary JSON and broadcast a concise result:

```bash
SUMMARY=$(python3 -c "
import json
d=json.load(open('$WORK/output/${PROJECT_NAME}_summary.json'))
print(f\"Spectra: {d['n_spectra']} | Matched within {d['time_tolerance_seconds']}s: {d['n_matched']}/{d['n_spectra']} ({d['match_rate']*100:.1f}%)\")
bf=d['best_fit_calibration']
print(f\"Best-fit cal: E = {bf['b0']:.3f} + {bf['b1']:.5f}·ch + {bf['b2']:.2e}·ch²\")
" 2>/dev/null || echo "Results available")

node skills/agent-job-dm/agent-job-dm.js send "📡 Gamma/Flight Join — Results Ready

Job: $JOB_ID
Project: $PROJECT_NAME

$SUMMARY

Outputs in Drive folder:
https://drive.google.com/drive/folders/$OUTPUT_FOLDER_ID" --broadcast
```

## Step 7 — Cleanup

```bash
rm -rf "$WORK"
```

## Critical rules

- **ONLY output files go to Drive.** Input files arrive via webhook payload and are decoded locally — they are NEVER uploaded to Drive.
- NEVER fabricate or substitute data. Process only the exact uploaded files.
- If a low match rate is reported (e.g. near 0%), suspect a timezone/clock offset between
  the two files — flag it in the Telegram message rather than presenting the result as sound.
- Do NOT write job data into the git workspace — use `/tmp`. Only agent code/config is version-controlled.
- Keep Telegram messages to the summary; never paste CSV contents.
