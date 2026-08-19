# Gamma / Flight-Log Join — Process from Disk

Process a gamma/flight-log join job. Input files are already saved to disk by the
upload server. **Do NOT upload input files to Drive — only outputs go to Drive.**

Execute every step autonomously — never ask for input.

## Parameters (from webhook/job trigger)

| Parameter | Description |
|-----------|-------------|
| `job_id` | Unique job identifier |
| `project_name` | Project name for output files |
| `input_dir` | **Disk path** where input files are saved |
| `spectrogram_file` | Filename of the spectrogram (.txt) |
| `flightlog_file` | Filename of the flight log (.csv) |
| `time_tolerance` | Max seconds for time matching (default: 1) |
| `factory_a0..a3` | Factory calibration coefficients |
| `client_name` | Client name (optional) |
| `email` | Notification email (optional) |

## Step 1 — Verify input files on disk

```bash
SPECTRO="$INPUT_DIR/$SPECTROGRAM_FILE"
FLIGHT="$INPUT_DIR/$FLIGHTLOG_FILE"

[ -s "$SPECTRO" ] || { echo "FAIL: spectrogram missing at $SPECTRO"; exit 1; }
[ -s "$FLIGHT" ] || { echo "FAIL: flight log missing at $FLIGHT"; exit 1; }
head -1 "$SPECTRO" | grep -q "^FORMAT:" || { echo "FAIL: not a FORMAT 3 spectrogram"; exit 1; }
```

## Step 2 — Set up output directory

```bash
OUTPUT_DIR="/tmp/gamma-join-output-$$"
mkdir -p "$OUTPUT_DIR"
```

## Step 3 — Ensure Python dependencies

```bash
python3 -c "import numpy, pandas, scipy" 2>/dev/null || \
  python3 -m pip install --user --break-system-packages -q numpy pandas scipy
```

## Step 4 — Run the join

```bash
python3 agents/gamma-flight-join/scripts/join_gamma_flight.py \
  --spectrogram "$SPECTRO" \
  --flightlog   "$FLIGHT" \
  --project-name "$PROJECT_NAME" \
  --output-dir  "$OUTPUT_DIR" \
  --output-csv  "${PROJECT_NAME}_joined_gamma_flight.csv" \
  --time-tolerance "$TIME_TOLERANCE" \
  --factory-a0 "$FACTORY_A0" --factory-a1 "$FACTORY_A1" \
  --factory-a2 "$FACTORY_A2" --factory-a3 "$FACTORY_A3"
```

## Step 5 — Upload ONLY outputs to Google Drive

```bash
# Get Drive credentials
export GOOGLE_DRIVE_OAUTH=$(node skills/agent-job-secrets/agent-job-secrets.js get GOOGLE_DRIVE_OAUTH 2>/dev/null || echo "")
[ -z "$GOOGLE_DRIVE_OAUTH" ] && { echo "FATAL: no Google Drive credentials"; exit 1; }

# Create output folder in Drive
DRIVE_FOLDER_ID=$(bash agents/gamma-flight-join/scripts/drive_utils.sh create-folder --name "$JOB_ID")

# Upload ONLY output files (never inputs)
for f in "$OUTPUT_DIR"/*; do
  bash agents/gamma-flight-join/scripts/drive_utils.sh upload --file "$f" --folder "$DRIVE_FOLDER_ID" | tail -1
done
```

## Step 6 — Read summary and notify via Telegram

```bash
SUMMARY=$(python3 -c "
import json
d=json.load(open('$OUTPUT_DIR/${PROJECT_NAME}_summary.json'))
print(f\"Spectra: {d['n_spectra']} | Matched within {d['time_tolerance_seconds']}s: {d['n_matched']}/{d['n_spectra']} ({d['match_rate']*100:.1f}%)\")
bf=d['best_fit_calibration']
print(f\"Best-fit cal: E = {bf['b0']:.3f} + {bf['b1']:.5f}·ch + {bf['b2']:.2e}·ch²\")
" 2>/dev/null || echo "Results available")

node skills/agent-job-dm/agent-job-dm.js send "📡 Gamma/Flight Join — Results Ready

Job: $JOB_ID
Project: $PROJECT_NAME

$SUMMARY

Outputs in Drive:
https://drive.google.com/drive/folders/$DRIVE_FOLDER_ID" --broadcast
```

## Step 7 — Cleanup

```bash
rm -rf "$OUTPUT_DIR"
# Input files stay on disk at $INPUT_DIR (never uploaded to Drive)
```

## Critical rules

- **NEVER upload input files to Drive.** Only the joined CSV, calibration.txt, and summary.json go to Drive.
- NEVER fabricate or substitute data.
- A near-zero match rate signals timezone/clock offset — flag it in the Telegram message.
- Keep Telegram messages to the summary; never paste CSV contents.
