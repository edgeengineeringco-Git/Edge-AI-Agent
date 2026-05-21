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
NORMALIZE_TOTAL=""
PAD_DIR="$SCRIPT_DIR/embedded_pads"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --job-id) JOB_ID="$2"; shift 2 ;;
        --client) CLIENT_NAME="$2"; shift 2 ;;
        --email) EMAIL="$2"; shift 2 ;;
        --roi-half-width) ROI_HALF_WIDTH="$2"; shift 2 ;;
        --normalize-live-time) NORMALIZE_LT="--normalize-live-time"; shift ;;
        --normalize-total-counts) NORMALIZE_TOTAL="yes"; shift ;;
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
echo "ROI half:          $ROI_HALF_WIDTH keV"
echo "Live-time norm:    $([ -n "$NORMALIZE_LT" ] && echo yes || echo no)"
echo "Total-count norm:  ${NORMALIZE_TOTAL:-no}"
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

# Ensure PAD files are available from the embedded data module
# This is the authoritative source — no Drive download, no synthetic fallback.
PAD_DATA_SCRIPT="$SCRIPT_DIR/pad_data.py"
if [[ ! -f "$PAD_DATA_SCRIPT" ]]; then
    PAD_DATA_SCRIPT="$WORKSPACE_ROOT/edge-kuth-portal/pad_data.py"
fi

if [[ ! -d "$PAD_DIR" ]]; then
    echo "[PAD] Generating PAD files from embedded data..."
    python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
sys.path.insert(0, '$WORKSPACE_ROOT/edge-kuth-portal')
from pad_data import ensure_pad_dir, validate_pad_dir
ensure_pad_dir('$PAD_DIR')
print('PAD files written to $PAD_DIR')
" 2>&1
fi

# Validate PAD files — exit on failure
if [[ -d "$PAD_DIR" ]]; then
    echo "[PAD] Validating PAD files..."
    python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
sys.path.insert(0, '$WORKSPACE_ROOT/edge-kuth-portal')
from pad_data import validate_pad_dir
validate_pad_dir('$PAD_DIR')
print('PAD validation OK')
" 2>&1 || { echo "[ERROR] PAD validation failed"; exit 1; }
else
    echo "[ERROR] PAD directory not found and could not be created: $PAD_DIR"
    exit 1
fi

# ── Preprocessing mode ──────────────────────────────────────────────────────
# Three independent modes, controlled by CLI flags:
#   neither flag set       = raw counts (no modification to PADs or samples)
#   --normalize-live-time  = Python divides counts by live time (counts/s)
#   --normalize-total-counts = Bash rescales all spectra to 100k total counts
#
# When --normalize-total-counts is set, live_time is written as 1,000,000 us
# in the normalized headers, making --normalize-live-time a no-op if both
# flags are set (division by 1s).
#
# PADs and samples always use identical preprocessing.

PROVENANCE_NOTES=()
PROVENANCE_NOTES+=("PAD_source:embedded_pad_data.py")

if [[ -n "$NORMALIZE_TOTAL" ]]; then
    PROVENANCE_NOTES+=("total_count_normalized:100k")
    NORM_DIR="$JOB_OUTPUT/normalized"
    mkdir -p "$NORM_DIR/pads" "$NORM_DIR/samples"
    echo "[NORM] Normalizing all spectra to uniform total counts..."
    python3 -c "
import numpy as np
from pathlib import Path

target_total = 100000.0
pad_dir = Path('$PAD_DIR')
sample_dir = Path('$JOB_INCOMING')
norm_pad_dir = Path('$NORM_DIR/pads')
norm_sample_dir = Path('$NORM_DIR/samples')

for spc in sorted(pad_dir.glob('*.spc')):
    with open(spc) as f:
        lines = [l.rstrip() for l in f]
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
        f.write('1000000\n1000000\n')
        for c in norm_counts:
            f.write(f'{int(round(c))}\n')
    print(f'  PAD {spc.name}: {int(total):,} -> {int(target_total):,} (scale={scale:.4f})')

for spc in sorted(sample_dir.glob('*.spc')):
    with open(spc) as f:
        lines = [l.rstrip() for l in f]
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
        f.write('1000000\n1000000\n')
        for c in norm_counts:
            f.write(f'{int(round(c))}\n')
    print(f'  sample {spc.name}: {int(total):,} -> {int(target_total):,} (scale={scale:.4f})')
" 2>&1

    PAD_DIR="$NORM_DIR/pads"
    JOB_INCOMING="$NORM_DIR/samples"
else
    echo "[NORM] Using raw counts (no total-count normalization)"
    PROVENANCE_NOTES+=("total_count_normalized:no")
fi

if [[ -n "$NORMALIZE_LT" ]]; then
    PROVENANCE_NOTES+=("live_time_normalized:yes")
else
    PROVENANCE_NOTES+=("live_time_normalized:no")
fi

PROVENANCE_NOTES+=("roi_half_width_kev:${ROI_HALF_WIDTH}")
PROVENANCE_NOTES+=("engine:estimate_k_u_th_matrix.py")
# ── Pre-estimation diagnostic snapshot ─────────────────────────────────────
# Save energy calibration, M_ref, and first-sample stats to estimation-debug.json
# for post-mortem analysis of bad results.
DEBUG_JSON="$JOB_OUTPUT/estimation-debug.json"
python3 -c "
import numpy as np, json, sys, glob
def _rsc(p):
    with open(p) as f:
        lines = [l.rstrip(chr(92)+"n") for l in f]
    c = []
    for raw in lines[2:2+1024]:
        try: c.append(float(raw.split()[0]))
        except: c.append(0.0)
    return np.array(c, dtype=float)
def _rsl(p):
    with open(p) as f: line = f.readline().strip()
    try: return float(line.split()[0])
    except: return None
anchors_ch = np.array([870.5, 720.8, 31.6, 484.0])
anchors_kv = np.array([2611.4, 2162.3, 94.8, 1451.9])
A = np.vstack([np.ones_like(anchors_ch), anchors_ch, anchors_ch**2]).T
c0, c1, c2 = np.linalg.lstsq(A, anchors_kv, rcond=None)[0]
pd = "$PAD_DIR"
pk = _rsc(pd+"/PAD_K_A.spc"); pu = _rsc(pd+"/PAD_U_A.spc"); pth = _rsc(pd+"/PAD_Th_A.spc")
ch = np.arange(1024.0); en = c0 + c1*ch + c2*ch**2
hw = float("$ROI_HALF_WIDTH")
RL = {"K":[1460.8],"U":[351.9,609.3,1120.3,1764.5],"Th":[583.2,911.1,968.9,2614.5]}
def _roi(co, ll, hw):
    return [float(co[(en>=e0-hw)&(en<=e0+hw)].sum()) for e0 in ll]
labels = ["K_1460","U_351","U_609","U_1120","U_1764","Th_583","Th_911","Th_968","Th_2614"]
fk = _roi(pk, RL["K"],hw)+_roi(pk, RL["U"],hw)+_roi(pk, RL["Th"],hw)
fu = _roi(pu, RL["K"],hw)+_roi(pu, RL["U"],hw)+_roi(pu, RL["Th"],hw)
fth = _roi(pth, RL["K"],hw)+_roi(pth, RL["U"],hw)+_roi(pth, RL["Th"],hw)
mrt = [[fk[i],fu[i],fth[i]] for i in range(9)]
M = np.column_stack([fk, fu, fth])
yk = np.array(fk+fu+fth)
w,_,_,_ = np.linalg.lstsq(M, yk, rcond=None); w = np.maximum(w,0)
yp = (M @ w).tolist(); ssr = sum((yk-yp)**2); sst = sum((yk-np.mean(yk))**2)
spfs = sorted(glob.glob("$JOB_INCOMING/*.spc"))
fs = _rsc(spfs[0]).tolist() if spfs else None
flt = _rsl(spfs[0]) if spfs else None
info = {
    "energy_cal": {"c0":f"{c0:.4f}","c1":f"{c1:.4f}","c2":f"{c2:.6f}"},
    "pad_live_times_us": {"K":_rsl(pd+"/PAD_K_A.spc"),"U":_rsl(pd+"/PAD_U_A.spc"),"Th":_rsl(pd+"/PAD_Th_A.spc")},
    "pad_total_counts": {"K":int(pk.sum()),"U":int(pu.sum()),"Th":int(pth.sum())},
    "m_ref": {labels[i]:mrt[i] for i in range(9)},
    "pad_k_self_r2": float(1.0-ssr/sst if sst>0 else 1.0),
    "pad_k_self_weights": [float(f"{v:.6f}") for v in w],
    "first_sample": str(spfs[0]) if spfs else None,
    "first_sample_live_time_us": flt,
    "first_sample_total_counts": int(sum(fs)) if fs else None,
    "first_sample_nonzero_ch": sum(1 for c in (fs or []) if c>0),
    "numpy_version": np.__version__,
}
with open("$DEBUG_JSON","w") as f: json.dump(info, f, indent=2)
print("[DEBUG] Estimation debug snapshot → " + "$DEBUG_JSON")
" 2>&1 || echo "[WARN] Debug snapshot failed (non-fatal)"

# Run the Python estimation
echo ""
echo "Running K/U/Th estimation..."
python3 "$PYTHON_SCRIPT" \
    --spectra "$JOB_INCOMING" \
    --pad-dir "$PAD_DIR" \
    --out "$RESULTS_CSV" \
    --roi-half-width-kev "$ROI_HALF_WIDTH" \
    ${NORMALIZE_LT:-}

# ── Post-estimation validation ──────────────────────────────────────────────
# Check results are physically plausible before sending Telegram.
VALIDATION_WARN=""
if [[ -f "$RESULTS_CSV" ]]; then
    VALIDATION_WARN=$(python3 -c "
import csv, sys
with open("'$RESULTS_CSV'") as f:
    rows = list(csv.DictReader(f))
n = len(rows)
if n == 0: print("EMPTY_CSV"); sys.exit(0)
k = [float(r["K_percent"]) for r in rows]
u = [float(r["U_ppm"]) for r in rows]
th = [float(r["Th_ppm"]) for r in rows]
r2 = [float(r["fit_r2"]) for r in rows]
mk = max(k); mu = max(u); mt = max(th); mr = min(r2)
w = []
if mk > 20: w.append(f"MAX_K={mk:.1f}%")
if mu > 100: w.append(f"MAX_U={mu:.0f}ppm")
if mt > 200: w.append(f"MAX_Th={mt:.0f}ppm")
if mr < 0: w.append(f"NEG_R2={mr:.3f}")
elif mr < 0.5: w.append(f"LOW_R2={mr:.3f}")
print("|".join(w) if w else "OK")
" 2>/dev/null || echo "VAL_FAIL")
    case "$VALIDATION_WARN" in
        EMPTY_CSV) echo "[VAL] WARNING: Empty results CSV" ;;
        VAL_FAIL)  echo "[VAL] WARNING: Could not validate" ;;
        OK)        echo "[VAL] Results pass plausibility checks" ;;
        *)         echo "[VAL] WARNING: Suspicious results: $VALIDATION_WARN"
                     echo "[VAL] Debug data at: $DEBUG_JSON" ;;
    esac
fi

# Write processing metadata
META_JSON="$JOB_OUTPUT/processing-metadata.json"
python3 -c "
import json
notes = [l for l in '''$(printf "%s\n" "${PROVENANCE_NOTES[@]}")'''.strip().split('\n') if l]
meta = {}
for n in notes:
    if ':' in n:
        k, v = n.split(':', 1)
        meta[k] = v
meta['job_id'] = '$JOB_ID'
meta['client_name'] = '${CLIENT_NAME:-anonymous}'
meta['email'] = '${EMAIL:-none}'
meta['total_count_normalized'] = '${NORMALIZE_TOTAL:+yes}' or 'no'
meta['live_time_normalized'] = '${NORMALIZE_LT:+yes}' or 'no'
with open('$META_JSON', 'w') as f:
    json.dump(meta, f, indent=2)
print(f'[META] Processing metadata written to $META_JSON')
" 2>&1 || true

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
    MODE_LINE=$(IFS=,; echo "${PROVENANCE_NOTES[*]}")
    echo "Mode: $MODE_LINE"
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
	    if [[ -n "$VALIDATION_WARN" && "$VALIDATION_WARN" != "OK" && "$VALIDATION_WARN" != "VAL_FAIL" && "$VALIDATION_WARN" != "EMPTY_CSV" ]]; then
	        echo "⚠️  WARNING: Results may be unreliable — $VALIDATION_WARN"
	        echo ""
	    fi
	    echo ""
    echo "Full CSV has been saved. Email delivery pending Brevo sender verification."
    echo ""
    echo "--- END TELEGRAM MESSAGE ---"
else
    echo "[ERROR] No results CSV generated"
    exit 1
fi
