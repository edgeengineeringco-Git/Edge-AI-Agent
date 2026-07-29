# REE Obsidian Brain — Agent Documentation

## Purpose

The REE Obsidian Brain is a knowledge-management agent that maintains an Obsidian-compatible Markdown vault for Rare Earth Element critical minerals research. The vault is designed to be cloned/synced to a local Obsidian installation.

## Vault Structure

The vault at `vault/` follows the Johnny.Decimal-inspired Zettelkasten hybrid:

- **00-Inbox** — Unprocessed material. The agent empties this on each run.
- **01-Sources** — Bibliographic notes. One per paper/report. DOI in frontmatter.
- **02-Elements** — 17 lanthanide element notes + Sc + Y. Seed data from `ree-database` skill.
- **03-Deposits** — Deposit-type profiles with TREO ranges, pathfinders, key minerals.
- **04-Processing** — Beneficiation, leaching, SX, refining flowsheets.
- **05-Markets** — Price data, demand scenarios, supply-chain risk.
- **06-Exploration** — Field methods, QA/QC, grid design, drone surveys.
- **07-Projects** — Mine/exploration project profiles (Mountain Pass, Bayan Obo, etc.).
- **08-Concepts** — Geochemical principles, anomalies, normative calculations.
- **09-Maps-of-Content** — Hub notes. `MOC — REE Master Index` is the entry point.
- **Templates** — `Source Template.md`, `Element Template.md`, `Project Template.md`.

## Obsidian Compatibility

- YAML frontmatter (Obsidian reads natively)
- WikiLinks `[[...]]` (Obsidian-native)
- Tags in YAML `tags:` or inline `#tag`
- Mermaid diagrams supported in Obsidian
- No plugins required (plain Markdown vault)

## How to Use with Obsidian

The vault is its own git repo at **https://github.com/edgeengineeringco-Git/Edge-Obsidian-Brain**. The user opens this repo directly as their Obsidian vault.

### Sync Workflow (Obsidian Git)
1. User opens Obsidian → Git plugin **auto-pulls** latest updates from GitHub on boot
2. User writes notes, adds papers → **Git commit + push** from Obsidian
3. Agent sees changes on next run → curates, links, updates MOCs
4. Agent commits to **Edge-Obsidian-Brain** repo (`cd agents/ree-obsidian-brain/vault && git push`)
5. User opens Obsidian → Git **auto-pulls** new agent changes

### Plugins Installed
- **Dataview** (v0.5.70) — pre-bundled, frontmatter queries
- **Obsidian Git** — auto-pull on boot, manual push
- **Obsidian Local REST API** — exposes vault via HTTP at `localhost:27124` for agent integration
- **Omni Search** — full-text search with `Ctrl/Cmd + O`

## User Delivery Protocol

**CRITICAL — Future updates must follow this exactly:**

1. **Commit + push to the Edge-Obsidian-Brain repo** from `agents/ree-obsidian-brain/vault/` (this is the PRIMARY sync method)
2. **Create a dated folder** inside the user's Google Drive folder: `https://drive.google.com/drive/folders/1TeA2-iAs5QLYK1cpT8HWbMeDAxWFHUf7`
   - Folder name format: `YYYY-MM-DD` (e.g., `2026-07-29`)
3. **Upload the vault ZIP** to that dated folder
4. **Also commit to GitHub** as usual

**The user uses Git sync as primary. The dated Google Drive folder is a backup/archive.**

**Do NOT skip the dated folder step. The user expects every update in a dated folder.**

## Cron Job

- **Name**: `ree-obsidian-curate`
- **Schedule**: Sundays at 09:00 (weekly curation)
- **Job**: Read `jobs/curate-vault.md` and execute autonomously
- **Status**: Enabled — processes inbox, curates links, updates MOCs

## Skills

Scoped skills in `skills/` (override root):
- `obsidian-rest-api` — real-time vault access via Obsidian Local REST API plugin when user's Obsidian is open

Inherits root skills automatically. Key root skills used:
- `ree-database` — element data, market prices, processing tech
- `critical-minerals-ref` — deposit types, pathfinders, cut-off grades
- `agent-job-dm` — Telegram notifications when curation completes
- `agent-job-secrets` — fetches `OBSIDIAN_API_KEY` for REST API auth

## Obsidian REST API Tooling

Located at `obsidian-client/obsidian_client.py` — a Python CLI and library for interacting with the user's running Obsidian instance.

| Command | Purpose |
|---------|---------|
| `ping` | Check if Obsidian REST API is reachable |
| `list` | List all vault notes |
| `get <path>` | Read a note's content |
| `create <path> --content` | Create a new note |
| `search <query>` | Full-text search across vault |
| `ingest-source` | Create a scientific source note with frontmatter + claims |
| `quick-capture <text>` | Drop content into inbox for later processing |

**Secret needed:** `OBSIDIAN_API_KEY` — the API key from the Obsidian Local REST API plugin settings. Store this via the `agent-job-secrets` skill.

## Adding Content

Drop Markdown files or PDF references into `vault/00-Inbox/`. The agent will:
1. Extract metadata (title, authors, DOI if present)
2. Create a source note in `01-Sources/`
3. Extract atomic claims and link them to element/deposit/concept notes
4. Clear the inbox

**Real-time option:** If Obsidian is open on the user's desktop, the agent can use the REST API (via `obsidian_client.py`) to create notes directly — they appear in Obsidian instantly without waiting for a Git sync.

## Maintenance

- Keep `02-Elements/` notes evergreen — update prices annually
- Expand `07-Projects/` as new developments occur
- `09-Maps-of-Content/` should be regenerated if the graph topology changes significantly
