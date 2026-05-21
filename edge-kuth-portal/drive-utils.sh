#!/bin/bash
# EDGE K/U/Th Portal — Google Drive & Sheets Utilities
#
# Usage:
#   export GDRIVE_TOKEN="<oauth-access-token>"
#   bash drive-utils.sh download-pads [--output-dir <path>]
#   bash drive-utils.sh upload-results --job-id <id> --csv <path> [--client <name>]
#   bash drive-utils.sh log-job --job-id <id> --client <name> --email <email> --files <n> --status <text> [--csv-link <url>]
#
# Dependencies: curl, jq (optional but recommended)
# Authentication: Get token via: node skills/agent-job-secrets/agent-job-secrets.js get GOOGLE_DRIVE_CREDENTIALS
#   Then export GDRIVE_TOKEN from the access_token field in the JSON response.
#
# Google Drive Folder IDs (hardcoded per user specification):
#   PAD_FOLDER_ID  = 1Eg04frfuGOFYbtqd-o4IMCpOaW6xoNc4  — calibration PAD spectra
#   JOBS_FOLDER_ID = 1INUTv6WYdmhRLKpNZlEX5L8Zmdw6Rx8d  — job results storage
#   SHEET_ID       = 1vV3mjhTcjFt0kf4Tk0ovDcL_NtrzyGxDtmFf6wv9iQ8  — job log spreadsheet

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Google Drive folder IDs (from user specification)
PAD_FOLDER_ID="1Eg04frfuGOFYbtqd-o4IMCpOaW6xoNc4"
JOBS_FOLDER_ID="1INUTv6WYdmhRLKpNZlEX5L8Zmdw6Rx8d"
SHEET_ID="1vV3mjhTcjFt0kf4Tk0ovDcL_NtrzyGxDtmFf6wv9iQ8"
SHEET_GID="2138085800"  # sheet tab ID for the job log

# ── Help ──────────────────────────────────────────────────────────────────────

usage() {
  sed -n '/^# Usage:/,/^$/p' "$0" | head -n -1 | sed 's/^# //'
  exit 1
}

# ── Auth check ────────────────────────────────────────────────────────────────

check_auth() {
  if [[ -z "${GDRIVE_TOKEN:-}" ]]; then
    echo "[ERROR] GDRIVE_TOKEN is not set."
    echo "  Run: node skills/agent-job-secrets/agent-job-secrets.js get GOOGLE_DRIVE_CREDENTIALS"
    echo "  Then: export GDRIVE_TOKEN=\"<access_token>\""
    exit 1
  fi
}

# ── Resolve sheet tab name from gid ──────────────────────────────────────────

get_sheet_name() {
  local sheet_id="$1"
  local target_gid="$2"
  local metadata
  metadata=$(curl -s \
    "https://sheets.googleapis.com/v4/spreadsheets/${sheet_id}?fields=sheets.properties" \
    -H "Authorization: Bearer ${GDRIVE_TOKEN}")

  # Try jq first, fallback to grep/json parsing
  if command -v jq &>/dev/null; then
    echo "$metadata" | jq -r \
      --argjson gid "$target_gid" \
      '.sheets[] | select(.properties.sheetId == $gid) | .properties.title'
  else
    # Manual parse without jq — fragile but works for simple cases
    echo "$metadata" | grep -oP '"sheetId":\s*'"$target_gid"',\s*"title":\s*"[^"]*"' | \
      grep -oP '"title":\s*"\K[^"]+'
  fi
}

# ── Download PAD files from Drive ─────────────────────────────────────────────
# Known PAD files: PAD_K_A.spc, PAD_U_A.spc, PAD_Th_A.spc

cmd_download_pads() {
  check_auth

  local output_dir="${1:-$SCRIPT_DIR/pad_reference}"
  mkdir -p "$output_dir"

  echo "=== Downloading PAD reference spectra ==="
  echo "Output dir: $output_dir"

  # List files in PAD folder
  local files_json
  files_json=$(curl -s \
    "https://www.googleapis.com/drive/v3/files?q='${PAD_FOLDER_ID}'+in+parents&fields=files(id,name,mimeType)&pageSize=100" \
    -H "Authorization: Bearer ${GDRIVE_TOKEN}")

  # Parse file IDs and names
  local file_ids file_names
  if command -v jq &>/dev/null; then
    file_ids=($(echo "$files_json" | jq -r '.files[]? | .id'))
    file_names=($(echo "$files_json" | jq -r '.files[]? | .name'))
  else
    echo "[WARN] jq not available, using grep-based parsing"
    file_ids=($(echo "$files_json" | grep -oP '"id":\s*"\K[^"]+'))
    file_names=($(echo "$files_json" | grep -oP '"name":\s*"\K[^"]+'))
  fi

  if [[ ${#file_ids[@]} -eq 0 ]]; then
    echo "[ERROR] No files found in PAD folder (ID: $PAD_FOLDER_ID)"
    echo "  Response: $files_json"
    return 1
  fi

  echo "Found ${#file_ids[@]} file(s) in PAD folder"

  local downloaded=0
  for i in "${!file_ids[@]}"; do
    local fid="${file_ids[$i]}"
    local fname="${file_names[$i]}"
    local dest="$output_dir/$fname"

    echo "  Downloading: $fname"
    curl -s "https://www.googleapis.com/drive/v3/files/${fid}?alt=media" \
      -H "Authorization: Bearer ${GDRIVE_TOKEN}" \
      -o "$dest"

    if [[ -f "$dest" && -s "$dest" ]]; then
      echo "    -> Saved ($(wc -c < "$dest") bytes)"
      ((downloaded++))
    else
      echo "    [ERROR] Failed to download $fname"
    fi
  done

  echo "Downloaded $downloaded/${#file_ids[@]} PAD files"
  [[ "$downloaded" -gt 0 ]] || return 1
}

# ── Create job folder in Drive ────────────────────────────────────────────────

create_job_folder() {
  local job_id="$1"

  echo "Creating job folder: $job_id"

  local folder_json
  folder_json=$(curl -s -X POST \
    "https://www.googleapis.com/drive/v3/files?fields=id" \
    -H "Authorization: Bearer ${GDRIVE_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$(cat <<EOF
{
  "name": "$job_id",
  "mimeType": "application/vnd.google-apps.folder",
  "parents": ["$JOBS_FOLDER_ID"]
}
EOF
)")

  local folder_id
  if command -v jq &>/dev/null; then
    folder_id=$(echo "$folder_json" | jq -r '.id // empty')
  else
    folder_id=$(echo "$folder_json" | grep -oP '"id":\s*"\K[^"]+')
  fi

  if [[ -z "$folder_id" ]]; then
    echo "[ERROR] Failed to create job folder: $folder_json"
    return 1
  fi

  echo "$folder_id"
  return 0
}

# ── Upload a file to Drive ────────────────────────────────────────────────────

upload_file() {
  local file_path="$1"
  local parent_folder_id="$2"
  local file_name="${3:-$(basename "$file_path")}"

  if [[ ! -f "$file_path" ]]; then
    echo "[ERROR] File not found: $file_path"
    return 1
  fi

  echo "Uploading: $file_name"

  # Upload with metadata for folder placement
  local response
  response=$(curl -s -X POST \
    "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,webViewLink" \
    -H "Authorization: Bearer ${GDRIVE_TOKEN}" \
    -F "metadata={\"name\":\"$file_name\",\"parents\":[\"$parent_folder_id\"]};type=application/json;charset=UTF-8" \
    -F "media=@$file_path")

  local file_id file_link
  if command -v jq &>/dev/null; then
    file_id=$(echo "$response" | jq -r '.id // empty')
    file_link=$(echo "$response" | jq -r '.webViewLink // empty')
  else
    file_id=$(echo "$response" | grep -oP '"id":\s*"\K[^"]+')
    file_link=$(echo "$response" | grep -oP '"webViewLink":\s*"\K[^"]+')
  fi

  if [[ -z "$file_id" ]]; then
    echo "[ERROR] Upload failed: $response"
    return 1
  fi

  echo "  Uploaded: fileId=$file_id"
  echo "  Link: $file_link"
  echo "$file_link"
  return 0
}

# ── Upload results CSV to Drive ───────────────────────────────────────────────

cmd_upload_results() {
  check_auth

  local job_id="" csv_path="" client_name=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --job-id) job_id="$2"; shift 2 ;;
      --csv) csv_path="$2"; shift 2 ;;
      --client) client_name="$2"; shift 2 ;;
      *) echo "Unknown: $1"; usage ;;
    esac
  done

  if [[ -z "$job_id" || -z "$csv_path" ]]; then
    echo "[ERROR] --job-id and --csv are required"
    usage
  fi

  echo "=== Uploading Results to Google Drive ==="
  echo "Job: $job_id"

  # Create job folder
  local folder_id
  folder_id=$(create_job_folder "$job_id")
  if [[ -z "$folder_id" ]]; then
    echo "[ERROR] Could not create job folder. Results not uploaded."
    return 1
  fi
  echo "Job folder ID: $folder_id"

  # Upload results CSV
  local csv_link
  csv_link=$(upload_file "$csv_path" "$folder_id" "${job_id}_results.csv") || true

  # Upload webhook metadata if available
  local webhook_meta="$SCRIPT_DIR/jobs/$job_id/webhook-payload.json"
  if [[ -f "$webhook_meta" ]]; then
    upload_file "$webhook_meta" "$folder_id" "${job_id}_metadata.json" >/dev/null || true
  fi

  echo "Results uploaded to Drive job folder"
  echo "$csv_link"
  return 0
}

# ── Log job details to Google Sheets ──────────────────────────────────────────

cmd_log_job() {
  check_auth

  local job_id="" client_name="" email="" files_count="" status="" csv_link=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --job-id) job_id="$2"; shift 2 ;;
      --client) client_name="$2"; shift 2 ;;
      --email) email="$2"; shift 2 ;;
      --files) files_count="$2"; shift 2 ;;
      --status) status="$2"; shift 2 ;;
      --csv-link) csv_link="$2"; shift 2 ;;
      *) echo "Unknown: $1"; usage ;;
    esac
  done

  if [[ -z "$job_id" || -z "$client_name" ]]; then
    echo "[ERROR] --job-id and --client are required"
    usage
  fi

  echo "=== Logging Job to Google Sheets ==="

  # Resolve sheet tab name from GID
  local sheet_name
  sheet_name=$(get_sheet_name "$SHEET_ID" "$SHEET_GID")
  if [[ -z "$sheet_name" ]]; then
    echo "[WARN] Could not resolve sheet tab for GID $SHEET_GID, using 'Sheet1'"
    sheet_name="Sheet1"
  fi
  echo "Sheet tab: $sheet_name"

  local timestamp
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  # Build row values (timestamp, job_id, client, email, files, status, csv_link)
  local row_values="[\"$timestamp\",\"$job_id\",\"$client_name\",\"$email\",\"$files_count\",\"$status\",\"$csv_link\"]"

  local append_response
  append_response=$(curl -s -X POST \
    "https://sheets.googleapis.com/v4/spreadsheets/${SHEET_ID}/values/${sheet_name}!A:G:append?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS" \
    -H "Authorization: Bearer ${GDRIVE_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{\"values\":[$row_values]}")

  local updates
  if command -v jq &>/dev/null; then
    updates=$(echo "$append_response" | jq -r '.updates.updatedRange // "failed"')
  else
    updates=$(echo "$append_response" | grep -oP '"updatedRange":\s*"\K[^"]+' || echo "failed")
  fi

  if [[ "$updates" != "failed" ]]; then
    echo "Logged to spreadsheet: $updates"
  else
    echo "[WARN] Spreadsheet append result: $append_response"
  fi

  return 0
}

# ── Main dispatch ─────────────────────────────────────────────────────────────

main() {
  if [[ $# -lt 1 ]]; then
    usage
  fi

  local cmd="$1"
  shift

  case "$cmd" in
    download-pads)
      local output_dir=""
      while [[ $# -gt 0 ]]; do
        case "$1" in
          --output-dir) output_dir="$2"; shift 2 ;;
          *) echo "Unknown: $1"; usage ;;
        esac
      done
      cmd_download_pads "${output_dir:-$SCRIPT_DIR/pad_reference}"
      ;;
    upload-results)
      cmd_upload_results "$@"
      ;;
    log-job)
      cmd_log_job "$@"
      ;;
    *)
      usage
      ;;
  esac
}

main "$@"
