#!/bin/bash
# EDGE K/U/Th Portal — Send Email via SendGrid API
#
# Sends transactional emails to clients (confirmation, results).
# Gracefully skips if SENDGRID_API_KEY is not configured.
#
# Usage:
#   # Plain text email
#   bash send-email.sh --to client@example.com --subject "Subject" --body "Message"
#
#   # With CSV attachment
#   bash send-email.sh --to client@example.com --subject "Subject" \
#     --body "Message" --attach results.csv
#
# Environment:
#   SENDGRID_API_KEY  — SendGrid API key with Mail Send permission (required for email)
#   FROM_EMAIL        — sender address (default: noreply@edgeengineers.net)
#   FROM_NAME         — sender display name (default: "EDGE K/U/Th Portal")

set -euo pipefail

FROM_EMAIL="${FROM_EMAIL:-noreply@edgeengineers.net}"
FROM_NAME="${FROM_NAME:-EDGE K/U/Th Portal}"

# ── Parse args ──────────────────────────────────────────────────────────────

TO=""
SUBJECT=""
BODY=""
ATTACH_PATH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --to) TO="$2"; shift 2 ;;
    --subject) SUBJECT="$2"; shift 2 ;;
    --body) BODY="$2"; shift 2 ;;
    --attach) ATTACH_PATH="$2"; shift 2 ;;
    *) echo "Unknown: $1"; exit 1 ;;
  esac
done

if [[ -z "$TO" || -z "$SUBJECT" || -z "$BODY" ]]; then
  echo "[ERROR] --to, --subject, and --body are required"
  exit 1
fi

# ── Skip if no API key ──────────────────────────────────────────────────────

if [[ -z "${SENDGRID_API_KEY:-}" ]]; then
  echo "[EMAIL] SENDGRID_API_KEY not set — skipping email to $TO"
  exit 0
fi

echo "[EMAIL] Sending to $TO ..."

# ── Build payload ────────────────────────────────────────────────────────────

# Escape for JSON (basic — handles line breaks and quotes in body)
BODY_ESCAPED=$(echo "$BODY" | python3 -c "
import sys, json
print(json.dumps(sys.stdin.read()))
" 2>/dev/null || echo "$BODY" | sed 's/"/\\"/g' | awk '{printf "%s\\n", $0}')

# Build the JSON payload
PAYLOAD=$(cat <<EOF
{
  "personalizations": [{"to": [{"email": "$TO"}]}],
  "from": {"email": "$FROM_EMAIL", "name": "$FROM_NAME"},
  "subject": "$SUBJECT",
  "content": [{"type": "text/plain", "value": $BODY_ESCAPED}]
EOF
)

# Add attachment if provided
if [[ -n "$ATTACH_PATH" && -f "$ATTACH_PATH" ]]; then
  ENCODED=$(base64 -w0 < "$ATTACH_PATH" 2>/dev/null || base64 < "$ATTACH_PATH" 2>/dev/null)
  FNAME=$(basename "$ATTACH_PATH")
  PAYLOAD="${PAYLOAD},
  \"attachments\": [{
    \"content\": \"$ENCODED\",
    \"filename\": \"${FNAME}\",
    \"type\": \"text/csv\",
    \"disposition\": \"attachment\"
  }]"
fi

PAYLOAD="${PAYLOAD}}"

# ── Send via SendGrid API ───────────────────────────────────────────────────

RESPONSE=$(curl -s -w "\n%{http_code}" \
  "https://api.sendgrid.com/v3/mail/send" \
  -X POST \
  -H "Authorization: Bearer ${SENDGRID_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" 2>/dev/null)

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
RESP_BODY=$(echo "$RESPONSE" | head -n -1)

if [[ "$HTTP_CODE" == "202" ]]; then
  echo "[EMAIL] Sent successfully (202 accepted)"
else
  echo "[EMAIL] SendGrid returned $HTTP_CODE: $RESP_BODY"
  # 202 is success from SendGrid — anything else is an error
  if [[ "$HTTP_CODE" != "202" ]]; then
    echo "[EMAIL] WARNING: Email may not have been delivered"
    exit 1
  fi
fi
