# agents/ — Custom Agent Definitions

## Active Agents

### edge-critical-minerals

The EDGE Weekly Critical Minerals Intel pipeline. Runs every Monday at 08:00 Ireland time. See `agents/edge-critical-minerals/CLAUDE.md` for full documentation.

- **Cron**: `edge-weekly-critical-minerals` in `agent-job/CRONS.json`
- **Job**: `agents/edge-critical-minerals/jobs/weekly-report.md`
- **System prompt**: `agents/edge-critical-minerals/SYSTEM.md`
- **Skills**: Inherits root skills (agent-job-dm, agent-job-secrets, google-drive-upload)
- **Secrets needed**: `GOOGLE_DRIVE_OAUTH` (OAuth refresh token JSON — client_id, client_secret, refresh_token)

### ireland-geospatial-opportunities

Ireland-only opportunities agent for remote sensing, GIS, UAV/UAS, photogrammetry, LiDAR and related academic/industry roles. Runs twice weekly (Monday and Thursday at 08:00 Europe/Dublin), sends a concise Telegram briefing through `agent-job-dm`, and keeps only runtime deduplication state outside the tracked workspace.

- **Cron:** `ireland-geospatial-opportunities` in `agent-job/CRONS.json`
- **Job:** `agents/ireland-geospatial-opportunities/jobs/search-and-notify.md`
- **System prompt:** `agents/ireland-geospatial-opportunities/SYSTEM.md`
- **Freshness:** validates live original listings; excludes expired, removed, duplicate and unchanged previously sent positions
- **Storage:** no Google Drive, GitHub, email or report archive

## Adding an Agent

Each subdirectory defines an agent. At minimum create a folder with a `SYSTEM.md` file:

```
agents/
└── my-agent/
    ├── SYSTEM.md        # System prompt — identity, instructions, constraints (required)
    ├── CLAUDE.md        # Optional — guidance for AI assistants editing this agent's files
    ├── skills/          # Optional — agent-specific skills (overrides root skills/ for this scope; symlink entries from ../../skills-library/)
    └── jobs/            # Optional — reusable task prompts referenced from CRONS.json
```

`SYSTEM.md` is the agent's system prompt. Write it in markdown addressed to the agent (e.g. "You are a code reviewer..."). `CLAUDE.md` (if present) is read by AI assistants working in this directory — use it for non-obvious context only.

**Skills resolution**: when a job runs with `scope: "agents/my-agent"`, the runtime checks `agents/my-agent/skills/` first; missing skills fall back to root `skills/`. To override a built-in skill for one agent, create the override in `skills-library/<override-name>/` and symlink it from `agents/my-agent/skills/`. To inherit a root skill into a scope, symlink it: `ln -s ../../../skills-library/agent-job-secrets agents/my-agent/skills/agent-job-secrets`.

> **Important:** `agents/<name>/SYSTEM.md` **replaces** `agent-job/SYSTEM.md` when the agent is scoped — it doesn't extend it. Use `agent-job/SYSTEM.md` as a starting template and adapt it: keep the runtime environment notes, the `/tmp` scratch directive, and add the `{{skills}}` token if you want skill descriptions injected. Then add the agent's identity-specific instructions on top.

For agents with multiple complex tasks, add a `jobs/` subfolder:

```
agents/
└── my-agent/
    ├── SYSTEM.md
    └── jobs/
        ├── weekly-report.md
        └── cleanup.md
```

## Scheduling

Add a cron entry in `agent-job/CRONS.json` with a `scope` field pointing at the agent:

```json
{
  "name": "my-agent-weekly-report",
  "schedule": "0 9 * * 1",
  "type": "agent",
  "scope": "agents/my-agent",
  "job": "Follow the instructions in jobs/weekly-report.md",
  "enabled": true
}
```

`scope` activates the agent's identity (`SYSTEM.md`), skills, and working directory — the cron runs as the scoped agent, not from the repo root. `job` is the task prompt the agent receives.

For reusable tasks, write the prompt as markdown in `agents/<name>/jobs/<task>.md` and reference it from `job` — the agent's working directory is the scoped folder, so the relative path resolves. For one-off tasks, write the prompt inline.

### edge-kuth-portal
EDGE K/U/Th Portal — gamma-ray spectral analysis pipeline. Processes .spc files **immediately** on form submission. The client form posts to the upload server (`upload-server.mjs`, Docker container, exposed at `/edge-kuth/upload-page`), which saves .spc files and triggers the agent via `/edge-kuth/upload` webhook (TRIGGERS.json, **enabled**).

### terrestrial-dose
Terrestrial Dose Indicator — interactive web GIS that estimates terrestrial radiation dose (radon-222, thoron-220, external gamma) at any European land point. FastAPI backend + React/MapLibre frontend.

- **Scope:** `agents/terrestrial-dose`
- **System prompt:** `agents/terrestrial-dose/SYSTEM.md`
- **Jobs:** `agents/terrestrial-dose/jobs/process-dose.md`
- **Skills:** `agent-job-dm` for Telegram notifications
- **Source:** https://github.com/edgeengineeringco-Git/edge-ai-agent-site/tree/main/terrestrial-dose
- **Run:** `python3 -m pytest tests/test_dose_core.py -v` or `uvicorn api.main:app --reload --port 8000`

### edge-smart-video
EDGE Smart Video Content Agent — produces LinkedIn-ready video content from a topic queue. Generates posts via LLM, produces professional text-first HTML video slideshow with structured slide content, and optionally generates Veo 3.1 AI video clips. Runs Wednesdays at 10:00 AM. Scope: `agents/edge-smart-video`.

- **Pipeline**: Topic fetch → Post + slide generation → Optional images/Veo → HTML video composition → Drive upload → Telegram delivery
- **Primary output**: Self-contained HTML slideshow (`video.html`) — no API keys needed
- **Skills**: `agent-job-dm` for Telegram notifications

### geosync-expert

GeoSync Expert — geochemical survey processing pipeline for REE prospecting. Processes pXRF / gamma-ray / ICP-MS data through QC → anomaly detection → resource estimation → HTML report generation.

- **Cron:** `geosync-process-survey` in `agent-job/CRONS.json`
- **Job:** `agents/geosync-expert/jobs/process-survey.md`
- **System prompt:** `agents/geosync-expert/SYSTEM.md`
- **Skills:** Inherits all 10 root geoscience skills (geochem-qc, geochem-anomaly, geochem-resource, geochem-pipeline, critical-minerals-ref, geochem-exploration, drone-survey, ore-grade, ree-database, spectral-interpret)

### ree-obsidian-brain

REE Obsidian Brain — scientific knowledge curator for Rare Earth Element critical minerals. Maintains an Obsidian-compatible Markdown vault at a **separate GitHub repo: [Edge-Obsidian-Brain](https://github.com/edgeengineeringco-Git/Edge-Obsidian-Brain)**.

- **Vault repo**: `https://github.com/edgeengineeringco-Git/Edge-Obsidian-Brain` (separate from this repo)
- **Vault location on disk**: `agents/ree-obsidian-brain/vault/` (nested git repo)

- **Weekly curation:** `ree-obsidian-curate` in `agent-job/CRONS.json` (Sundays 09:00)
- **Monthly update:** `ree-obsidian-monthly-update` in `agent-job/CRONS.json` (1st of every month at 09:00) — auto-creates dated Google Drive folder with fresh vault ZIP
- **Job:** `agents/ree-obsidian-brain/jobs/curate-vault.md`
- **System prompt:** `agents/ree-obsidian-brain/SYSTEM.md`
- **Vault:** `agents/ree-obsidian-brain/vault/` — open in Obsidian desktop/mobile
- **Skills:** Inherits root skills (ree-database, critical-minerals-ref, agent-job-dm)
- **Universal write:** Any agent can write to this vault via the `ree-vault-write` skill. From any chat: *"Save this to my REE vault"*

```
agents/ree-obsidian-brain/
├── SYSTEM.md
├── CLAUDE.md
├── jobs/
│   └── curate-vault.md
└── vault/
    ├── 00-Inbox/              ← drop new papers/sources here
    ├── 01-Sources/            ← processed bibliographic notes
    ├── 02-Elements/           ← 17 lanthanides + Sc + Y
    ├── 03-Deposits/           ← carbonatite, IAC, hydrothermal, placer
    ├── 04-Processing/         ← beneficiation, leaching, SX, refining
    ├── 05-Markets/            ← prices, demand, supply chain
    ├── 06-Exploration/        ← methods, pathfinders, case studies
    ├── 07-Projects/           ← specific mines worldwide
    ├── 08-Concepts/           ← geochemical principles
    ├── 09-Maps-of-Content/    ← index hubs (MOCs)
    └── Templates/             ← source, element, project templates
```

### gamma-flight-join

Gamma / Flight-Log Join Portal — time-synchronises airborne gamma spectrograms (FORMAT 3) with Airdata drone flight logs. Produces a joined CSV (one row per spectrum, all channels + SI-unit flight parameters) and a dual calibration report (factory Cs-check + best-fit survey). Results are written to a per-job folder in Google Drive and announced via Telegram.

- **Scope:** `agents/gamma-flight-join`
- **System prompt:** `agents/gamma-flight-join/SYSTEM.md`
- **Job:** `agents/gamma-flight-join/jobs/process-join.md`
- **Engine:** `scripts/join_gamma_flight.py` (numpy/pandas/scipy)
- **Drive helper:** `scripts/drive_utils.sh` (list-jobs / download / create-folder / upload)
- **Serverless backend:** `web/gas-backend.js` (Google Apps Script Web App — NO Docker/server)
- **Web form:** `web/index.html` + `web/style.css` (published to public Pages repo `edge-ai-agent-site/gamma-flight-join/`)
- **Cron:** `gamma-flight-join-batch` in `agent-job/CRONS.json` (disabled by default; scans Drive for pending jobs)
- **Skills:** `agent-job-dm`, `agent-job-secrets`
- **Drive folder:** `18fSXEOVp8D039BUXWMiYrPuIeIXOxgt3` (one subfolder per job)

## Removing an Agent

Delete the `agents/<name>/` folder and remove its cron entries from `agent-job/CRONS.json`.
