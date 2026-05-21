#!/bin/bash
# EDGE K/U/Th Portal — Send Email via Brevo (free) or SendGrid
#
# Sends transactional emails to clients (confirmation, results).
# Gracefully skips if no API key is configured.
#
# Supported providers (auto-detected by which env var is set):
#   BREVO_API_KEY     — Brevo (free, 300 emails/day, no DNS needed) ← default
#   SENDGRID_API_KEY  — SendGrid (legacy, requires domain verification)
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
#   BREVO_API_KEY     — Brevo API key (recommended, free)
#   SENDGRID_API_KEY  — SendGrid API key (alternative)
#   FROM_EMAIL        — sender address (default: info@edgeengineers.net)
#   FROM_NAME         — sender display name (default: EDGE K/U/Th Portal)
#                       Requires sender verification in Brevo before use.

set -euo pipefail

FROM_EMAIL="${FROM_EMAIL:-info@edgeengineers.net}"
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

# ── Detect provider ─────────────────────────────────────────────────────────

PROVIDER=""
API_KEY=""

if [[ -n "${BREVO_API_KEY:-}" ]]; then
  PROVIDER="brevo"
  API_KEY="$BREVO_API_KEY"
elif [[ -n "${SENDGRID_API_KEY:-}" ]]; then
  PROVIDER="sendgrid"
  API_KEY="$SENDGRID_API_KEY"
fi

if [[ -z "$PROVIDER" ]]; then
  echo "[EMAIL] No API key set (BREVO_API_KEY or SENDGRID_API_KEY) — skipping email to $TO"
  exit 0
fi

echo "[EMAIL] Sending to $TO via $PROVIDER ..."

# ── Helper: JSON-encode body ────────────────────────────────────────────────

json_encode() {
  python3 -c "
import sys, json
print(json.dumps(sys.stdin.read()))
" 2>/dev/null || echo "\"$(echo "$1" | sed 's/"/\\"/g' | tr '\n' ' ')\""
}

# ── Send via Brevo ──────────────────────────────────────────────────────────

send_brevo() {
  local body_encoded
  body_encoded=$(echo "$BODY" | python3 -c "
import sys, json
print(json.dumps(sys.stdin.read()))
")

  local payload
  payload=$(cat <<EOF
{
  "sender": {"name": "$FROM_NAME", "email": "$FROM_EMAIL"},
  "to": [{"email": "$TO"}],
  "subject": "$SUBJECT",
  "textContent": $body_encoded
EOF
)

  # Add attachment if provided
  if [[ -n "$ATTACH_PATH" && -f "$ATTACH_PATH" ]]; then
    local encoded
    encoded=$(base64 -w0 < "$ATTACH_PATH" 2>/dev/null || base64 < "$ATTACH_PATH" 2>/dev/null)
    local fname
    fname=$(basename "$ATTACH_PATH")
    payload="${payload},
  \"attachment\": [{\"content\": \"$encoded\", \"name\": \"$fname\"}]"
  fi

  payload="${payload}}"

  local response http_code
  http_code=$(curl -s -o /tmp/brevo_response.txt -w "%{http_code}" \
    "https://api.brevo.com/v3/smtp/email" \
    -X POST \
    -H "api-key: ${API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$payload" 2>/dev/null)
  response=$(cat /tmp/brevo_response.txt 2>/dev/null || echo "")

  if [[ "$http_code" == "201" || "$http_code" == "200" ]]; then
    echo "[EMAIL] Sent successfully (${http_code})"
    return 0
  else
    echo "[EMAIL] Brevo returned ${http_code}: ${response}"
    return 1
  fi
}

# ── Send via SendGrid ───────────────────────────────────────────────────────

send_sendgrid() {
  local body_encoded
  body_encoded=$(echo "$BODY" | python3 -c "
import sys, json
print(json.dumps(sys.stdin.read()))
")

  local payload
  payload=$(cat <<EOF
{
  "personalizations": [{"to": [{"email": "$TO"}]}],
  "from": {"email": "$FROM_EMAIL", "name": "$FROM_NAME"},
  "subject": "$SUBJECT",
  "content": [{"type": "text/plain", "value": $body_encoded}]
EOF
)

  # Add attachment if provided
  if [[ -n "$ATTACH_PATH" && -f "$ATTACH_PATH" ]]; then
    local encoded
    encoded=$(base64 -w0 < "$ATTACH_PATH" 2>/dev/null || base64 < "$ATTACH_PATH" 2>/dev/null)
    local fname
    fname=$(basename "$ATTACH_PATH")
    payload="${payload},
  \"attachments\": [{
    \"content\": \"$encoded\",
    \"filename\": \"${fname}\",
    \"type\": \"text/csv\",
    \"disposition\": \"attachment\"
  }]"
  fi

  payload="${payload}}"

  local response http_code
  http_code=$(curl -s -o /tmp/sg_response.txt -w "%{http_code}" \
    "https://api.sendgrid.com/v3/mail/send" \
    -X POST \
    -H "Authorization: Bearer ${API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$payload" 2>/dev/null)
  response=$(cat /tmp/sg_response.txt 2>/dev/null || echo "")

  if [[ "$http_code" == "202" ]]; then
    echo "[EMAIL] Sent successfully (202)"
    return 0
  else
    echo "[EMAIL] SendGrid returned ${http_code}: ${response}"
    return 1
  fi
}

# ── Dispatch ────────────────────────────────────────────────────────────────

case "$PROVIDER" in
  brevo) send_brevo ;;
  sendgrid) send_sendgrid ;;
esac
