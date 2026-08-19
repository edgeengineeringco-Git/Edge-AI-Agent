#!/usr/bin/env bash
# Gamma–Flight Join Portal — Google Drive helper
#
# Creates a per-job subfolder inside the project Drive folder and uploads
# the job's output files into it. Uses OAuth refresh-token auth (the same
# GOOGLE_DRIVE_OAUTH secret used across this thepopebot instance).
#
# Usage:
#   export GOOGLE_DRIVE_OAUTH='{"client_id":..,"client_secret":..,"refresh_token":..}'
#   drive_utils.sh create-folder --name <job_name> [--parent <folder_id>]
#       -> prints the new folder id on the last stdout line
#   drive_utils.sh upload --file <path> --folder <folder_id> [--mime <type>]
#       -> prints "<file_id> <webViewLink>" on the last stdout line
#   drive_utils.sh list-jobs [--parent <folder_id>]
#       -> prints one TSV line per pending job: <folder_id>\t<folder_name>
#          (a job is pending when its folder has job-manifest.json but no *_summary.json)
#   drive_utils.sh download --folder <folder_id> --name <filename> --out <path>
#       -> downloads the named file from the folder to <path>
#   drive_utils.sh delete --folder <folder_id> --name <filename>
#       -> deletes the named file from the folder (skips gracefully if not found)
#
# The default parent folder is the project folder supplied by the user:
#   https://drive.google.com/drive/folders/18fSXEOVp8D039BUXWMiYrPuIeIXOxgt3

set -euo pipefail

# Project Drive folder (per user specification)
DEFAULT_PARENT_FOLDER_ID="18fSXEOVp8D039BUXWMiYrPuIeIXOxgt3"

TOKEN_URI="https://oauth2.googleapis.com/token"

die() { echo "[ERROR] $*" >&2; exit 1; }

get_access_token() {
  [[ -n "${GOOGLE_DRIVE_OAUTH:-}" ]] || die "GOOGLE_DRIVE_OAUTH env var not set."

  local cid cs rt uri
  cid=$(printf '%s' "$GOOGLE_DRIVE_OAUTH" | python3 -c "import sys,json;print(json.load(sys.stdin).get('client_id',''))" 2>/dev/null || echo "")
  cs=$(printf '%s' "$GOOGLE_DRIVE_OAUTH" | python3 -c "import sys,json;print(json.load(sys.stdin).get('client_secret',''))" 2>/dev/null || echo "")
  rt=$(printf '%s' "$GOOGLE_DRIVE_OAUTH" | python3 -c "import sys,json;print(json.load(sys.stdin).get('refresh_token',''))" 2>/dev/null || echo "")
  uri=$(printf '%s' "$GOOGLE_DRIVE_OAUTH" | python3 -c "import sys,json;print(json.load(sys.stdin).get('token_uri','$TOKEN_URI'))" 2>/dev/null || echo "$TOKEN_URI")

  # Fall back to an already-issued access_token if refresh fields are absent.
  if [[ -z "$cid" || -z "$cs" || -z "$rt" ]]; then
    local at
    at=$(printf '%s' "$GOOGLE_DRIVE_OAUTH" | python3 -c "import sys,json;print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null || echo "")
    [[ -n "$at" ]] || die "GOOGLE_DRIVE_OAUTH lacks refresh credentials and access_token."
    echo "$at"
    return 0
  fi

  local resp at
  resp=$(curl -s -X POST "$uri" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "client_id=$cid" -d "client_secret=$cs" \
    -d "refresh_token=$rt" -d "grant_type=refresh_token")
  at=$(printf '%s' "$resp" | python3 -c "import sys,json;print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null || echo "")
  [[ -n "$at" ]] || die "Failed to obtain access token. Response: $resp"
  echo "$at"
}

cmd_create_folder() {
  local name="" parent="$DEFAULT_PARENT_FOLDER_ID"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --name) name="$2"; shift 2 ;;
      --parent) parent="$2"; shift 2 ;;
      *) die "Unknown arg: $1" ;;
    esac
  done
  [[ -n "$name" ]] || die "--name is required"

  local token; token=$(get_access_token)
  local resp
  resp=$(curl -s -X POST "https://www.googleapis.com/drive/v3/files?fields=id" \
    -H "Authorization: Bearer $token" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\",\"mimeType\":\"application/vnd.google-apps.folder\",\"parents\":[\"$parent\"]}")
  local fid
  fid=$(printf '%s' "$resp" | python3 -c "import sys,json;print(json.load(sys.stdin).get('id',''))" 2>/dev/null || echo "")
  [[ -n "$fid" ]] || die "Folder creation failed. Response: $resp"
  echo "[OK] Created Drive folder '$name' (id=$fid) under parent $parent" >&2
  echo "$fid"
}

cmd_upload() {
  local file="" folder="" mime=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --file) file="$2"; shift 2 ;;
      --folder) folder="$2"; shift 2 ;;
      --mime) mime="$2"; shift 2 ;;
      *) die "Unknown arg: $1" ;;
    esac
  done
  [[ -n "$file" ]] || die "--file is required"
  [[ -f "$file" ]] || die "File not found: $file"
  [[ -n "$folder" ]] || die "--folder is required"

  # Infer MIME type from extension when not given.
  if [[ -z "$mime" ]]; then
    case "$file" in
      *.csv) mime="text/csv" ;;
      *.json) mime="application/json" ;;
      *.txt) mime="text/plain" ;;
      *.html) mime="text/html" ;;
      *) mime="application/octet-stream" ;;
    esac
  fi

  local token; token=$(get_access_token)
  local fname; fname=$(basename "$file")
  local resp
  resp=$(curl -s -X POST \
    "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,webViewLink" \
    -H "Authorization: Bearer $token" \
    -F "metadata={\"name\":\"$fname\",\"parents\":[\"$folder\"]};type=application/json;charset=UTF-8" \
    -F "media=@$file;type=$mime")
  local fid link
  fid=$(printf '%s' "$resp" | python3 -c "import sys,json;print(json.load(sys.stdin).get('id',''))" 2>/dev/null || echo "")
  link=$(printf '%s' "$resp" | python3 -c "import sys,json;print(json.load(sys.stdin).get('webViewLink',''))" 2>/dev/null || echo "")
  [[ -n "$fid" ]] || die "Upload failed for $fname. Response: $resp"
  echo "[OK] Uploaded $fname (id=$fid)" >&2
  echo "$fid $link"
}

cmd_list_jobs() {
  local parent="$DEFAULT_PARENT_FOLDER_ID"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --parent) parent="$2"; shift 2 ;;
      *) die "Unknown arg: $1" ;;
    esac
  done
  local token; token=$(get_access_token)

  # List subfolders of the project folder.
  local q resp
  q=$(python3 -c "import urllib.parse;print(urllib.parse.quote(\"'$parent' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false\"))")
  resp=$(curl -s -H "Authorization: Bearer $token" \
    "https://www.googleapis.com/drive/v3/files?q=$q&fields=files(id,name)&pageSize=1000")

  # For each subfolder, emit a TSV line only if it is pending
  # (has job-manifest.json but no *_summary.json among its children).
  printf '%s' "$resp" | python3 -c "
import sys, json, subprocess, urllib.parse
token = '''$token'''
folders = json.load(sys.stdin).get('files', [])
for fo in folders:
    fid = fo['id']; name = fo['name']
    q = urllib.parse.quote(\"'%s' in parents and trashed=false\" % fid)
    url = 'https://www.googleapis.com/drive/v3/files?q=%s&fields=files(name)&pageSize=1000' % q
    out = subprocess.run(['curl','-s','-H','Authorization: Bearer '+token, url],
                         capture_output=True, text=True).stdout
    try:
        names = [f['name'] for f in json.loads(out).get('files', [])]
    except Exception:
        names = []
    has_manifest = 'job-manifest.json' in names
    has_summary = any(n.endswith('_summary.json') for n in names)
    if has_manifest and not has_summary:
        print('%s\t%s' % (fid, name))
"
}

cmd_download() {
  local folder="" name="" out=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --folder) folder="$2"; shift 2 ;;
      --name) name="$2"; shift 2 ;;
      --out) out="$2"; shift 2 ;;
      *) die "Unknown arg: $1" ;;
    esac
  done
  [[ -n "$folder" ]] || die "--folder is required"
  [[ -n "$name" ]] || die "--name is required"
  [[ -n "$out" ]] || die "--out is required"

  local token; token=$(get_access_token)
  local q resp fid
  q=$(python3 -c "import urllib.parse;print(urllib.parse.quote(\"'$folder' in parents and name='$name' and trashed=false\"))")
  resp=$(curl -s -H "Authorization: Bearer $token" \
    "https://www.googleapis.com/drive/v3/files?q=$q&fields=files(id,name)")
  fid=$(printf '%s' "$resp" | python3 -c "import sys,json;fs=json.load(sys.stdin).get('files',[]);print(fs[0]['id'] if fs else '')" 2>/dev/null || echo "")
  [[ -n "$fid" ]] || die "File '$name' not found in folder $folder. Response: $resp"

  mkdir -p "$(dirname "$out")"
  curl -s -L -H "Authorization: Bearer $token" \
    "https://www.googleapis.com/drive/v3/files/$fid?alt=media" -o "$out"
  [[ -s "$out" ]] || die "Downloaded file is empty: $out"
  echo "[OK] Downloaded $name -> $out" >&2
  echo "$out"
}

cmd_delete() {
  local folder="" name=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --folder) folder="$2"; shift 2 ;;
      --name) name="$2"; shift 2 ;;
      *) die "Unknown arg: $1" ;;
    esac
  done
  [[ -n "$folder" ]] || die "--folder is required"
  [[ -n "$name" ]] || die "--name is required"

  local token; token=$(get_access_token)
  local q resp fid
  q=$(python3 -c "import urllib.parse;print(urllib.parse.quote(\"'$folder' in parents and name='$name' and trashed=false\"))")
  resp=$(curl -s -H "Authorization: Bearer $token" \
    "https://www.googleapis.com/drive/v3/files?q=$q&fields=files(id,name)")
  fid=$(printf '%s' "$resp" | python3 -c "import sys,json;fs=json.load(sys.stdin).get('files',[]);print(fs[0]['id'] if fs else '')" 2>/dev/null || echo "")
  if [[ -z "$fid" ]]; then
    echo "[WARN] File '$name' not found in folder $folder; skipping delete." >&2
    return 0
  fi

  curl -s -X DELETE -H "Authorization: Bearer $token" \
    "https://www.googleapis.com/drive/v3/files/$fid" >/dev/null 2>&1
  echo "[OK] Deleted '$name' from folder $folder" >&2
}

main() {
  [[ $# -ge 1 ]] || die "Usage: drive_utils.sh {create-folder|upload|list-jobs|download|delete} [args]"
  local cmd="$1"; shift
  case "$cmd" in
    create-folder) cmd_create_folder "$@" ;;
    upload) cmd_upload "$@" ;;
    list-jobs) cmd_list_jobs "$@" ;;
    download) cmd_download "$@" ;;
    delete) cmd_delete "$@" ;;
    *) die "Unknown command: $cmd" ;;
  esac
}

main "$@"
