#!/bin/bash
set -euo pipefail

# ─── Google Drive Upload Script ───────────────────────────────────────────────
# Uploads a file to a specified Google Drive folder using a service account.
#
# Usage:
#   upload.sh <file_path> [folder_id] [mime_type]
#
# Credentials (one of):
#   - GOOGLE_DRIVE_CREDENTIALS env var (service account JSON key, injected via thepopebot secrets)
#   - GOOGLE_DRIVE_CREDENTIALS_FILE env var (path to a file containing the JSON key)
#
# Folder resolution (first match wins):
#   1. Second CLI argument
#   2. GOOGLE_DRIVE_TARGET_FOLDER env var
#   3. Uses folder specified in credentials JSON (if present, uncommon)
#
# MIME type defaults to text/html if not provided.
# ────────────────────────────────────────────────────────────────────────────────

FILE_PATH="${1:-}"
FOLDER_ID="${2:-${GOOGLE_DRIVE_TARGET_FOLDER:-}}"
MIME_TYPE="${3:-text/html}"

# ─── Validation ────────────────────────────────────────────────────────────────

if [ -z "$FILE_PATH" ]; then
  echo "Error: File path is required."
  echo "Usage: upload.sh <file_path> [folder_id] [mime_type]"
  exit 1
fi

if [ ! -f "$FILE_PATH" ]; then
  echo "Error: File not found: $FILE_PATH"
  exit 1
fi

# ─── Credential Resolution ─────────────────────────────────────────────────────

CREDS_FILE=""

if [ -n "${GOOGLE_DRIVE_CREDENTIALS_FILE:-}" ] && [ -f "$GOOGLE_DRIVE_CREDENTIALS_FILE" ]; then
  CREDS_FILE="$GOOGLE_DRIVE_CREDENTIALS_FILE"
elif [ -n "${GOOGLE_DRIVE_CREDENTIALS:-}" ]; then
  # Write env var to temp file (handles both literal and escaped newlines)
  CREDS_FILE="/tmp/gdrive_creds_$$.json"
  # Use python3 to properly decode the JSON (handles escaped \n in private_key)
  python3 -c "
import sys, json, os
raw = os.environ.get('GOOGLE_DRIVE_CREDENTIALS', '')
# Try parsing as-is; if it fails, try unescaping
try:
    creds = json.loads(raw)
except json.JSONDecodeError:
    # Might have literal newlines that need to be JSON-encoded
    creds = json.loads(json.dumps(raw))
with open('$CREDS_FILE', 'w') as f:
    json.dump(creds, f)
" 2>/dev/null || {
    # Fallback: write raw and let python handle it later
    echo "$GOOGLE_DRIVE_CREDENTIALS" > "$CREDS_FILE"
  }
else
  echo "Error: No Google Drive credentials found."
  echo "Set GOOGLE_DRIVE_CREDENTIALS (service account JSON key) as a secret in the Admin UI."
  exit 1
fi

# ─── Cleanup handler ───────────────────────────────────────────────────────────

cleanup() {
  rm -f /tmp/gdrive_creds_$$.json /tmp/gdrive_key_$$.pem /tmp/gdrive_jwt_$$.txt
}
trap cleanup EXIT

# ─── Extract Credentials ───────────────────────────────────────────────────────

CLIENT_EMAIL=$(python3 -c "import json; print(json.load(open('$CREDS_FILE'))['client_email'])")
TOKEN_URI=$(python3 -c "
import json
d = json.load(open('$CREDS_FILE'))
print(d.get('token_uri', 'https://oauth2.googleapis.com/token'))
")

# Extract and normalize private key (handles \n escapes vs literal newlines)
python3 -c "
import json
d = json.load(open('$CREDS_FILE'))
key = d['private_key']
# If the key has literal \\n (escaped in JSON), python handles it automatically via json.load
with open('/tmp/gdrive_key_$$.pem', 'w') as f:
    f.write(key)
"

PRIVATE_KEY_FILE="/tmp/gdrive_key_$$.pem"

if [ ! -s "$PRIVATE_KEY_FILE" ]; then
  echo "Error: Failed to extract private key from credentials."
  exit 1
fi

if [ -z "$FOLDER_ID" ]; then
  echo "Error: No target folder specified. Pass folder_id as argument or set GOOGLE_DRIVE_TARGET_FOLDER."
  exit 1
fi

# ─── JWT Assertion ─────────────────────────────────────────────────────────────

NOW=$(date +%s)
EXP=$((NOW + 3600))

# Base64url encode function
b64url() {
  base64 -w0 | tr '+/' '-_' | tr -d '='
}

# Create JWT header and claim set
JWT_HEADER=$(echo -n '{"alg":"RS256","typ":"JWT"}' | b64url)

# Build claim set
JWT_CLAIM=$(printf '{"iss":"%s","scope":"https://www.googleapis.com/auth/drive.file","aud":"%s","exp":%d,"iat":%d}' \
  "$CLIENT_EMAIL" "$TOKEN_URI" "$EXP" "$NOW" | b64url)

# Sign with RSA private key
JWT_SIGNATURE=$(echo -n "$JWT_HEADER.$JWT_CLAIM" | \
  openssl dgst -sha256 -sign "$PRIVATE_KEY_FILE" | b64url)

JWT="$JWT_HEADER.$JWT_CLAIM.$JWT_SIGNATURE"

# ─── Exchange for Access Token ─────────────────────────────────────────────────

echo "Exchanging JWT for access token..." >&2
TOKEN_RESPONSE=$(curl -s -X POST "$TOKEN_URI" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=$JWT")

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
  -H "Content-Type: multipart/related" \
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
