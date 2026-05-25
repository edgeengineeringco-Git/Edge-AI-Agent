#!/usr/bin/env python3
"""
EDGE Smart Video - Google Sheets Integration
Reads/writes the EDGE content tracker via Google Sheets v4 API with OAuth.

Uses GOOGLE_DRIVE_OAUTH credentials (fetched via agent-job-secrets).

Usage:
  Read pending topics:
    python3 sheets_handler.py read --sheet-id SHEET_ID

  Update status:
    python3 sheets_handler.py update --sheet-id SHEET_ID --topic-id SVT001 --status "Draft Ready"

  Full pipeline:
    python3 sheets_handler.py pipeline --sheet-id SHEET_ID --output-dir ./output
"""

import urllib.request
import json
import sys
import os
import csv
import io


TOKEN_URL = "https://oauth2.googleapis.com/token"
SHEETS_API = "https://sheets.googleapis.com/v4/spreadsheets"


def get_access_token(oauth_creds):
    """Exchange refresh token for access token."""
    payload = {
        "client_id": oauth_creds["client_id"],
        "client_secret": oauth_creds["client_secret"],
        "refresh_token": oauth_creds["refresh_token"],
        "grant_type": "refresh_token"
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        TOKEN_URL, data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode())

    return result.get("access_token", "")


def load_oauth():
    """Load OAuth creds from env (injected by agent-job-secrets)."""
    creds_json = os.environ.get("GOOGLE_DRIVE_OAUTH", "")
    if not creds_json:
        # Try to read from a file (for local testing)
        for path in ["/tmp/google_oauth.json", "google_oauth.json"]:
            if os.path.exists(path):
                with open(path) as f:
                    creds_json = f.read()
                break

    if not creds_json:
        raise Exception(
            "GOOGLE_DRIVE_OAUTH not found. "
            "Run: node skills/agent-job-secrets/agent-job-secrets.js get GOOGLE_DRIVE_OAUTH "
            "then export GOOGLE_DRIVE_OAUTH='<json>'"
        )

    try:
        return json.loads(creds_json)
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid GOOGLE_DRIVE_OAUTH JSON: {e}")


def sheets_request(method, url, access_token, body=None):
    """Make an authenticated request to Google Sheets API."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def get_sheet_data(sheet_id, access_token, sheet_name="Edge_topics_sample"):
    """Read all rows from a sheet tab."""
    range_str = urllib.parse.quote(f"'{sheet_name}'!A:E")
    url = f"{SHEETS_API}/{sheet_id}/values/{range_str}"

    result = sheets_request("GET", url, access_token)
    return result.get("values", [])


def update_sheet_cell(sheet_id, row_idx, column, value, access_token, sheet_name="Edge_topics_sample"):
    """Update a single cell by row index and column letter."""
    range_str = urllib.parse.quote(f"'{sheet_name}'!{column}{row_idx}")
    url = f"{SHEETS_API}/{sheet_id}/values/{range_str}?valueInputOption=USER_ENTERED"

    body = {"values": [[value]]}
    return sheets_request("PUT", url, access_token, body)


def find_column_indices(header_row):
    """Map column names to indices (0-based) and letters."""
    col_names = [h.strip().lower() for h in header_row]
    col_map = {}
    letter_map = {}

    for i, name in enumerate(col_names):
        col_map[name] = i
        # Convert 0-based index to A, B, C... Z, AA, AB...
        letter = ""
        n = i + 1
        while n > 0:
            n, rem = divmod(n - 1, 26)
            letter = chr(65 + rem) + letter
        letter_map[name] = letter

    return col_map, letter_map


def parse_row(row, col_map, col_letters):
    """Parse a sheet row into a dict."""
    return {
        "id": row[col_map.get("id", 0)].strip() if col_map.get("id", 0) < len(row) else "",
        "topic": row[col_map.get("topic", 1)].strip() if col_map.get("topic", 1) < len(row) else "",
        "sector": row[col_map.get("sector", 2)].strip() if col_map.get("sector", 2) < len(row) else "",
        "status": row[col_map.get("status", 3)].strip() if col_map.get("status", 3) < len(row) else "",
        "notes": row[col_map.get("notes", 4)].strip() if col_map.get("notes", 4) < len(row) else "",
        "_row": None,  # Will be set by caller
        "_cols": col_map,
        "_letters": col_letters
    }


def read_topics(sheet_id, access_token, sheet_name="Edge_topics_sample"):
    """Read all topics from the sheet."""
    print(f"  Reading sheet...")
    sys.stdout.flush()

    rows = get_sheet_data(sheet_id, access_token, sheet_name)
    if not rows or len(rows) < 2:
        print("  Sheet is empty or has only header")
        return []

    header = rows[0]
    col_map, col_letters = find_column_indices(header)
    print(f"  Columns: {list(col_map.keys())}")

    topics = []
    for i, row in enumerate(rows[1:], start=2):  # row 1 is header, data starts at row 2
        if len(row) < 2 or not row[0].strip():
            continue  # skip empty rows
        topic = parse_row(row, col_map, col_letters)
        topic["_row"] = i  # Actual spreadsheet row number (1-indexed)
        topics.append(topic)

    print(f"  Found {len(topics)} topics")
    return topics


def find_pending(topics):
    """Find first pending topic."""
    for t in topics:
        if t["status"].lower() == "pending":
            return t
    return None


def update_topic_status(sheet_id, access_token, topic_id, row_idx,
                        status, post_text=None, video_url=None, notes=None,
                        sheet_name="Edge_topics_sample"):
    """Update topic status and data in the sheet."""
    updates_made = []

    # Update Status column (usually D)
    update_sheet_cell(sheet_id, row_idx, "D", status, access_token, sheet_name)
    updates_made.append(f"Status -> {status}")
    print(f"  Updated Status -> {status}")

    # Update PostText column (usually E or F)
    if post_text:
        try:
            update_sheet_cell(sheet_id, row_idx, "E", post_text, access_token, sheet_name)
            updates_made.append("PostText updated")
            print(f"  Updated PostText ({len(post_text)} chars)")
        except Exception as e:
            print(f"  Note: Could not update PostText: {e}")

    # Update Notes
    if notes:
        try:
            update_sheet_cell(sheet_id, row_idx, "F", notes, access_token, sheet_name)
            updates_made.append(f"Notes updated")
        except Exception as e:
            print(f"  Note: Could not update Notes: {e}")

    return updates_made


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Google Sheets handler for EDGE video")
    sub = parser.add_subparsers(dest="command", required=True)

    # Read command
    read_cmd = sub.add_parser("read", help="Read topics")
    read_cmd.add_argument("--sheet-id", default=os.environ.get("GOOGLE_SHEETS_ID", ""),
                          help="Google Sheet ID")
    read_cmd.add_argument("--find-pending", action="store_true")
    read_cmd.add_argument("--output-dir", default="./output")

    # Update command
    upd_cmd = sub.add_parser("update", help="Update topic")
    upd_cmd.add_argument("--sheet-id", default=os.environ.get("GOOGLE_SHEETS_ID", ""))
    upd_cmd.add_argument("--topic-id", required=True)
    upd_cmd.add_argument("--row", type=int, help="Sheet row number (auto-found if not given)")
    upd_cmd.add_argument("--status", default="Draft Ready")
    upd_cmd.add_argument("--post-text", default="")
    upd_cmd.add_argument("--video-url", default="")
    upd_cmd.add_argument("--notes", default="")

    # Pipeline command
    pipe_cmd = sub.add_parser("pipeline", help="Full pipeline: find pending + read output")
    pipe_cmd.add_argument("--sheet-id", default=os.environ.get("GOOGLE_SHEETS_ID", ""))
    pipe_cmd.add_argument("--output-dir", default="./output")

    args = parser.parse_args()

    if not args.sheet_id:
        print("ERROR: --sheet-id required or set GOOGLE_SHEETS_ID env var", file=sys.stderr)
        return 1

    # Load OAuth
    try:
        oauth = load_oauth()
        access_token = get_access_token(oauth)
        print("  OAuth token obtained")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if args.command == "read":
        topics = read_topics(args.sheet_id, access_token)

        if args.find_pending:
            pending = find_pending(topics)
            if pending:
                print(f"\nPending topic found:")
                print(f"  ID:     {pending['id']}")
                print(f"  Topic:  {pending['topic']}")
                print(f"  Sector: {pending['sector']}")
                print(f"  Row:    {pending['_row']}")

                if args.output_dir:
                    os.makedirs(args.output_dir, exist_ok=True)
                    with open(os.path.join(args.output_dir, "topic.json"), "w") as f:
                        json.dump({
                            "id": pending["id"],
                            "topic": pending["topic"],
                            "sector": pending["sector"],
                            "status": pending["status"],
                            "notes": pending["notes"],
                            "sheet_row": pending["_row"],
                            "sheet_id": args.sheet_id
                        }, f, indent=2)
                    print(f"  Saved to {args.output_dir}/topic.json")
            else:
                print("No pending topics found.")
                return 1
        else:
            for t in topics:
                print(f"  Row {t['_row']:3} [{t['status']:12}] {t['id']}: {t['topic']}")

    elif args.command == "update":
        topics = read_topics(args.sheet_id, access_token) if not args.row else None

        if topics and not args.row:
            for t in topics:
                if t["id"] == args.topic_id:
                    args.row = t["_row"]
                    break

        if not args.row:
            print(f"ERROR: Topic {args.topic_id} not found and --row not given", file=sys.stderr)
            return 1

        update_topic_status(
            args.sheet_id, access_token, args.topic_id, args.row,
            args.status, args.post_text, args.video_url, args.notes
        )

    elif args.command == "pipeline":
        topics = read_topics(args.sheet_id, access_token)
        pending = find_pending(topics)

        if not pending:
            print("No pending topics.", file=sys.stderr)
            return 1

        print(f"\nNext topic: {pending['id']} - {pending['topic']}")

        if args.output_dir:
            os.makedirs(args.output_dir, exist_ok=True)
            with open(os.path.join(args.output_dir, "topic.json"), "w") as f:
                json.dump({
                    "id": pending["id"],
                    "topic": pending["topic"],
                    "sector": pending["sector"],
                    "sheet_row": pending["_row"],
                    "sheet_id": args.sheet_id
                }, f, indent=2)

    return 0


if __name__ == "__main__":
    main()
