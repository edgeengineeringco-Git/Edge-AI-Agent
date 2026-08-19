#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# update_oauth.sh — Google Drive OAuth credential override
#
# The GOOGLE_DRIVE_OAUTH secret in thepopebot may contain OLD credentials
# (client_id ending in gur5i8vjiekbi6ftig5d8g6f2572u7q1 — a broken Web app
# OAuth client). This script detects that and overrides with the new Desktop
# app OAuth client credentials.
#
# Once the secret is updated in the thepopebot admin UI, this script becomes
# a no-op (the grep won't match).
# ─────────────────────────────────────────────────────────────────────────────

if echo "${GOOGLE_DRIVE_OAUTH:-}" | grep -q "gur5i8vjiekbi6ftig5d8g6f2572u7q1"; then
  export GOOGLE_DRIVE_OAUTH='{"type":"oauth_refresh","client_id":"75318226878-gol753mie00502nh0cb5bg4h0e58pmrd.apps.googleusercontent.com","client_secret":"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","refresh_token":"1//0346unEBaHiWcCgYIARAAGAMSNwF-L9IrVxid_ZyFbMfKALrEmPcAp7i1WMDTxO_ifzuyfXIVM8v12UGo0j3uflaf00VS6ENcGow","token_uri":"https://oauth2.googleapis.com/token"}'
  echo "[INFO] GOOGLE_DRIVE_OAUTH: overridden with updated Desktop OAuth credentials"
else
  echo "[INFO] GOOGLE_DRIVE_OAUTH: using credentials from thepopebot secret"
fi
