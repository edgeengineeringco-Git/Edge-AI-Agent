---
name: google-drive-upload
description: Upload files to Google Drive using OAuth refresh token auth. Requires GOOGLE_DRIVE_OAUTH secret (JSON with client_id, client_secret, refresh_token) stored as an agent job secret.
---

# Google Drive Upload Skill

Uploads files to a specified Google Drive folder using OAuth refresh token authentication.

Two upload methods are available:

- **`upload-oauth.sh`** (recommended) — Uses OAuth refresh token. Best for user-owned Drive folders.
- **`upload.sh`** (legacy) — Uses Google Cloud service account JWT auth. May fail on free-tier accounts ("no storage quota").

## Setup (OAuth method)

The `GOOGLE_DRIVE_OAUTH` secret is already configured and stored in the thepopebot secrets system. It contains:

- `client_id` — Google OAuth client ID
- `client_secret` — Google OAuth client secret
- `refresh_token` — OAuth refresh token (used to get fresh access tokens)
- `token_uri` — Token endpoint (default: `https://oauth2.googleapis.com/token`)

To update or replace this secret, use the Admin UI (Settings > Agent Jobs > Secrets).

The default folder ID for EDGE reports is: `1ECFvfIafuyRqgU4fV9jFMt9GXzTRLO5T`

To find a folder ID: open the folder in Google Drive → the URL contains `folders/<FOLDER_ID>`.

## Usage

### Upload a file (OAuth method — recommended)

```bash
skills/google-drive-upload/upload-oauth.sh /path/to/file.html <FOLDER_ID> [mime-type]
```

- `GOOGLE_DRIVE_OAUTH` env var must be set (auto-injected into agent-job containers)
- `FOLDER_ID` required as second argument or set `GOOGLE_DRIVE_TARGET_FOLDER` env var
- `mime-type` defaults to `text/html`

### Upload a file (service account method — legacy)

```bash
skills/google-drive-upload/upload.sh /path/to/file.html <FOLDER_ID> [mime-type]
```

- Requires `GOOGLE_DRIVE_CREDENTIALS` env var (service account JSON key)

### Examples

```bash
# Upload HTML report (OAuth)
skills/google-drive-upload/upload-oauth.sh /tmp/report.html 1ECFvfIafuyRqgU4fV9jFMt9GXzTRLO5T

# Upload with explicit MIME type
skills/google-drive-upload/upload-oauth.sh /tmp/data.csv 1ECFvfIafuyRqgU4fV9jFMt9GXzTRLO5T text/csv

# Upload using default folder from env
export GOOGLE_DRIVE_TARGET_FOLDER=1ECFvfIafuyRqgU4fV9jFMt9GXzTRLO5T
skills/google-drive-upload/upload-oauth.sh /tmp/report.html
```

## How It Works (OAuth method)

1. Reads OAuth credentials from `GOOGLE_DRIVE_OAUTH` env var (JSON with client_id, client_secret, refresh_token)
2. Exchanges the refresh token for a fresh Google OAuth2 access token
3. Uploads the file using the Google Drive API v3 (multipart upload)
4. Outputs the file ID and URL on success

## Troubleshooting

- **"GOOGLE_DRIVE_OAUTH not set"** — The secret must be configured in Admin > Settings > Agent Jobs > Secrets
- **"Failed to get access token"** — The refresh token may have expired (re-auth needed) or credentials are invalid
- **"File not found"** error — Verify the uploaded file was created in the expected folder
- **403/404 on upload** — Verify the folder ID is correct and the authenticated user has access to the folder
