#!/usr/bin/env python3
"""
Obsidian Local REST API Client for the REE Obsidian Brain.

Connects to the Obsidian Local REST API plugin running on the user's desktop.
Provides vault CRUD, search, and REE-specific scientific source ingestion.

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
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import requests


class ObsidianClient:
    """Client for the Obsidian Local REST API plugin."""

    def __init__(self, api_key: Optional[str] = None, port: int = 27124, host: str = "localhost"):
        self.api_key = api_key or os.environ.get("OBSIDIAN_API_KEY", "")
        self.base_url = f"http://{host}:{port}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------ #
    #  Core helpers
    # ------------------------------------------------------------------ #

    def _get(self, path: str, params: dict = None) -> requests.Response:
        url = f"{self.base_url}{path}"
        return requests.get(url, headers=self.headers, params=params)

    def _put(self, path: str, data: dict = None) -> requests.Response:
        url = f"{self.base_url}{path}"
        return requests.put(url, headers=self.headers, json=data or {})

    def _post(self, path: str, data: dict = None) -> requests.Response:
        url = f"{self.base_url}{path}"
        return requests.post(url, headers=self.headers, json=data or {})

    def _delete(self, path: str) -> requests.Response:
        url = f"{self.base_url}{path}"
        return requests.delete(url, headers=self.headers)

    def _check(self, resp: requests.Response) -> dict:
        """Check response and return JSON body."""
        try:
            resp.raise_for_status()
            return resp.json() if resp.content else {}
        except requests.exceptions.RequestException as e:
            print(f"API error: {e}", file=sys.stderr)
            if resp.text:
                print(f"Response: {resp.text[:500]}", file=sys.stderr)
            raise

    # ------------------------------------------------------------------ #
    #  Health / status
    # ------------------------------------------------------------------ #

    def ping(self) -> bool:
        """Check if the REST API is reachable."""
        try:
            resp = self._get("/")
            return resp.status_code == 200
        except requests.exceptions.ConnectionError:
            return False

    # ------------------------------------------------------------------ #
    #  Vault CRUD
    # ------------------------------------------------------------------ #

    def list_notes(self) -> list[dict]:
        """List all notes in the vault (recursive)."""
        return self._check(self._get("/vault/"))

    def get_note(self, path: str) -> Optional[str]:
        """Read a note by its vault path (e.g. '02-Elements/Neodymium.md')."""
        encoded = quote(path, safe="")
        resp = self._get(f"/vault/{encoded}")
        if resp.status_code == 404:
            return None
        self._check(resp)
        return resp.text

    def note_exists(self, path: str) -> bool:
        """Check if a note exists at the given path."""
        return self.get_note(path) is not None

    def create_note(self, path: str, content: str) -> dict:
        """Create a new note. Returns the API response."""
        encoded = quote(path, safe="")
        return self._check(self._put(f"/vault/{encoded}", {"content": content}))

    def update_note(self, path: str, content: str) -> dict:
        """Overwrite an existing note."""
        encoded = quote(path, safe="")
        return self._check(self._put(f"/vault/{encoded}", {"content": content}))

    def delete_note(self, path: str) -> dict:
        """Delete a note."""
        encoded = quote(path, safe="")
        return self._check(self._delete(f"/vault/{encoded}"))

    # ------------------------------------------------------------------ #
    #  Search
    # ------------------------------------------------------------------ #

    def search(self, query: str, context_length: int = 100) -> list[dict]:
        """Full-text search across the vault. Returns list of {filename, match, context}."""
        return self._check(self._post("/search", {
            "query": query,
            "contextLength": context_length,
        }))

    # ------------------------------------------------------------------ #
    #  Commands
    # ------------------------------------------------------------------ #

    def list_commands(self) -> list[dict]:
        """List all available Obsidian commands."""
        return self._check(self._get("/commands"))

    def execute_command(self, command_id: str) -> dict:
        """Execute an Obsidian command by ID (e.g. 'editor:insert-link')."""
        return self._check(self._post(f"/commands/{quote(command_id, safe='')}"))

    # ------------------------------------------------------------------ #
    #  Daily / periodic notes
    # ------------------------------------------------------------------ #

    def get_daily_note(self) -> Optional[str]:
        """Get today's daily note content."""
        resp = self._get("/daily")
        if resp.status_code == 404:
            return None
        return self._check(resp).get("content", "")

    # ------------------------------------------------------------------ #
    #  Active note
    # ------------------------------------------------------------------ #

    def get_active_note(self) -> Optional[dict]:
        """Get the currently active note in Obsidian."""
        resp = self._get("/active")
        if resp.status_code == 404:
            return None
        return self._check(resp)

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
        safe_title = title.replace(":", " -").replace("/", "-").replace("?", "")
        filename = f"{safe_title[:120]}.md"
        vault_path = f"01-Sources/{filename}"

        # Build frontmatter
        frontmatter = {
            "title": title,
            "authors": authors,
            "year": year,
            "date_created": __import__("datetime").date.today().isoformat(),
            "date_modified": __import__("datetime").date.today().isoformat(),
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
        import datetime
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
