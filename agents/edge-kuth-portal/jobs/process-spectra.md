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
The upload server already created the job directory with .spc files on the host at `/project/edge-kuth-portal/jobs/{job_id}/`. This workspace has `/project` mounted so host files are accessible. First, ensure files are available in the workspace:

```bash
# Copy files from host path if not already in workspace
if [ ! -f "../../edge-kuth-portal/jobs/{job_id}/webhook-payload.json" ]; then
  echo "Job directory not found in workspace — copying from host path..."
  mkdir -p ../../edge-kuth-portal/jobs/{job_id}
  cp -r /project/edge-kuth-portal/jobs/{job_id}/* ../../edge-kuth-portal/jobs/{job_id}/
fi
```

Then verify the .spc files exist:

```bash
if ls ../../edge-kuth-portal/jobs/{job_id}/spectra/*.spc 2>/dev/null; then
  echo "Files found in workspace"
else
  echo "Files not found in workspace — trying Docker host fallback..."
  # The workspace is isolated from the host filesystem where the upload server saves files.
  # Try copying via the event-handler container (has full project mount at /project).
  if [ -S /var/run/docker.sock ]; then
    WORKSPACE_NAME=$(cd ../../edge-kuth-portal && pwd -P | awk -F/ '{print $(NF-2)}')
    EXEC_ID=$(curl -s --unix-socket /var/run/docker.sock \
      -X POST http://localhost/containers/thepopebot-event-handler/exec \
      -H "Content-Type: application/json" \
      -d '{"Cmd":["/bin/sh","-c","cp -a /project/edge-kuth-portal/jobs/'"${job_id}"' /project/data/workspaces/'"${WORKSPACE_NAME}"'/workspace/edge-kuth-portal/jobs/"],"AttachStdout":true,"AttachStderr":true}' | python3 -c "import sys,json; print(json.load(sys.stdin).get('Id',''))" 2>/dev/null)
    if [ -n "$EXEC_ID" ]; then
      curl -s --unix-socket /var/run/docker.sock \
        -X POST "http://localhost/exec/$EXEC_ID/start" \
        -H "Content-Type: application/json" \
        -d '{"Detach":false,"Tty":false}' >/dev/null 2>&1
      echo "Files copied from host"
    fi
  fi
  ls ../../edge-kuth-portal/jobs/{job_id}/spectra/*.spc || {
    echo "ERROR: No .spc files found in job directory. The upload server may not have saved them."
    exit 1
  }
fi
```

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
Columns: `file, latitude, longitude, elevation, K_percent, U_ppm, Th_ppm, w_PADK, w_PADU, w_PADTh, fit_r2`

Location (lat/lon/elev) is extracted from the 3 lines before the footer of each .spc file. Missing values are blank.

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
# Get OAuth credentials from agent-job-secrets
# Note: GOOGLE_DRIVE_OAUTH returns refresh credentials (client_id, client_secret, refresh_token),
# not an access_token directly. Must exchange refresh token for a fresh access token.
CREDENTIALS=$(node skills/agent-job-secrets/agent-job-secrets.js get GOOGLE_DRIVE_OAUTH 2>/dev/null || echo "")
if [[ -z "$CREDENTIALS" ]]; then
  echo "Google Drive not configured — skipping"
else
	  # Exchange OAuth refresh credentials for an access token
	  CLIENT_ID=$(echo "$CREDENTIALS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('client_id',''))")
	  CLIENT_SECRET=$(echo "$CREDENTIALS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('client_secret',''))")
	  REFRESH_TOKEN=$(echo "$CREDENTIALS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('refresh_token',''))")
	  TOKEN_URI=$(echo "$CREDENTIALS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('token_uri','https://oauth2.googleapis.com/token'))")
	  if [[ -z "$REFRESH_TOKEN" || -z "$CLIENT_ID" || -z "$CLIENT_SECRET" ]]; then
	    echo "Google Drive OAuth credentials incomplete — skipping Drive steps"
	  else
	    GDRIVE_TOKEN=$(curl -s -X POST "$TOKEN_URI" \
	      -d "client_id=$CLIENT_ID" \
	      -d "client_secret=$CLIENT_SECRET" \
	      -d "refresh_token=$REFRESH_TOKEN" \
	      -d "grant_type=refresh_token" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))")
	    if [[ -z "$GDRIVE_TOKEN" ]]; then
	      echo "Google Drive token exchange failed — skipping Drive steps"
	    else
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
