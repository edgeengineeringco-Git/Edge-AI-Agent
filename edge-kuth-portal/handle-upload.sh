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

# Ensure numpy is available (needed by estimate_k_u_th_matrix.py)
if ! python3 -c "import numpy" 2>/dev/null; then
    echo "[SETUP] numpy not found, installing..."
    if command -v apt-get &>/dev/null; then
        apt-get update -qq && apt-get install -y -qq python3-numpy 2>/dev/null && echo "[SETUP] numpy installed via apt" || \
        { python3 -m pip install numpy -q 2>/dev/null && echo "[SETUP] numpy installed via pip"; } || \
        { curl -sS https://bootstrap.pypa.io/get-pip.py | python3 -q 2>/dev/null && pip3 install numpy -q 2>/dev/null && echo "[SETUP] numpy installed via pip (bootstrap)"; } || \
        echo "[WARN] Could not install numpy — estimation will fail"
    elif command -v pip3 &>/dev/null; then
        pip3 install numpy -q && echo "[SETUP] numpy installed via pip" || echo "[WARN] Could not install numpy"
    else
        echo "[WARN] No package manager found — estimation may fail if numpy is missing"
    fi
fi

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

# Normalize all spectra (PAD + sample) to the same total counts.
# This prevents PAD weights from being inflated by arbitrary count-scale differences.
# Both PAD and sample .spc files are normalized so the least-squares fit gives
# meaningful fractional weights instead of scale-driven inflated values.
# Live time is set to 1,000,000 us (=1 second) in normalized files so that
# --normalize-live-time in the Python engine becomes a no-op (divide by 1s).
# This avoids double-normalization issues when PADs and samples have very
# different acquisition times (e.g. PADs at ~600s, samples at ~259us).
NORM_DIR="$JOB_OUTPUT/normalized"
mkdir -p "$NORM_DIR/pads" "$NORM_DIR/samples"
echo "[NORM] Normalizing all spectra to uniform total counts..."
python3 -c "
import numpy as np
from pathlib import Path

target_total = 100000.0  # arbitrary uniform target for all spectra
pad_dir = Path('$PAD_DIR')
sample_dir = Path('$JOB_INCOMING')
norm_pad_dir = Path('$NORM_DIR/pads')
norm_sample_dir = Path('$NORM_DIR/samples')

# Normalize PAD files
for spc in sorted(pad_dir.glob('*.spc')):
    with open(spc) as f:
        lines = [l.rstrip() for l in f]
    live_us = float(lines[0].split()[0]) if lines[0].strip() else 0
    clock_us = float(lines[1].split()[0]) if len(lines) > 1 and lines[1].strip() else 0
    counts = []
    for raw in lines[2:2+1024]:
        try:
            counts.append(float(raw.split()[0]))
        except (ValueError, IndexError):
            counts.append(0.0)
    counts = np.array(counts)
    total = counts.sum()
    scale = target_total / total if total > 0 else 1.0
    norm_counts = counts * scale
    out_path = norm_pad_dir / spc.name
    with open(out_path, 'w') as f:
        f.write(f'1000000\n1000000\n')  # 1s live+clock so --normalize-live-time is no-op
        for c in norm_counts:
            f.write(f'{int(round(c))}\n')
    print(f'  PAD {spc.name}: {int(total):,} -> {int(target_total):,} (scale={scale:.4f})')

# Normalize sample files
for spc in sorted(sample_dir.glob('*.spc')):
    with open(spc) as f:
        lines = [l.rstrip() for l in f]
    live_us = float(lines[0].split()[0]) if lines[0].strip() else 0
    clock_us = float(lines[1].split()[0]) if len(lines) > 1 and lines[1].strip() else 0
    counts = []
    for raw in lines[2:2+1024]:
        try:
            counts.append(float(raw.split()[0]))
        except (ValueError, IndexError):
            counts.append(0.0)
    counts = np.array(counts)
    total = counts.sum()
    scale = target_total / total if total > 0 else 1.0
    norm_counts = counts * scale
    out_path = norm_sample_dir / spc.name
    with open(out_path, 'w') as f:
        f.write(f'1000000\n1000000\n')  # 1s live+clock so --normalize-live-time is no-op
        for c in norm_counts:
            f.write(f'{int(round(c))}\n')
    print(f'  sample {spc.name}: {int(total):,} -> {int(target_total):,} (scale={scale:.4f})')
" 2>&1

PAD_DIR="$NORM_DIR/pads"
JOB_INCOMING="$NORM_DIR/samples"

# Run the Python estimation
echo ""
echo "Running K/U/Th estimation..."
python3 "$PYTHON_SCRIPT" \
    --spectra "$JOB_INCOMING" \
    --pad-dir "$PAD_DIR" \
    --out "$RESULTS_CSV" \
    --roi-half-width-kev "$ROI_HALF_WIDTH" \
    ${NORMALIZE_LT:-}

echo ""
echo "=== Results ==="
echo "CSV: $RESULTS_CSV"
echo ""

# Output summary for Telegram
if [[ -f "$RESULTS_CSV" ]]; then
    N=$(python3 -c "
import csv
with open('$RESULTS_CSV') as f:
    rows = list(csv.DictReader(f))
print(len(rows))
" 2>/dev/null || echo "N")
    echo "--- BEGIN TELEGRAM MESSAGE ---"
    echo "📊 EDGE K/U/Th Portal — Results Ready"
    echo ""
    echo "Job: $JOB_ID"
    echo "Spectra: ${N} files processed"
    echo ""
    python3 -c "
import csv, sys
with open('$RESULTS_CSV') as f:
    rows = list(csv.DictReader(f))
n = len(rows)
if n == 0:
    sys.exit(0)
k = [float(r['K_percent']) for r in rows]
u = [float(r['U_ppm']) for r in rows]
th = [float(r['Th_ppm']) for r in rows]
r2 = [float(r['fit_r2']) for r in rows]
print(f'K:  {min(k):.2f}–{max(k):.2f}%  (avg {sum(k)/n:.2f})')
print(f'U:  {min(u):.1f}–{max(u):.1f} ppm  (avg {sum(u)/n:.1f})')
print(f'Th: {min(th):.1f}–{max(th):.1f} ppm  (avg {sum(th)/n:.1f})')
print(f'R²: {min(r2):.3f}–{max(r2):.3f}')
" 2>/dev/null || true
    echo ""
    echo "Full CSV has been saved. Email delivery pending Brevo sender verification."
    echo ""
    echo "--- END TELEGRAM MESSAGE ---"
else
    echo "[ERROR] No results CSV generated"
    exit 1
fi
