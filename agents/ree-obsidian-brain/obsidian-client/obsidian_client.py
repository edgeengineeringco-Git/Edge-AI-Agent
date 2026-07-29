#!/usr/bin/env python3
"""
Obsidian Local REST API Client for the REE Obsidian Brain.

Connects to the Obsidian Local REST API plugin running on the user's desktop.
Zero external dependencies — uses only Python standard library.

Usage:
    from obsidian_client import ObsidianClient

    client = ObsidianClient(api_key="your-api-key", port=27124)
    notes = client.list_notes()
    client.create_note("path/to/note", "Note content")
"""

import os
import json
import sys
import argparse
import datetime
import urllib.request
import urllib.parse
import urllib.error
from typing import Optional


class ObsidianClientError(Exception):
    """Wrapper for API errors with status code and body."""
    def __init__(self, status: int, body: str):
        self.status = status
        self.body = body
        super().__init__(f"API error {status}: {body[:200]}")


class ObsidianClient:
    """Client for the Obsidian Local REST API plugin (zero external dependencies)."""

    def __init__(self, api_key: Optional[str] = None, port: int = 27124, host: str = "localhost"):
        self.api_key = api_key or os.environ.get("OBSIDIAN_API_KEY", "")
        self.base_url = f"http://{host}:{port}"
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------ #
    #  Core helpers (stdlib urllib only)
    # ------------------------------------------------------------------ #

    def _request(self, method: str, path: str, body: Optional[dict] = None) -> dict:
        """Make an HTTP request and return parsed JSON response."""
        url = f"{self.base_url}{path}"
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=data,
            headers=self._headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(req) as resp:
                content = resp.read().decode("utf-8")
                if content.strip():
                    return json.loads(content)
                return {}
        except urllib.error.HTTPError as e:
            body_text = e.read().decode("utf-8", errors="replace")
            raise ObsidianClientError(e.code, body_text) from e
        except urllib.error.URLError as e:
            raise ObsidianClientError(0, f"Connection failed: {e.reason}") from e

    def _get(self, path: str) -> tuple:
        """GET request, returns (status, body_text_or_parsed_json)."""
        url = f"{self.base_url}{path}"
        req = urllib.request.Request(url, headers=self._headers, method="GET")
        try:
            with urllib.request.urlopen(req) as resp:
                content = resp.read().decode("utf-8")
                if content.strip():
                    return resp.status, json.loads(content)
                return resp.status, {}
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            try:
                return e.code, json.loads(body) if body.strip() else {}
            except (json.JSONDecodeError, ValueError):
                return e.code, body
        except urllib.error.URLError as e:
            raise ObsidianClientError(0, f"Connection failed: {e.reason}") from e

    def _put(self, path: str, data: Optional[dict] = None) -> tuple:
        """PUT request, returns (status, parsed_json)."""
        url = f"{self.base_url}{path}"
        body = json.dumps(data or {}).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=self._headers, method="PUT")
        try:
            with urllib.request.urlopen(req) as resp:
                content = resp.read().decode("utf-8")
                if content.strip():
                    return resp.status, json.loads(content)
                return resp.status, {}
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            try:
                return e.code, json.loads(body) if body.strip() else {}
            except (json.JSONDecodeError, ValueError):
                return e.code, body
        except urllib.error.URLError as e:
            raise ObsidianClientError(0, f"Connection failed: {e.reason}") from e

    def _delete(self, path: str) -> tuple:
        """DELETE request, returns (status, parsed_json)."""
        url = f"{self.base_url}{path}"
        req = urllib.request.Request(url, headers=self._headers, method="DELETE")
        try:
            with urllib.request.urlopen(req) as resp:
                content = resp.read().decode("utf-8")
                if content.strip():
                    return resp.status, json.loads(content)
                return resp.status, {}
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            try:
                return e.code, json.loads(body) if body.strip() else {}
            except (json.JSONDecodeError, ValueError):
                return e.code, body
        except urllib.error.URLError as e:
            return 0, f"Connection failed: {e.reason}"

    # ------------------------------------------------------------------ #
    #  Health / status
    # ------------------------------------------------------------------ #

    def ping(self) -> bool:
        """Check if the REST API is reachable."""
        try:
            status, _ = self._get("/")
            return status == 200
        except ObsidianClientError:
            return False

    # ------------------------------------------------------------------ #
    #  Vault CRUD
    # ------------------------------------------------------------------ #

    def list_notes(self) -> list[dict]:
        """List all notes in the vault (recursive)."""
        status, data = self._get("/vault/")
        if status != 200:
            raise ObsidianClientError(status, str(data))
        return data if isinstance(data, list) else []

    def get_note(self, path: str) -> Optional[str]:
        """Read a note by its vault path (e.g. '02-Elements/Neodymium.md')."""
        encoded = urllib.parse.quote(path, safe="")
        status, data = self._get(f"/vault/{encoded}")
        if status == 404:
            return None
        # The REST API returns the raw markdown as the response body
        if isinstance(data, str):
            return data
        return str(data)

    def note_exists(self, path: str) -> bool:
        """Check if a note exists at the given path."""
        return self.get_note(path) is not None

    def create_note(self, path: str, content: str) -> dict:
        """Create a new note. Returns the API response."""
        encoded = urllib.parse.quote(path, safe="")
        status, data = self._put(f"/vault/{encoded}", {"content": content})
        if status not in (200, 201):
            raise ObsidianClientError(status, str(data))
        return data if isinstance(data, dict) else {}

    def update_note(self, path: str, content: str) -> dict:
        """Overwrite an existing note."""
        encoded = urllib.parse.quote(path, safe="")
        status, data = self._put(f"/vault/{encoded}", {"content": content})
        if status not in (200, 201):
            raise ObsidianClientError(status, str(data))
        return data if isinstance(data, dict) else {}

    def delete_note(self, path: str) -> dict:
        """Delete a note."""
        encoded = urllib.parse.quote(path, safe="")
        status, data = self._delete(f"/vault/{encoded}")
        if status not in (200, 204):
            raise ObsidianClientError(status, str(data))
        return data if isinstance(data, dict) else {}

    # ------------------------------------------------------------------ #
    #  Search
    # ------------------------------------------------------------------ #

    def search(self, query: str, context_length: int = 100) -> list[dict]:
        """Full-text search across the vault. Returns list of {filename, match, context}."""
        status, data = self._request(
            "POST", "/search",
            {"query": query, "contextLength": context_length}
        )
        if status != 200:
            raise ObsidianClientError(status, str(data))
        return data if isinstance(data, list) else []

    # ------------------------------------------------------------------ #
    #  Commands
    # ------------------------------------------------------------------ #

    def list_commands(self) -> list[dict]:
        """List all available Obsidian commands."""
        status, data = self._get("/commands")
        if status != 200:
            raise ObsidianClientError(status, str(data))
        return data if isinstance(data, list) else []

    def execute_command(self, command_id: str) -> dict:
        """Execute an Obsidian command by ID (e.g. 'editor:insert-link')."""
        encoded = urllib.parse.quote(command_id, safe="")
        status, data = self._request("POST", f"/commands/{encoded}")
        return data if isinstance(data, dict) else {}

    # ------------------------------------------------------------------ #
    #  Daily / periodic notes
    # ------------------------------------------------------------------ #

    def get_daily_note(self) -> Optional[str]:
        """Get today's daily note content."""
        status, data = self._get("/daily")
        if status == 404:
            return None
        if isinstance(data, dict):
            return data.get("content", "")
        return str(data)

    # ------------------------------------------------------------------ #
    #  Active note
    # ------------------------------------------------------------------ #

    def get_active_note(self) -> Optional[dict]:
        """Get the currently active note in Obsidian."""
        status, data = self._get("/active")
        if status == 404:
            return None
        return data if isinstance(data, dict) else {"content": str(data)}

    # ------------------------------------------------------------------ #
    #  REE-specific helpers
    # ------------------------------------------------------------------ #

    def ingest_source_note(
        self,
        title: str,
        authors: list[str],
        year: str,
        source_type: str = "paper",
        doi: str = "",
        tags: list[str] = None,
        abstract: str = "",
        claims: list[str] = None,
        linked_notes: list[str] = None,
    ) -> str:
        """Create a scientific source note in 01-Sources/ with proper frontmatter.

        Returns the vault path of the created note.
        """
        tags = tags or []
        claims = claims or []
        linked_notes = linked_notes or []

        # Sanitize title for filename
        safe_title = title.replace(":", " -").replace("/", "-").replace("?", "").replace('"', "'")
        filename = f"{safe_title[:120]}.md"
        vault_path = f"01-Sources/{filename}"

        today = datetime.date.today().isoformat()

        # Build frontmatter
        frontmatter = {
            "title": title,
            "authors": authors,
            "year": year,
            "date_created": today,
            "date_modified": today,
            "type": source_type,
            "status": "seed",
            "tags": ["source", source_type] + tags,
        }
        if doi:
            frontmatter["doi"] = doi

        # Build body
        body_parts = [f"# {title}", ""]
        if authors:
            body_parts.append(f"**Authors:** {', '.join(authors)}")
        if year:
            body_parts.append(f"**Year:** {year}")
        if doi:
            body_parts.append(f"**DOI:** [{doi}](https://doi.org/{doi})")
        body_parts.append("")

        if abstract:
            body_parts.extend(["## Abstract", "", abstract, ""])

        if claims:
            body_parts.append("## Key Claims")
            for i, claim in enumerate(claims, 1):
                body_parts.append(f"{i}. {claim}")
            body_parts.append("")

        if linked_notes:
            body_parts.append("## Related")
            for ln in linked_notes:
                body_parts.append(f"- [[{ln}]]")

        # Assemble full note
        note = f"---\n{json.dumps(frontmatter, indent=2)}\n---\n\n" + "\n".join(body_parts)

        self.create_note(vault_path, note)
        return vault_path

    def quick_capture(self, content: str, folder: str = "00-Inbox") -> str:
        """Drop a quick note into the inbox for later curation.

        Returns the vault path.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        vault_path = f"{folder}/quick-capture-{timestamp}.md"
        self.create_note(vault_path, content)
        return vault_path

    def link_mentions(self, note_path: str, target: str) -> list[str]:
        """Find all notes mentioning a term and add a [[wiki-link]] back.

        Returns list of updated note paths.
        """
        results = self.search(target, context_length=200)
        updated = []
        for r in results:
            fname = r.get("filename", "")
            if fname == note_path or not fname.endswith(".md"):
                continue
            content = self.get_note(fname)
            if content and target not in content:
                new_content = content.rstrip() + f"\n\nSee also: [[{note_path.replace('.md', '')}]]\n"
                self.update_note(fname, new_content)
                updated.append(fname)
        return updated


# ------------------------------------------------------------------ #
#  CLI entrypoint
# ------------------------------------------------------------------ #

def main():
    parser = argparse.ArgumentParser(
        description="Obsidian REST API client for the REE Obsidian Brain"
    )
    parser.add_argument(
        "--key",
        help="API key (default: $OBSIDIAN_API_KEY)",
        default=os.environ.get("OBSIDIAN_API_KEY", ""),
    )
    parser.add_argument("--port", type=int, default=27124)
    parser.add_argument("--host", default="localhost")

    sub = parser.add_subparsers(dest="command")

    # ping
    sub.add_parser("ping", help="Check if Obsidian REST API is reachable")

    # list
    sub.add_parser("list", help="List all vault notes")

    # get
    get_p = sub.add_parser("get", help="Read a note")
    get_p.add_argument("path", help="Vault path (e.g. '02-Elements/Neodymium.md')")

    # create
    create_p = sub.add_parser("create", help="Create a new note")
    create_p.add_argument("path", help="Vault path")
    create_p.add_argument("--content", "-c", default="", help="Note content")
    create_p.add_argument("--file", "-f", help="Read content from file")

    # search
    search_p = sub.add_parser("search", help="Full-text search")
    search_p.add_argument("query", help="Search term")

    # ingest-source
    ingest_p = sub.add_parser("ingest-source", help="Create a scientific source note")
    ingest_p.add_argument("--title", required=True)
    ingest_p.add_argument("--authors", nargs="+", default=[])
    ingest_p.add_argument("--year", default="")
    ingest_p.add_argument("--doi", default="")
    ingest_p.add_argument("--tags", nargs="+", default=[])
    ingest_p.add_argument("--abstract", default="")
    ingest_p.add_argument("--claims", nargs="+", default=[])

    # quick-capture
    qc_p = sub.add_parser("quick-capture", help="Drop a note into the inbox")
    qc_p.add_argument("content", help="Note content")

    # delete
    del_p = sub.add_parser("delete", help="Delete a note")
    del_p.add_argument("path", help="Vault path")

    args = parser.parse_args()

    if not args.key:
        print("Error: API key required via --key or OBSIDIAN_API_KEY env var", file=sys.stderr)
        sys.exit(1)

    client = ObsidianClient(api_key=args.key, port=args.port, host=args.host)

    if args.command == "ping":
        ok = client.ping()
        print(json.dumps({"reachable": ok}))
        sys.exit(0 if ok else 1)

    elif args.command == "list":
        notes = client.list_notes()
        print(json.dumps(notes, indent=2))

    elif args.command == "get":
        content = client.get_note(args.path)
        if content is None:
            print(f"Note not found: {args.path}", file=sys.stderr)
            sys.exit(1)
        print(content)

    elif args.command == "create":
        if args.file:
            with open(args.file) as f:
                content = f.read()
        else:
            content = args.content
        result = client.create_note(args.path, content)
        print(json.dumps(result, indent=2))

    elif args.command == "search":
        results = client.search(args.query)
        print(json.dumps(results, indent=2))

    elif args.command == "ingest-source":
        path = client.ingest_source_note(
            title=args.title,
            authors=list(args.authors),
            year=args.year,
            doi=args.doi,
            tags=list(args.tags),
            abstract=args.abstract,
            claims=list(args.claims),
        )
        print(json.dumps({"created": path}, indent=2))

    elif args.command == "quick-capture":
        path = client.quick_capture(args.content)
        print(json.dumps({"created": path}, indent=2))

    elif args.command == "delete":
        result = client.delete_note(args.path)
        print(json.dumps(result, indent=2))

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
