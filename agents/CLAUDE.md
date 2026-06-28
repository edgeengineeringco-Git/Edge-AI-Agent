# agents/ — Custom Agent Definitions

## Active Agents

### edge-critical-minerals

The EDGE Weekly Critical Minerals Intel pipeline. Runs every Monday at 08:00 Ireland time. See `agents/edge-critical-minerals/CLAUDE.md` for full documentation.

- **Cron**: `edge-weekly-critical-minerals` in `agent-job/CRONS.json`
- **Job**: `agents/edge-critical-minerals/jobs/weekly-report.md`
- **System prompt**: `agents/edge-critical-minerals/SYSTEM.md`
- **Skills**: Inherits root skills (agent-job-dm, agent-job-secrets, google-drive-upload)
- **Secrets needed**: `GOOGLE_DRIVE_OAUTH` (OAuth refresh token JSON — client_id, client_secret, refresh_token)

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
- **Skills:** Inherits root skills (geochem-qc, geochem-anomaly, geochem-resource, geochem-pipeline, critical-minerals-ref, geochem-exploration)

## Removing an Agent

Delete the `agents/<name>/` folder and remove its cron entries from `agent-job/CRONS.json`.
