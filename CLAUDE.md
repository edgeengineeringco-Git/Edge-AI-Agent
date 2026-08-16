# Project Structure

This is a [thepopebot](https://github.com/stephengpope/thepopebot) project.

## Directories

- **`agent-job/`** — Agent job configuration: system prompt (`SYSTEM.md`), heartbeat prompt, and cron schedules (`CRONS.json`).
- **`coding-workspace/`** — Optional system prompt (`SYSTEM.md`) for code mode workspaces. Empty by default.
- **`agents/`** — Custom agent definitions. Each subdirectory defines an agent (see Managing Agents below).
- **`event-handler/`** — Event handler configuration: chat system prompts, trigger definitions (`TRIGGERS.json`), cluster templates, and LiteLLM proxy config.
- **`skills-library/`** — Canonical skill source. All `SKILL.md` files and scripts live here.
- **`skills/`** — Activation surface. Each entry is a symlink to `../skills-library/<name>` — present means active, absent means deactivated. Coding agents only see skills symlinked here.
- **`data/`** — Runtime data (SQLite database, cluster state). Not checked into git.
- **`logs/`** — Agent job logs, organized by job ID. Not checked into git.

## Files

- **`docker-compose.yml`** — Container definitions for the event handler and LiteLLM proxy. Managed — do not edit.
- **`docker-compose.custom.yml`** — Your Docker Compose overrides. Merged with the main compose file.
- **`.env`** — Environment variables (API keys, secrets). Never committed to git.

## Managed Files

Some files are auto-synced by `npx thepopebot init` and will be overwritten on every init/upgrade. Do not edit these:

- `.github/workflows/` — CI/CD workflows
- `docker-compose.yml`
- `.dockerignore`
- `.gitignore`

The `CLAUDE.md` files scattered through the project tree (e.g. `agent-job/CLAUDE.md`, `agents/CLAUDE.md`, `event-handler/CLAUDE.md`, `skills/CLAUDE.md`, `skills-library/CLAUDE.md`) are scaffolded by `init` from `*.template` sources but are **not** in the managed-paths list — they will not be overwritten if you have edited them. Run `npx thepopebot reset <path>` to restore one to its template default, or `npx thepopebot diff <path>` to see your local changes.

## Agent Scoping

Agents can be scoped to subdirectories within the repository. When a chat is launched with a scope (e.g., `agents/gary-vee`), the coding agent runs with that directory as its working directory.

### Directory Structure

```
agents/
  gary-vee/
    CLAUDE.md         ← agent-specific context (optional)
    SYSTEM.md         ← agent-specific system prompt (optional)
    skills/           ← agent-specific skills (optional, overrides root skills/ for this scope)
      agent-job-secrets → ../../../skills-library/agent-job-secrets  (symlink)
      custom-skill/
```

### How Scoping Works

- **Working directory** — The agent's cwd is set to the scoped directory. It still has access to the full repo.
- **Skills** — If the scoped directory has a `skills/` folder, those skills are used. If not, the root `skills/` folder is used as a fallback. Sub-agent skills can symlink back to entries in the canonical `skills-library/` (e.g. `agents/<name>/skills/agent-job-secrets → ../../../skills-library/agent-job-secrets`).
- **CLAUDE.md** — The coding agent automatically picks up `.claude/` and `CLAUDE.md` files relative to its working directory.
- **Default scope** — When no scope is selected, the agent runs from the repository root with root-level skills.

## Agent Organization Rules

**CRITICAL: Each agent is a SEPARATE, SELF-CONTAINED directory. Never mix code from different agents.**

### Creating a New Agent

1. **Always create a new directory:** `agents/<new-agent-name>/`
2. **Never add new code to an existing agent** unless it belongs there
3. **Each agent gets its own:**
   - `SYSTEM.md` — Agent identity and instructions
   - `CLAUDE.md` — Agent-specific context
   - `jobs/` — Job task prompts
   - `skills/` — Agent-specific skill symlinks (optional)
4. **Update root `CLAUDE.md`** — Add the new agent to the Agents section below

### Existing Agents (DO NOT mix these)

| Agent | Purpose | Directory |
|-------|---------|----------|
| `edge-kuth-portal` | K/U/Th gamma-ray spectral analysis (.spc files) | `agents/edge-kuth-portal/` |
| `terrestrial-dose` | Irish Terrestrial Dose Indicator — Ireland-only, real WMS data sources (FastAPI + React) | `agents/terrestrial-dose/` |
| `edge-critical-minerals` | Weekly critical minerals intel briefing | `agents/edge-critical-minerals/` |
| `edge-smart-video` | LinkedIn video content generation | `agents/edge-smart-video/` |
| `geosync-expert` | Geochemical survey processing (REE) | `agents/geosync-expert/` |
| `ree-obsidian-brain` | REE knowledge vault curation | `agents/ree-obsidian-brain/` |

### What NOT to Do

- ❌ Add terrestrial-dose code to edge-kuth-portal
- ❌ Add edge-kuth-portal code to terrestrial-dose
- ❌ Mix unrelated agent code in the same directory
- ❌ Create agents without their own SYSTEM.md and CLAUDE.md

### What TO Do

- ✅ Create `agents/<new-agent>/` with its own SYSTEM.md, CLAUDE.md, jobs/
- ✅ Keep each agent focused on ONE purpose
- ✅ Update root CLAUDE.md when adding new agents
- ✅ Use skills/ symlinks for shared capabilities

## Agents

### edge-critical-minerals

The **EDGE Critical Minerals Intel Agent** runs every Monday at 08:00 Ireland time. It autonomously researches and generates a weekly intelligence briefing covering funding, events, policy, and R&D opportunities for critical minerals prospecting (REE, K-Th-U).

- Agent directory: `agents/edge-critical-minerals/`
- Cron entry: `edge-weekly-critical-minerals` in `agent-job/CRONS.json`
- Pipeline: Research (web search) → HTML report → Google Drive upload → Telegram notification

```
agents/edge-critical-minerals/
├── SYSTEM.md
├── CLAUDE.md
├── jobs/
│   └── weekly-report.md
└── reports/
    └── YYYY-MM-DD-weekly-report.md
```

### edge-kuth-portal

EDGE K/U/Th Portal — gamma-ray spectral analysis pipeline. Processes .spc files and returns K/U/Th concentration results. Runs natively in thepopebot as a scoped agent — no separate servers or containers needed.

**Processing happens IMMEDIATELY on webhook trigger** — no cron batch delays.

- **Scope:** `agents/edge-kuth-portal`
- **Upload endpoint:** `/edge-kuth/upload-page` (Traefik → upload-server Docker container)
- **Webhook trigger:** `/edge-kuth/upload` (TRIGGERS.json, **enabled**) — fires agent on upload server callback
- **Flow:** Client form POSTs multipart → upload server saves files → triggers agent → agent runs Python → Telegram broadcast
- **Telegram:** Results CSV broadcast to all admins via `agent-job-dm` skill
- **Skill:** `edge-kuth-analysis` — invocable by any agent

```
agents/edge-kuth-portal/
├── SYSTEM.md
├── CLAUDE.md
├── skills/
│   ├── agent-job-dm → ../../../skills-library/agent-job-dm
│   └── edge-kuth-analysis → ../../../skills-library/edge-kuth-analysis
└── jobs/
    └── process-spectra.md
```

### terrestrial-dose

**Irish Terrestrial Dose Indicator** — commercial-grade interactive web application estimating terrestrial radiation dose (radon, thoron, gamma) for every point in Ireland at 100m resolution. Built for MDPI Air journal special issue "Radon in the Environment". EU BSS 2013/59/Euratom compliant. v5.0 — complete rebuild per spec.

- **Scope:** `agents/terrestrial-dose`
- **System prompt:** `agents/terrestrial-dose/SYSTEM.md`
- **Source:** https://github.com/edgeengineeringco-Git/edge-ai-agent-site/tree/main/terrestrial-dose
- **Live:** https://edgeengineeringco-git.github.io/edge-ai-agent-site/irish-dose.html

**Architecture:**
- **Backend** (`api/dose_backend.py`, 657 lines): FastAPI with real GeoTIFF raster loading
  - RasterLayer class for sampling bedrock, Tellus K/U/Th, EPA radon, Teagasc soils
  - Named constants for all physical values (UNSCEAR/ICRP cited)
  - Derivation strings for every computed number
  - TTLCache for computed responses
  - Honest missing-data handling (null, not guesses)
- **Frontend** (`irish-dose-standalone.html`, 635 lines): Two-pane layout
  - MapLibre satellite basemap + Bing/Streets toggle
  - Cursor triangle (SVG) with proportional arms
  - Hover interaction (100ms debounce) → real API calls
  - Click-to-pin, risk choropleth overlay, search bar
  - Report: fingerprint triangle, factors table, confidence meter
  - Data source badges, provenance footer, derivation panel

**Data sources (real rasters, all optional):**
- GSI Bedrock 1:100k → lithology backbone
- Tellus radiometric K/U/Th → measured activities
- EPA Radon Risk → radon zone validation
- Teagasc Soils → permeability
- GSI Faults → fault proximity
- Corine Land Cover, Sentinel-2 NDVI, ESA CCI (optional)

```
agents/terrestrial-dose/
├── api/dose_backend.py            # FastAPI backend (THE MAIN API)
├── dose_core/dose_calculation_core.py  # Core dose formulas (legacy/tests)
├── irish-dose-standalone.html     # Frontend HTML (deployed)
├── data/                          # Runtime raster data (not committed)
│   ├── gsi_bedrock_100k.tif
│   ├── tellus_radiometric_k.tif
│   ├── tellus_radiometric_u.tif
│   ├── tellus_radiometric_th.tif
│   ├── epa_radon_map.tif
│   ├── teagasc_soil_permeability.tif
│   ├── gsi_faults.geojson
│   └── era5_season.json
├── tests/test_dose_core.py
├── Dockerfile
├── requirements.txt
├── SYSTEM.md
├── CLAUDE.md
└── README.md
```

### edge-smart-video

EDGE Smart Video Content Agent — LinkedIn-ready video content from a topic queue. Generates LinkedIn posts via LLM, produces a professional text-first HTML video slideshow with structured slide content, and optionally generates Veo 3.1 AI video clips.

- **Scope:** `agents/edge-smart-video`
- **Schedule:** Wednesdays at 10:00 AM (cron: `0 10 * * 3`)
- **System prompt:** `agents/edge-smart-video/SYSTEM.md`
- **Jobs:** `agents/edge-smart-video/jobs/generate-content.md`
- **Pipeline:** Topic fetch → Post + slide generation → Optional images/Veo → HTML video composition → Drive upload → Telegram delivery
- **Primary output:** Self-contained HTML slideshow (`video.html`) — no API keys or external dependencies needed

```
agents/edge-smart-video/
├── SYSTEM.md
├── CLAUDE.md
├── scripts/
│   ├── compose_video.py      # Professional HTML video slideshow (primary output)
│   ├── generate_images.py    # Pollinations (free) or Nano Banana (Gemini) backend
│   ├── generate_video.py     # Veo 3.1 AI video generation
│   ├── sheets_handler.py     # Google Sheets topic queue CRUD
│   └── drive_upload.py       # Google Drive upload of generated assets
├── jobs/
│   └── generate-content.md
├── input/
│   └── topics.csv            # Local topic queue (fallback)
├── skills/
│   └── agent-job-dm → ../../../skills-library/agent-job-dm
└── output/
    └── YYYY-MM-DD-topic/     # Generated assets per run
```

### geosync-expert

**GeoSync Expert** — geochemical survey processing pipeline for REE prospecting. Processes pXRF / gamma-ray / ICP-MS CSV data through QC → anomaly detection → resource estimation → HTML report generation. Triggered on schedule or manually.

- **Scope:** `agents/geosync-expert`
- **Cron:** `geosync-process-survey` in `agent-job/CRONS.json` (disabled by default)
- **System prompt:** `agents/geosync-expert/SYSTEM.md`
- **Jobs:** `agents/geosync-expert/jobs/process-survey.md`
- **Pipeline:** Raw CSV → QC gate → TREO/HREO computation → DBSCAN clustering → deposit classification → resource estimate → risk matrix → HTML report → Telegram notification
- **Skills:** `geochem-qc`, `geochem-anomaly`, `geochem-resource`, `geochem-pipeline`, `critical-minerals-ref`, `geochem-exploration` (all root skills, inherited by scope)

```
agents/geosync-expert/
├── SYSTEM.md
├── CLAUDE.md
├── jobs/
│   └── process-survey.md
└── (data + reports written to data/ and reports/ at repo root)
```

### ree-obsidian-brain

**REE Obsidian Brain** — scientific knowledge curator and research librarian for Rare Earth Element critical minerals. Maintains an Obsidian-compatible Markdown vault designed to be opened in Obsidian desktop or mobile.

- **Scope:** `agents/ree-obsidian-brain`
- **Weekly curation:** `ree-obsidian-curate` in `agent-job/CRONS.json` (Sundays at 09:00)
- **Monthly update:** `ree-obsidian-monthly-update` in `agent-job/CRONS.json` (1st of every month at 09:00) — creates dated folder in user's Google Drive, zips vault, uploads ZIP
- **System prompt:** `agents/ree-obsidian-brain/SYSTEM.md`
- **Jobs:** `agents/ree-obsidian-brain/jobs/curate-vault.md`
- **Pipeline:** Inbox processing → source note creation → atomic claim extraction → wiki-link curation → MOC updates → integrity check → Telegram notification
- **Skills:** Inherits root skills (`ree-database`, `critical-minerals-ref`, `agent-job-dm`)
- **Universal write:** Any agent can write to the vault via the `ree-vault-write` skill. Just ask: *"Save this to my REE vault"*

```
agents/ree-obsidian-brain/
├── SYSTEM.md
├── CLAUDE.md
├── jobs/
│   └── curate-vault.md
└── vault/
    ├── 00-Inbox/              ← drop new papers/sources here
    ├── 01-Sources/            ← processed bibliographic notes
    ├── 02-Elements/           ← 17 lanthanides + Sc + Y (seeded)
    ├── 03-Deposits/           ← carbonatite, IAC, hydrothermal, placer
    ├── 04-Processing/         ← beneficiation, leaching, SX, refining
    ├── 05-Markets/            ← prices, demand, supply chain
    ├── 06-Exploration/        ← methods, pathfinders, case studies
    ├── 07-Projects/           ← specific mines worldwide
    ├── 08-Concepts/           ← geochemical principles
    ├── 09-Maps-of-Content/    ← index hubs (MOCs)
    └── Templates/             ← source, element, project templates
```

## Skills

### edge-kuth-analysis

K/U/Th spectral analysis skill. Any agent can invoke this skill for instructions on running the estimation engine. See `skills-library/edge-kuth-analysis/SKILL.md` for details.

### geochem-qc

Automated QC validation for geochemical CSV data. Returns PASS / CONDITIONAL / FAIL based on structure, CRM recovery, duplicate RPD, range bounds, and IQR outlier detection. See `skills-library/geochem-qc/SKILL.md`.

### geochem-anomaly

Spatial anomaly clustering (DBSCAN, median + 3×MAD threshold) and deposit-type classification (carbonatite / ion-adsorption clay / hydrothermal HREE / placer monazite) from REE patterns. See `skills-library/geochem-anomaly/SKILL.md`.

### geochem-resource

Quick resource estimation (tonnage, contained TREO/CREO, JORC-aligned confidence tier, economic status) and geological/analytical/economic risk matrix with recommendations. See `skills-library/geochem-resource/SKILL.md`.

### geochem-pipeline

End-to-end geochemical processing — moisture/matrix correction, TREO/HREO/CREO computation, CSV + JSON summary output, and HTML report generation via Jinja2. See `skills-library/geochem-pipeline/SKILL.md`.

### critical-minerals-ref

Pure reference — REE element tables, deposit-type TREO ranges, pathfinder elements, Li/Co/Cu/Ni/W occurrence patterns and cut-off grades, multi-commodity associations. See `skills-library/critical-minerals-ref/SKILL.md`.

### geochem-exploration

Pure reference — sampling best practices, grid spacing guidelines, field QA/QC checklist, and continue vs. cease decision criteria. See `skills-library/geochem-exploration/SKILL.md`.

### drone-survey

Aerial survey planning and interpretation for REE and critical minerals — platform selection (multirotor / fixed-wing / hybrid VTOL), sensor specs (gamma / pXRF / hyperspectral / LiDAR), flight grid design, weather constraints, cost analysis, data processing workflows, regulatory framework, and troubleshooting. See `skills-library/drone-survey/SKILL.md`.

### ore-grade

Ore grade economic assessment — confidence tier verification, uncertainty ranges, tonnage and contained metal, cut-off grade assessment with HREE premium, JORC-aligned resource classification, 3-axis risk matrix, and regulation-safe reporting language. See `skills-library/ore-grade/SKILL.md`.

### ree-database

Comprehensive REE reference — full 17-element lanthanide data (crustal abundance, ionic radii, electron configuration, magnetic properties, redox chemistry), market prices and correlations, global production and reserve statistics, processing and separation technologies, substitutability matrix, magnet specifications, environmental radioactivity, and 2025–2035 demand scenarios. See `skills-library/ree-database/SKILL.md`.

### spectral-interpret

Gamma-ray and pXRF spectral interpretation — data quality assessment, background characterization, REE pattern analysis, chondrite normalization, Ce/Eu anomaly interpretation, deposit-type fingerprinting, and radiometric ratio analysis (Th/U, F-parameter). See `skills-library/spectral-interpret/SKILL.md`.

### ree-vault-write

Universal vault write skill — any agent or chat can save scientific notes, papers, or data directly to the REE Obsidian Brain vault. Creates properly formatted Markdown with YAML frontmatter, wiki-links, and tags. See `skills-library/ree-vault-write/SKILL.md`.

**Usage from any chat**: *"Save this paper to the REE vault"* or *"Add this to my Obsidian brain"*

## Security Note

The original n8n workflow used a hardcoded password (`Edge12345`). This thepopebot-native deployment handles auth through the platform's standard webhook authentication and agent scoping. No credentials are embedded in code.

