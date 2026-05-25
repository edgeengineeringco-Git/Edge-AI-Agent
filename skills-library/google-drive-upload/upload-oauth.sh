#!/bin/bash
set -euo pipefail

# ─── Google Drive OAuth Upload Script ─────────────────────────────────────────
# Uploads a file to a specified Google Drive folder using OAuth refresh token auth.
# Uses the GOOGLE_DRIVE_OAUTH env var (JSON with client_id, client_secret, refresh_token, token_uri).
#
# Usage:
#   upload-oauth.sh <file_path> <folder_id> [mime_type]
#
# MIME type defaults to text/html if not provided.
# ────────────────────────────────────────────────────────────────────────────────

FILE_PATH="${1:-}"
FOLDER_ID="${2:-${GOOGLE_DRIVE_TARGET_FOLDER:-}}"
MIME_TYPE="${3:-text/html}"

# ─── Validation ────────────────────────────────────────────────────────────────

if [ -z "$FILE_PATH" ]; then
  echo "Error: File path is required."
  echo "Usage: upload-oauth.sh <file_path> <folder_id> [mime_type]"
  exit 1
fi

if [ ! -f "$FILE_PATH" ]; then
  echo "Error: File not found: $FILE_PATH"
  exit 1
fi

if [ -z "$FOLDER_ID" ]; then
  echo "Error: No target folder specified. Pass folder_id as argument or set GOOGLE_DRIVE_TARGET_FOLDER."
  exit 1
fi

# ─── Read OAuth Credentials ────────────────────────────────────────────────────

if [ -z "${GOOGLE_DRIVE_OAUTH:-}" ]; then
  echo "Error: GOOGLE_DRIVE_OAUTH env var not set."
  echo "This should contain JSON with client_id, client_secret, refresh_token, and token_uri."
  exit 1
fi

CLIENT_ID=$(echo "$GOOGLE_DRIVE_OAUTH" | python3 -c "import sys,json; print(json.load(sys.stdin).get('client_id',''))" 2>/dev/null || echo "")
CLIENT_SECRET=$(echo "$GOOGLE_DRIVE_OAUTH" | python3 -c "import sys,json; print(json.load(sys.stdin).get('client_secret',''))" 2>/dev/null || echo "")
REFRESH_TOKEN=$(echo "$GOOGLE_DRIVE_OAUTH" | python3 -c "import sys,json; print(json.load(sys.stdin).get('refresh_token',''))" 2>/dev/null || echo "")
TOKEN_URI=$(echo "$GOOGLE_DRIVE_OAUTH" | python3 -c "import sys,json; print(json.load(sys.stdin).get('token_uri','https://oauth2.googleapis.com/token'))" 2>/dev/null || echo "https://oauth2.googleapis.com/token")

if [ -z "$CLIENT_ID" ] || [ -z "$CLIENT_SECRET" ] || [ -z "$REFRESH_TOKEN" ]; then
  echo "Error: GOOGLE_DRIVE_OAUTH must contain client_id, client_secret, and refresh_token."
  exit 1
fi

# ─── Exchange Refresh Token for Access Token ───────────────────────────────────

echo "Exchanging refresh token for access token..." >&2
TOKEN_RESPONSE=$(curl -s -X POST "$TOKEN_URI" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=$CLIENT_ID" \
  -d "client_secret=$CLIENT_SECRET" \
  -d "refresh_token=$REFRESH_TOKEN" \
  -d "grant_type=refresh_token")

ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('access_token', ''))
except Exception:
    print('')
" 2>/dev/null || echo "")

if [ -z "$ACCESS_TOKEN" ]; then
  echo "Error: Failed to get access token."
  echo "Response: $TOKEN_RESPONSE"
  exit 1
fi

echo "Access token obtained." >&2

# ─── Upload File to Google Drive ───────────────────────────────────────────────

FILE_NAME=$(basename "$FILE_PATH")
echo "Uploading: $FILE_NAME to folder $FOLDER_ID..." >&2

UPLOAD_RESPONSE=$(curl -s -X POST "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "metadata={\"name\":\"$FILE_NAME\",\"parents\":[\"$FOLDER_ID\"]};type=application/json;charset=UTF-8" \
  -F "media=@$FILE_PATH;type=$MIME_TYPE")

# ─── Parse Response ────────────────────────────────────────────────────────────

FILE_ID=$(echo "$UPLOAD_RESPONSE" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('id', ''))
except Exception:
    print('')
" 2>/dev/null || echo "")

if [ -n "$FILE_ID" ]; then
  echo "SUCCESS"
  echo "File ID: $FILE_ID"
  echo "File URL: https://drive.google.com/file/d/$FILE_ID/view"
  echo "File Name: $FILE_NAME"
else
  echo "Error: Upload failed."
  echo "Response: $UPLOAD_RESPONSE"
  exit 1
fi
