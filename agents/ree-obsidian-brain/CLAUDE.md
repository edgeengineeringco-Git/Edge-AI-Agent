# REE Obsidian Brain — Agent Documentation

## Purpose

The REE Obsidian Brain is a knowledge-management agent that maintains an Obsidian-compatible Markdown vault for Rare Earth Element critical minerals research. The vault is designed to be cloned/synced to a local Obsidian installation.

## ⚠️ CRITICAL: Vault Git Setup

The vault lives in its own GitHub repo: **`Edge-Obsidian-Brain`**

```
Repo:   https://github.com/edgeengineeringco-Git/Edge-Obsidian-Brain
Branch: main
Token:  embedded in vault-setup.sh (committed to Edge-AI-Agent repo)
```

**Run `vault-setup.sh` before touching the vault:**

```bash
bash agents/ree-obsidian-brain/vault-setup.sh
```

This configures git credentials, sets the remote URL, and pulls latest. **`Edge-Obsidian-Brain` is the ONLY repo for Obsidian. Never push vault changes to `Edge-AI-Agent`.**

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
- **attachments** — PDFs, Excel, images (large files gitignored, see `.gitignore`)
- **Templates** — `Source Template.md`, `Element Template.md`, `Project Template.md`.

## Attachments Folder

`vault/attachments/` is where the user drops PDFs, Excel, images, etc.

- **Images** (`.png`, `.jpg`, `.svg`) → synced to GitHub ✅
- **Large files** (`.pdf`, `.xlsx`, `.docx`) → gitignored, NOT synced via GitHub
- **For large files**: upload to Google Drive and link from notes

The `attachments/.gitignore` allows images through but blocks large binaries.

## Obsidian Compatibility

- YAML frontmatter (Obsidian reads natively)
- WikiLinks `[[...]]` (Obsidian-native)
- Tags in YAML `tags:` or inline `#tag`
- Mermaid diagrams supported in Obsidian
- No plugins required (plain Markdown vault)

## Sync Workflow (Obsidian Git)

1. **Agent runs `vault-setup.sh`** → configures token, pulls latest from `Edge-Obsidian-Brain`
2. User opens Obsidian → Git plugin **auto-pulls** latest from GitHub on boot
3. User writes notes, adds papers → **Git commit + push** from Obsidian
4. Agent sees changes on next run → curates, links, updates MOCs
5. Agent commits to **Edge-Obsidian-Brain** repo
6. User opens Obsidian → Git **auto-pulls** new agent changes

### Plugins Installed
- **Dataview** (v0.5.70) — pre-bundled, frontmatter queries
- **Obsidian Git** — auto-pull on boot, manual push
- **Obsidian Local REST API** — exposes vault via HTTP at `localhost:27124` for agent integration
- **Omni Search** — full-text search with `Ctrl/Cmd + O`

## User Delivery Protocol

**CRITICAL — Every vault update must follow this:**

1. **Run `vault-setup.sh`** → configures git access and pulls latest
2. **Make changes** to the vault
3. **Commit + push to Edge-Obsidian-Brain**:
   ```bash
   cd agents/ree-obsidian-brain/vault
   git add -A
   git commit -m "vault: <description>"
   git push origin main
   ```
4. **Create a dated folder** inside the user's Google Drive folder: `1TeA2-iAs5QLYK1cpT8HWbMeDAxWFHUf7`
   - Folder name format: `YYYY-MM-DD`
5. **Upload the vault ZIP** to that dated folder — BACKUP/ARCHIVE

**Git sync is primary. Google Drive dated folder is backup. Do both every time.**

## Cron Jobs

| Name | Schedule | Purpose |
|------|----------|---------|
| `ree-obsidian-curate` | Sundays 09:00 | Weekly curation — process inbox, curate links, update MOCs |
| `ree-obsidian-monthly-update` | 1st of month 09:00 | Monthly — curate + ZIP + upload to dated Drive folder + Telegram |

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

## Adding Content

Drop Markdown files or PDF references into `vault/00-Inbox/`. The agent will:
1. Extract metadata (title, authors, DOI if present)
2. Create a source note in `01-Sources/`
3. Extract atomic claims and link them to element/deposit/concept notes
4. Clear the inbox

For large attachments (PDFs, Excel), use `vault/attachments/`.
