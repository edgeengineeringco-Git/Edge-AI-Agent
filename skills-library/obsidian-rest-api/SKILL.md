# Obsidian REST API

Connect to the user's running Obsidian instance via the Local REST API plugin to read, create, and manage vault notes in real time. This skill is available to **any agent** that has it symlinked in its `skills/` directory.

## Prerequisites

- User has **Obsidian Local REST API** plugin installed and enabled in their Obsidian vault
- Plugin is running (Obsidian app is open)
- API key is stored as an agent job secret named `OBSIDIAN_API_KEY`
- `pip install requests` is available in the Python environment

## Files

| Purpose | Path |
|---------|------|
| Python client | `agents/ree-obsidian-brain/obsidian-client/obsidian_client.py` |
| Requirements | `agents/ree-obsidian-brain/obsidian-client/requirements.txt` |
| Vault plugin config | `agents/ree-obsidian-brain/vault/.obsidian/plugins/obsidian-local-rest-api/data.json` |

## Usage

### 1. Ping (check if Obsidian is running)

```bash
python3 agents/ree-obsidian-brain/obsidian-client/obsidian_client.py \
  --key "$OBSIDIAN_API_KEY" ping
```

Returns `{"reachable": true}` if the REST API is online.

### 2. List all vault notes

```bash
python3 agents/ree-obsidian-brain/obsidian-client/obsidian_client.py \
  --key "$OBSIDIAN_API_KEY" list
```

### 3. Read a note

```bash
python3 agents/ree-obsidian-brain/obsidian-client/obsidian_client.py \
  --key "$OBSIDIAN_API_KEY" get "02-Elements/Neodymium.md"
```

### 4. Create a new note

```bash
python3 agents/ree-obsidian-brain/obsidian-client/obsidian_client.py \
  --key "$OBSIDIAN_API_KEY" create "01-Sources/My Paper.md" \
  --content "# My Paper\n\nContent here"
```

### 5. Search the vault

```bash
python3 agents/ree-obsidian-brain/obsidian-client/obsidian_client.py \
  --key "$OBSIDIAN_API_KEY" search "carbonatite"
```

### 6. Ingest a scientific source (REE-specific)

```bash
python3 agents/ree-obsidian-brain/obsidian-client/obsidian_client.py \
  --key "$OBSIDIAN_API_KEY" ingest-source \
  --title "Geochemistry of the Mountain Pass carbonatite" \
  --authors "Smith J" "Doe A" \
  --year 2024 \
  --doi "10.1016/j.chemgeo.2024.123456" \
  --tags "carbonatite" "California" \
  --abstract "This paper presents new geochemical data..." \
  --claims "TREO grades average 8.5%" "HREE proportion is 12% of total"
```

### 7. Quick capture (drop into inbox)

```bash
python3 agents/ree-obsidian-brain/obsidian-client/obsidian_client.py \
  --key "$OBSIDIAN_API_KEY" quick-capture "Check out paper on ion-adsorption clays"
```

## Integration with the Agent

**When to use this skill:**

1. **User asks "what's in my vault?"** — Use `list` or `search` to answer in real time
2. **User says "save this paper"** — Use `ingest-source` to create a properly formatted source note
3. **User asks "what do I have on X?"** — Use `search` to find relevant notes
4. **During curation** — Use the client to create/link notes directly in the running Obsidian instance
5. **Quick capture** — Use `quick-capture` to save ideas the user wants to process later

**Python API (for inline use):**

```python
import sys
sys.path.insert(0, "agents/ree-obsidian-brain/obsidian-client")
from obsidian_client import ObsidianClient

client = ObsidianClient(api_key="key-from-secret")
if client.ping():
    notes = client.list_notes()
    client.ingest_source_note(...)
```

## Best Practices

- Always `ping` first to verify Obsidian is running before other operations
- If the REST API is unreachable, fall back to direct file writes into the vault directory
- Use `ingest-source` for scientific papers (it handles frontmatter + linking)
- Use `quick-capture` for ephemeral notes that need curation later
- Keep note paths consistent with the vault directory structure:
  - `00-Inbox/` — unprocessed captures
  - `01-Sources/` — bibliographic notes
  - `02-Elements/` — element data
  - `03-Deposits/` — deposit profiles
  - `04-Processing/` — processing methods
  - `05-Markets/` — market data
  - `06-Exploration/` — exploration
  - `07-Projects/` — project profiles
  - `08-Concepts/` — geochemical concepts
  - `09-Maps-of-Content/` — MOC hub notes
