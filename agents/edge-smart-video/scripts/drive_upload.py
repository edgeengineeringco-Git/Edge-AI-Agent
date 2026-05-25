#!/usr/bin/env python3
"""
EDGE Smart Video - Google Drive Upload
Uploads generated content to a dated subfolder in a target Drive folder.

Usage:
  python3 scripts/drive_upload.py --folder-id DRIVE_FOLDER_ID --output-dir ./output/YYYY-MM-DD --topic "Topic Name"

Requires GOOGLE_DRIVE_OAUTH env var (auto-injected for scoped agent jobs).
"""

import urllib.request
import json
import sys
import os
import time
import mimetypes

DRIVE_API = "https://www.googleapis.com/drive/v3"
UPLOAD_API = "https://www.googleapis.com/upload/drive/v3"
TOKEN_URL = "https://oauth2.googleapis.com/token"


def get_access_token():
    """Get access token from GOOGLE_DRIVE_OAUTH env var."""
    creds_json = os.environ.get("GOOGLE_DRIVE_OAUTH", "")
    if not creds_json:
        raise Exception(
            "GOOGLE_DRIVE_OAUTH env var not found. "
            "Run: node skills/agent-job-secrets/agent-job-secrets.js get GOOGLE_DRIVE_OAUTH"
        )

    creds = json.loads(creds_json)
    payload = {
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"],
        "refresh_token": creds["refresh_token"],
        "grant_type": "refresh_token"
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        TOKEN_URL, data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode())

    token = result.get("access_token", "")
    if not token:
        raise Exception(f"Failed to get access token: {result.get('error', 'unknown')}")
    return token


def drive_request(method, url, access_token, body=None, content_type="application/json"):
    """Make an authenticated request to Google Drive API."""
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    if body is not None:
        headers["Content-Type"] = content_type
        data = json.dumps(body).encode("utf-8") if isinstance(body, dict) else body
    else:
        data = None

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        raise Exception(f"Drive API error ({e.code}): {error_body[:300]}")


def create_folder(name, parent_id, access_token):
    """Create a folder in Drive. Returns folder ID."""
    body = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id]
    }
    url = f"{DRIVE_API}/files?fields=id,name,webViewLink"
    result = drive_request("POST", url, access_token, body)
    print(f"  \u2713 Created folder: {name}")
    print(f"    ID: {result['id']}")
    print(f"    URL: {result.get('webViewLink', 'N/A')}")
    return result["id"]


def upload_file(file_path, folder_id, access_token):
    """Upload a single file to Drive. Returns file info."""
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    # Step 1: Create metadata
    metadata = json.dumps({
        "name": file_name,
        "parents": [folder_id]
    }).encode("utf-8")

    # Step 2: Read file content
    with open(file_path, "rb") as f:
        file_content = f.read()

    # Step 3: Multipart upload
    boundary = "----boundary" + str(int(time.time() * 1000))

    body = (
        b"--" + boundary.encode() + b"\r\n"
        b"Content-Type: application/json; charset=UTF-8\r\n\r\n" +
        metadata + b"\r\n" +
        b"--" + boundary.encode() + b"\r\n"
        b"Content-Type: application/octet-stream\r\n\r\n" +
        file_content + b"\r\n" +
        b"--" + boundary.encode() + b"--\r\n"
    )

    content_type = f"multipart/related; boundary={boundary}"
    url = f"{UPLOAD_API}/files?uploadType=multipart&fields=id,name,webViewLink,size"

    result = drive_request("POST", url, access_token, body, content_type)

    print(f"  \u2713 {file_name} ({_format_size(file_size)})")
    return result


def _format_size(bytes_val):
    for unit in ["B", "KB", "MB"]:
        if bytes_val < 1024:
            return f"{bytes_val:.0f}{unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f}MB"


def shorten_topic(topic, max_words=5):
    """Create a short folder name from topic."""
    import re
    # Remove special chars, keep alphanumeric and spaces
    clean = re.sub(r'[^a-zA-Z0-9\s-]', '', topic)
    words = clean.split()
    # Take first max_words words
    short = '-'.join(words[:max_words])
    # Add date prefix
    date_prefix = time.strftime("%Y-%m-%d")
    return f"{date_prefix}-{short}"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Upload EDGE video output to Drive")
    parser.add_argument("--folder-id", required=True, help="Target Drive folder ID")
    parser.add_argument("--output-dir", required=True, help="Local output directory")
    parser.add_argument("--topic", required=True, help="Topic name (for subfolder naming)")
    args = parser.parse_args()

    if not os.path.isdir(args.output_dir):
        print(f"ERROR: Output dir not found: {args.output_dir}", file=sys.stderr)
        return 1

    # Auth
    print("Authenticating...")
    sys.stdout.flush()
    access_token = get_access_token()

    # Create subfolder
    folder_name = shorten_topic(args.topic)
    print(f"Creating subfolder: {folder_name}")
    sys.stdout.flush()
    subfolder_id = create_folder(folder_name, args.folder_id, access_token)

    # Upload files
    print(f"\nUploading files from {args.output_dir}...")
    sys.stdout.flush()

    # Files to upload (in priority order)
    upload_patterns = [
        "*.png", "*.jpg", "*.jpeg", "*.html",
        "*.json", "*.md", "*.mp4", "*.webm"
    ]

    imported_glob = False
    try:
        import glob
        imported_glob = True
        files_to_upload = []
        for pattern in upload_patterns:
            files_to_upload.extend(glob.glob(os.path.join(args.output_dir, pattern)))

        # Remove duplicates and sort
        files_to_upload = sorted(set(f for f in files_to_upload if os.path.isfile(f)))
    except ImportError:
        # Fallback: list directory
        files_to_upload = []
        all_files = sorted(os.listdir(args.output_dir))
        for f in all_files:
            path = os.path.join(args.output_dir, f)
            if os.path.isfile(path):
                ext = os.path.splitext(f)[1].lower()
                if ext in ['.png', '.jpg', '.jpeg', '.html', '.json', '.md', '.mp4', '.webm']:
                    files_to_upload.append(path)

    if not files_to_upload:
        print("  No files to upload (dir may be empty)")
    else:
        for file_path in files_to_upload:
            try:
                upload_file(file_path, subfolder_id, access_token)
            except Exception as e:
                print(f"  \u2717 {os.path.basename(file_path)} failed: {e}", file=sys.stderr)

    # Get folder URL
    try:
        folder_info = drive_request(
            "GET",
            f"{DRIVE_API}/files/{subfolder_id}?fields=id,name,webViewLink",
            access_token
        )
        folder_url = folder_info.get("webViewLink", f"https://drive.google.com/drive/folders/{subfolder_id}")
    except Exception:
        folder_url = f"https://drive.google.com/drive/folders/{subfolder_id}"

    # Write manifest
    result = {
        "folder_id": subfolder_id,
        "folder_name": folder_name,
        "folder_url": folder_url,
        "parent_folder_id": args.folder_id,
        "files_uploaded": len(files_to_upload)
    }

    result_path = os.path.join(args.output_dir, "drive_upload.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n\u2713 Upload complete: {len(files_to_upload)} files to {folder_name}")
    print(f"  Folder URL: {folder_url}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
