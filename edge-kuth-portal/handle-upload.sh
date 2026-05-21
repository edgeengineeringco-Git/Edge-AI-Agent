#!/bin/bash
# EDGE K/U/Th Portal — Handle Upload & Process Immediately
#
# Usage: handle-upload.sh --job-id <id> --client <name> --email <email> [options]
#
# This script:
#   1. Reads job config from arguments or a JSON file
#   2. Finds .spc files in the incoming directory
#   3. Runs the Python estimation engine
#   4. Saves results CSV to the output directory
#   5. Outputs a summary for Telegram notification
#
# The agent (Claude Code) calls this after receiving a webhook notification.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
INCOMING_DIR="$SCRIPT_DIR/incoming"
OUTPUT_DIR="$SCRIPT_DIR/output"
JOBS_DIR="$SCRIPT_DIR/jobs"

# Default values
JOB_ID=""
CLIENT_NAME=""
EMAIL=""
ROI_HALF_WIDTH=20
NORMALIZE_LT=""
PAD_DIR="$SCRIPT_DIR/pad_reference"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --job-id) JOB_ID="$2"; shift 2 ;;
        --client) CLIENT_NAME="$2"; shift 2 ;;
        --email) EMAIL="$2"; shift 2 ;;
        --roi-half-width) ROI_HALF_WIDTH="$2"; shift 2 ;;
        --normalize-live-time) NORMALIZE_LT="--normalize-live-time"; shift ;;
        --pad-dir) PAD_DIR="$2"; shift 2 ;;
        --json) JSON_FILE="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# If JSON file provided, parse fields from it
if [[ -n "${JSON_FILE:-}" && -f "$JSON_FILE" ]]; then
    JOB_ID="${JOB_ID:-$(python3 -c "import json; print(json.load(open('$JSON_FILE')).get('job_id',''))")}"
    CLIENT_NAME="${CLIENT_NAME:-$(python3 -c "import json; print(json.load(open('$JSON_FILE')).get('client_name',''))")}"
    EMAIL="${EMAIL:-$(python3 -c "import json; print(json.load(open('$JSON_FILE')).get('email',''))")}"
fi

# Generate job ID if not provided
if [[ -z "$JOB_ID" ]]; then
    JOB_ID="job_$(date +%Y%m%d_%H%M%S)"
fi

# Create job-specific directories
JOB_INCOMING="$JOBS_DIR/$JOB_ID/spectra"
JOB_OUTPUT="$JOBS_DIR/$JOB_ID"
mkdir -p "$JOB_INCOMING" "$JOB_OUTPUT"

echo "=== EDGE K/U/Th Portal — Processing Job ==="
echo "Job ID:      $JOB_ID"
echo "Client:      ${CLIENT_NAME:-anonymous}"
echo "Email:       ${EMAIL:-none}"
echo "ROI half:    $ROI_HALF_WIDTH keV"
echo "Normalize:   ${NORMALIZE_LT:+yes}"
echo ""

# Find .spc files: first check job directory, then incoming
SPC_FILES=()
# Check if files were already placed in job incoming dir
for f in "$JOB_INCOMING"/*.spc; do
    if [[ -f "$f" ]]; then
        SPC_FILES+=("$f")
    fi
done
# If no files in job dir, check global incoming
if [[ ${#SPC_FILES[@]} -eq 0 ]]; then
    for f in "$INCOMING_DIR"/*.spc; do
        if [[ -f "$f" ]]; then
            cp "$f" "$JOB_INCOMING/"
            SPC_FILES+=("$f")
        fi
    done
fi

if [[ ${#SPC_FILES[@]} -eq 0 ]]; then
    echo "[ERROR] No .spc files found in incoming/ or jobs/$JOB_ID/"
    echo "Place .spc files in one of these directories and re-run."
    exit 1
fi

echo "Found ${#SPC_FILES[@]} .spc file(s) to process"
for f in "${SPC_FILES[@]}"; do
    echo "  - $(basename "$f")"
done
echo ""

RESULTS_CSV="$JOB_OUTPUT/results.csv"

# Locate the Python engine
PYTHON_SCRIPT="$SCRIPT_DIR/estimate_k_u_th_matrix.py"
if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    PYTHON_SCRIPT="$WORKSPACE_ROOT/edge-kuth-portal/estimate_k_u_th_matrix.py"
fi

# Check PAD reference directory
if [[ ! -d "$PAD_DIR" ]]; then
    # Use synthetic test PADs if no real ones
    PAD_DIR="$JOB_OUTPUT/test_pads"
    echo "[INFO] No PAD reference directory found. Generating test PAD spectra..."
    python3 "$SCRIPT_DIR/generate_test_data.py" --output-dir "$PAD_DIR" 2>/dev/null || \
    python3 "$WORKSPACE_ROOT/edge-kuth-portal/generate_test_data.py" --output-dir "$PAD_DIR" 2>/dev/null || true
    if [[ -d "$PAD_DIR/pads" ]]; then
        PAD_DIR="$PAD_DIR/pads"
    fi
fi

# Run the Python estimation
echo "Running K/U/Th estimation..."
python3 "$PYTHON_SCRIPT" \
    --spectra-dir "$JOB_INCOMING" \
    --pad-dir "$PAD_DIR" \
    --output "$RESULTS_CSV" \
    --roi-half-width "$ROI_HALF_WIDTH" \
    ${NORMALIZE_LT:-}

echo ""
echo "=== Results ==="
echo "CSV: $RESULTS_CSV"
echo ""

# Output summary for Telegram
if [[ -f "$RESULTS_CSV" ]]; then
    echo "--- BEGIN TELEGRAM MESSAGE ---"
    echo "📊 K/U/Th Analysis Complete"
    echo "Job: $JOB_ID"
    echo "Client: ${CLIENT_NAME:-anonymous}"
    echo ""
    # Show summary stats
    python3 -c "
import csv
with open('$RESULTS_CSV') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
n = len(rows)
k = [float(r['K_percent']) for r in rows]
u = [float(r['U_ppm']) for r in rows]
th = [float(r['Th_ppm']) for r in rows]
r2 = [float(r['fit_r2']) for r in rows]
has_loc = 'lat' in rows[0] and rows[0]['lat']
has_elev = 'elevation' in rows[0] and rows[0]['elevation']
print(f'Files:  {n}')
if has_loc:
    print(f'Location data:  yes')
if has_elev:
    print(f'Elevation data: yes')
print(f'K:  {min(k):.2f}–{max(k):.2f}%  (avg {sum(k)/n:.2f})')
print(f'U:  {min(u):.1f}–{max(u):.1f} ppm  (avg {sum(u)/n:.1f})')
print(f'Th: {min(th):.1f}–{max(th):.1f} ppm  (avg {sum(th)/n:.1f})')
print(f'R²: {min(r2):.3f}–{max(r2):.3f}')
" 2>/dev/null || true
    echo ""
    echo "Full CSV:"
    cat "$RESULTS_CSV"
    echo ""
    echo "--- END TELEGRAM MESSAGE ---"
else
    echo "[ERROR] No results CSV generated"
    exit 1
fi
