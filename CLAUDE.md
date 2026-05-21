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

## Agents

### edge-critical-minerals

EDGE (Extraction, Development, Geopolitics & Economics) Critical Minerals Intelligence agent. Produces weekly intelligence briefs on the global critical minerals landscape including lithium, rare earths, cobalt, nickel, copper, and graphite.

- **Scope:** `agents/edge-critical-minerals`
- **Schedule:** Mondays at 9:00 AM (cron: `0 9 * * 1`)
- **System prompt:** `agents/edge-critical-minerals/SYSTEM.md`
- **Jobs:** `agents/edge-critical-minerals/jobs/weekly-report.md`
- **Reports:** `agents/edge-critical-minerals/reports/`

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

**Pipeline files:**
- `edge-kuth-portal/estimate_k_u_th_matrix.py` — Core Python engine (CLI with args)
- `edge-kuth-portal/upload-server.mjs` — Node.js multipart upload receiver (Docker container, zero npm deps)
- `edge-kuth-portal/handle-upload.sh` — Upload handler orchestrator
- `edge-kuth-portal/drive-utils.sh` — Google Drive & Sheets helper (PAD fetch, results upload, job logging)
- `edge-kuth-portal/send-email.sh` — SendGrid email helper (confirmation + results)
- `edge-kuth-portal/incoming/` — Drop .spc files here for processing
- `edge-kuth-portal/output/` — Results CSVs archived here
- `edge-kuth-portal/jobs/{job_id}/` — Per-job working directory
- `edge-kuth-portal/pad_reference/` — PAD reference spectra (PAD_K_A.spc, PAD_U_A.spc, PAD_Th_A.spc)

## Skills

### edge-kuth-analysis

K/U/Th spectral analysis skill. Any agent can invoke this skill for instructions on running the estimation engine. See `skills-library/edge-kuth-analysis/SKILL.md` for details.

## Security Note

The original n8n workflow used a hardcoded password (`Edge12345`). This thepopebot-native deployment handles auth through the platform's standard webhook authentication and agent scoping. No credentials are embedded in code.
