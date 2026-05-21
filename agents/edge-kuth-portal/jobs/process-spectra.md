# K/U/Th Spectra — Immediate Processing Pipeline

Process gamma-ray .spc spectrum files **immediately** upon receipt. Do not wait for batch cycles.

## Trigger

This job runs when a client submits the upload form. The webhook payload contains:

| Field | Description |
|-------|-------------|
| `job_id` | Unique job identifier (e.g., `client_20260518_143000`) |
| `client_name` | Client or project name |
| `email` | Client email address |
| `project` | Project name from form |
| `roi_half_width` | ROI half-width in keV (default: 20) |
| `normalize_live_time` | Whether to normalize counts by live time |
| `measurement_id_column` | Column name for measurement IDs in dose CSV |
| `spectra_files` | Array of uploaded .spc filenames |
| `dose_csv_file` | Uploaded dose CSV filename (or null) |

## Execution Steps (Execute All Immediately)

### Step 1: Verify Job Directory and Files
The upload server already created the job directory with .spc files. Verify they exist:

```bash
ls ../../edge-kuth-portal/jobs/{job_id}/spectra/*.spc
```

If no .spc files found, stop and notify via Telegram broadcast.

The webhook payload is at `../../edge-kuth-portal/jobs/{job_id}/webhook-payload.json` (created by upload server).

### Step 2: Ensure PAD Reference Files
PAD files (PAD_K_A.spc, PAD_U_A.spc, PAD_Th_A.spc) are embedded in `../../edge-kuth-portal/pad_data.py` as the authoritative source.

The `handle-upload.sh` script automatically generates PAD files from this module on first run. Processing stops with an error if PAD generation or validation fails — no synthetic fallback, no Drive download for PADs.

To explicitly regenerate from embedded data:
```bash
python3 -c "
from pad_data import ensure_pad_dir, validate_pad_dir
ensure_pad_dir('../../edge-kuth-portal/pad_drive')
validate_pad_dir('../../edge-kuth-portal/pad_drive')
"
```

### Step 3: Install numpy if needed
```bash
python3 -m pip install numpy 2>/dev/null || true
```

### Step 4: Run Estimation Immediately
Read the webhook payload flags and pass the corresponding CLI flags:

| Form field | CLI flag | Effect |
|-----------|----------|--------|
| `normalize_live_time` | `--normalize-live-time` | Python divides counts by live time (counts/s) |

When `--normalize-live-time` is not set, **raw counts** are used with no preprocessing.

```bash
# Build flags from webhook payload
NORM_LT_FLAG=""
if python3 -c "import json; d=json.load(open('../../edge-kuth-portal/jobs/{job_id}/webhook-payload.json')); exit(0 if d.get('normalize_live_time') else 1)" 2>/dev/null; then
  NORM_LT_FLAG="--normalize-live-time"
fi

bash ../../edge-kuth-portal/handle-upload.sh \
  --job-id {job_id} \
  --client {client_name} \
  --email {email} \
  --roi-half-width {roi_half_width} \
  $NORM_LT_FLAG
```

### Step 5: Read Results
Results CSV at: `../../edge-kuth-portal/jobs/{job_id}/results.csv`
Columns: `file, [lat, lon, [elevation,]] K_percent, U_ppm, Th_ppm, w_PADK, w_PADU, w_PADTh, fit_r2`

Processing metadata at: `../../edge-kuth-portal/jobs/{job_id}/processing-metadata.json`

R² is included for every spectrum — no review or filtering, include everything.

### Step 6: Email Results CSV to Client
Send the results CSV to the client's email address via SendGrid.

The upload server already sent a confirmation email — this is the follow-up with actual results.

```bash
# Read CSV to build summary stats
SUMMARY=$(python3 -c "
import csv
with open('../../edge-kuth-portal/jobs/{job_id}/results.csv') as f:
    rows = list(csv.DictReader(f))
n = len(rows)
k = [float(r['K_percent']) for r in rows]
u = [float(r['U_ppm']) for r in rows]
th = [float(r['Th_ppm']) for r in rows]
r2 = [float(r['fit_r2']) for r in rows]
print(f'{n} files processed')
print(f'K:  {min(k):.2f}-{max(k):.2f}%  (avg {sum(k)/n:.2f})')
print(f'U:  {min(u):.1f}-{max(u):.1f} ppm  (avg {sum(u)/n:.1f})')
print(f'Th: {min(th):.1f}-{max(th):.1f} ppm  (avg {sum(th)/n:.1f})')
print(f'R²: {min(r2):.3f}-{max(r2):.3f}')
" 2>/dev/null || echo "Results available"
)

EMAIL_BODY="Dear Client,

Your K/U/Th analysis is complete.

  Job ID:   {job_id}
  Project:  {client_name}

$SUMMARY

The full results CSV is attached to this email.

Best regards,
EDGE Geointelligence"

# Send with CSV attachment
bash ../../edge-kuth-portal/send-email.sh \
  --to "{email}" \
  --subject "EDGE K/U/Th Portal — Results Ready ({job_id})" \
  --body "$EMAIL_BODY" \
  --attach ../../edge-kuth-portal/jobs/{job_id}/results.csv
```

If `SENDGRID_API_KEY` is not configured, this step skips gracefully.

### Step 7: Google Drive Integration (execute fully if configured)
Use the `drive-utils.sh` helper. PAD files come from the embedded `pad_data.py` module — no Drive download needed. Results upload and job logging use Drive if configured.

```bash
# Get OAuth token from agent-job-secrets
CREDENTIALS=$(node skills/agent-job-secrets/agent-job-secrets.js get GOOGLE_DRIVE_OAUTH 2>/dev/null || echo "")
if [[ -z "$CREDENTIALS" ]]; then
  echo "Google Drive not configured — skipping"
else
  # Parse token
  GDRIVE_TOKEN=$(echo "$CREDENTIALS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)
  export GDRIVE_TOKEN

  # 7a. Upload results CSV to Drive job folder
  READS=$(bash ../../edge-kuth-portal/drive-utils.sh upload-results \
    --job-id {job_id} \
    --csv ../../edge-kuth-portal/jobs/{job_id}/results.csv \
    --client {client_name})
  FOLDER_ID=$(echo "$READS" | awk '{print $1}')
  CSV_LINK=$(echo "$READS" | awk '{print $2}')

  # 7b. Log job details to spreadsheet (Google Sheets)
  bash ../../edge-kuth-portal/drive-utils.sh log-job \
    --job-id {job_id} \
    --client {client_name} \
    --drive-folder "$FOLDER_ID" \
    --result-link "$CSV_LINK" \
    --status "complete"
fi
```

**Google Drive resources (hardcoded):**
- PAD folder: `1Eg04frfuGOFYbtqd-o4IMCpOaW6xoNc4`
- Jobs folder: `1INUTv6WYdmhRLKpNZlEX5L8Zmdw6Rx8d`
- Log spreadsheet: `1vV3mjhTcjFt0kf4Tk0ovDcL_NtrzyGxDtmFf6wv9iQ8` (tab GID: `2138085800`)

### Step 8: Send Results via Telegram
Use the `agent-job-dm` skill (`--broadcast` flag) to send the results to all admins.

Send only the message from the handle-upload.sh output between the BEGIN/END TELEGRAM MESSAGE markers. Do NOT include any per-file details, CSV content, or additional commentary.

The output will look like:
```
📊 EDGE K/U/Th Portal — Results Ready

Job: {job_id}
Spectra: {N} files processed
Mode: PAD_source:embedded_pad_data.py,live_time_normalized:no,roi_half_width_kev:20,engine:estimate_k_u_th_matrix.py

K:  0.00–1.84%  (avg 1.42)
U:  0.0–19.7 ppm  (avg 15.5)
Th: 0.0–32.2 ppm  (avg 24.5)
R²: 0.917–1.000

Full CSV has been saved. Email delivery pending Brevo sender verification.
```

### Step 9: Archive
```bash
cp ../../edge-kuth-portal/jobs/{job_id}/results.csv ../../edge-kuth-portal/output/{job_id}_results.csv
```

## Notes
- All results are kept — no R² filtering or quality review
- The CSV includes fit_r2 per row as requested
- Location data (lat, lon, elevation) from .spc file metadata is included when available
- Google Drive integration: the PAD reference files and results can use Drive if configured. If not configured, local files are used and results go only via Telegram
