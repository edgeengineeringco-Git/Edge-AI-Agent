---
name: google-drive-upload
description: Upload files to Google Drive using a service account. Requires GOOGLE_DRIVE_CREDENTIALS secret (service account JSON key) stored in the Admin UI.
---

# Google Drive Upload Skill

Uploads files to a specified Google Drive folder using a Google Cloud service account for authentication.

## Setup

### 1. Create a Google Cloud Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → IAM & Admin → Service Accounts
2. Create a new service account (e.g., "edge-agent-uploader")
3. Generate a JSON key for this service account and download it
4. Store the **entire JSON key** as a secret named `GOOGLE_DRIVE_CREDENTIALS` in the Admin UI (Settings > Agent Jobs > Secrets)

### 2. Share the Target Drive Folder

Share your Google Drive folder with the service account email (e.g., `edge-agent-uploader@<project>.iam.gserviceaccount.com`) as an **Editor** or **Contributor**.

The default folder ID for EDGE reports is: `1ECFvfIafuyRqgU4fV9jFMt9GXzTRLO5T`

To find a folder ID: open the folder in Google Drive → the URL contains `folders/<FOLDER_ID>`.

## Usage

### Upload a file

```bash
skills/google-drive-upload/upload.sh /path/to/file.html <FOLDER_ID> [mime-type]
```

- `FOLDER_ID` is optional if `GOOGLE_DRIVE_TARGET_FOLDER` env var is set
- `mime-type` defaults to `text/html`

### Examples

```bash
# Upload HTML report
skills/google-drive-upload/upload.sh /tmp/report.html 1ECFvfIafuyRqgU4fV9jFMt9GXzTRLO5T

# Upload with explicit MIME type
skills/google-drive-upload/upload.sh /tmp/data.csv 1ECFvfIafuyRqgU4fV9jFMt9GXzTRLO5T text/csv

# Upload using default folder from env
export GOOGLE_DRIVE_TARGET_FOLDER=1ECFvfIafuyRqgU4fV9jFMt9GXzTRLO5T
skills/google-drive-upload/upload.sh /tmp/report.html
```

## How It Works

1. Reads the service account JSON key from `GOOGLE_DRIVE_CREDENTIALS` env var (injected by thepopebot secrets)
2. Creates a signed JWT assertion using the service account's private key
3. Exchanges the JWT for a Google OAuth2 access token
4. Uploads the file using the Google Drive API v3 (multipart upload)
5. Outputs the file ID and URL on success

## Troubleshooting

- **"GOOGLE_DRIVE_CREDENTIALS not set"** — Store the service account JSON key in Admin > Settings > Agent Jobs > Secrets
- **"Failed to get access token"** — Verify the service account JSON key is valid and not expired
- **"File not found"** error — Verify the uploaded file was created in the expected folder
- **403/404 on upload** — Verify the folder ID is correct and the service account email has been granted access to the folder
