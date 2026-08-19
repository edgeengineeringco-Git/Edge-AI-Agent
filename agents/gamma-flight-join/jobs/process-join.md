# Gamma / Flight-Log Join — Processing Pipeline

Process a gamma spectrogram + Airdata flight-log job submitted through the public
web form. The GAS backend saves inputs to a temporary `_pending` folder in Drive
and triggers this agent via `/api/create-agent-job`.

The agent downloads the inputs, runs the join, uploads ONLY the output files to a
new job folder in the main Drive folder, verifies outputs exist, and **then deletes
the `_pending` folder** so inputs never persist.

Execute every step autonomously — never ask for input.

## Parameters (from the agent job description)

These are provided in the job trigger text:

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

```bash
[ -s "$WORK/input/$SPECTRO" ] || { echo "FAIL: spectrogram empty/missing"; exit 1; }
[ -s "$WORK/input/$FLIGHT" ] || { echo "FAIL: flight log empty/missing"; exit 1; }
head -1 "$WORK/input/$SPECTRO" | grep -q "^FORMAT:" || { echo "FAIL: not a FORMAT 3 spectrogram"; exit 1; }
```

If verification fails, broadcast the error via Telegram and skip this job.

## Step 4 — Ensure Python dependencies

The container may not have pip pre-installed. Bootstrap it if needed.

```bash
# Check if numpy/pandas/scipy are already available
python3 -c "import numpy, pandas, scipy" 2>/dev/null && echo "deps OK" || {
  # Bootstrap pip if missing
  python3 -m pip --version 2>/dev/null || {
    echo "Bootstrapping pip..."
    curl -sL https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
    python3 /tmp/get-pip.py --user --break-system-packages -q
  }
  export PATH="$HOME/.local/bin:$PATH"
  python3 -m pip install --user --break-system-packages -q numpy pandas scipy
}
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

**IMPORTANT:** `create-folder` prints the folder ID to stdout and status messages to stderr.
Capture ONLY stdout to get the clean folder ID.

```bash
# Create output folder — capture ONLY stdout (folder ID)
OUTPUT_FOLDER_ID=$(bash scripts/drive_utils.sh create-folder --name "$JOB_ID" 2>/dev/null)
echo "Output folder ID: $OUTPUT_FOLDER_ID"

UPLOAD_OK=true
for f in "$WORK/output"/*; do
  result=$(bash scripts/drive_utils.sh upload --file "$f" --folder "$OUTPUT_FOLDER_ID" 2>&1)
  if echo "$result" | grep -q "\[OK\]"; then
    echo "Uploaded: $(basename $f)"
  else
    echo "FAIL to upload: $(basename $f) — $result"
    UPLOAD_OK=false
  fi
done

if [ "$UPLOAD_OK" != "true" ]; then
  echo "ERROR: Some uploads failed. NOT deleting _pending folder."
  node skills/agent-job-dm/agent-job-dm.js send "❌ Gamma/Flight Join — Upload Failed

Job: $JOB_ID
Project: $PROJECT

Some output files failed to upload to Drive. Input files preserved in _pending folder." --broadcast
  exit 1
fi
```

## Step 7 — Verify outputs exist in Drive before deleting inputs

**CRITICAL: Only delete _pending AFTER confirming outputs are in Drive.**

```bash
# Verify the output folder has the summary file
OUTPUT_CHECK=$(bash scripts/drive_utils.sh list-folder --folder "$OUTPUT_FOLDER_ID" 2>/dev/null)
if ! echo "$OUTPUT_CHECK" | grep -q "_summary.json"; then
  echo "ERROR: Output verification failed. NOT deleting _pending folder."
  node skills/agent-job-dm/agent-job-dm.js send "❌ Gamma/Flight Join — Verification Failed

Job: $JOB_ID
Project: $PROJECT

Output files not found in Drive. Input files preserved in _pending folder." --broadcast
  exit 1
fi

# NOW it's safe to delete the _pending folder
bash scripts/drive_utils.sh delete-folder --folder "$PENDING_FOLDER_ID"
echo "_pending folder deleted — inputs cleaned up."
```

## Step 8 — Notify via Telegram

```bash
SUMMARY=$(python3 -c "
import json
d=json.load(open('$WORK/output/${PROJECT}_summary.json'))
print(f\"Spectra: {d['n_spectra']} | Matched within {d['time_tolerance_seconds']}s: {d['n_matched']}/{d['n_spectra']} ({d['match_rate']*100:.1f}%)\")
bf=d['best_fit_calibration']
print(f\"Best-fit cal: E = {bf['b0']:.3f} + {bf['b1']:.5f}·ch + {bf['b2']:.2e}·ch²\")
" 2>/dev/null || echo "Results available")

node skills/agent-job-dm/agent-job-dm.js send "✅ Gamma/Flight Join — Results Ready

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

- **ONLY output files persist in Drive.** Input files are in a temporary `_pending` folder that is DELETED after processing — but only AFTER outputs are verified in Drive.
- NEVER fabricate or substitute data. Process only the exact uploaded files.
- If a low match rate is reported (e.g. near 0%), suspect a timezone/clock offset between the two files — flag it in the Telegram message rather than presenting the result as sound.
- Do NOT write job data into the git workspace — use `/tmp`. Only agent code/config is version-controlled.
- Keep Telegram messages to the summary; never paste CSV contents.
