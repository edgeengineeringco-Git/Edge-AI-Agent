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

1. Clone/pull this repo locally
2. Open `agents/ree-obsidian-brain/vault/` as an Obsidian vault
3. Install optional plugins: Dataview (for frontmatter queries), Graph Analysis
4. The vault works out of the box without plugins

## Cron Job

- **Name**: `ree-obsidian-curate`
- **Schedule**: Sundays at 09:00 (weekly curation)
- **Job**: Read `jobs/curate-vault.md` and execute autonomously
- **Status**: Enabled — processes inbox, curates links, updates MOCs

## Skills

Inherits root skills automatically (no `skills/` folder needed). Key skills used:
- `ree-database` — element data, market prices, processing tech
- `critical-minerals-ref` — deposit types, pathfinders, cut-off grades
- `agent-job-dm` — Telegram notifications when curation completes

## Adding Content

Drop Markdown files or PDF references into `vault/00-Inbox/`. The agent will:
1. Extract metadata (title, authors, DOI if present)
2. Create a source note in `01-Sources/`
3. Extract atomic claims and link them to element/deposit/concept notes
4. Clear the inbox

## Maintenance

- Keep `02-Elements/` notes evergreen — update prices annually
- Expand `07-Projects/` as new developments occur
- `09-Maps-of-Content/` should be regenerated if the graph topology changes significantly
