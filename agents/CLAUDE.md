# agents/ — Custom Agent Definitions

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

## Removing an Agent

Delete the `agents/<name>/` folder and remove its cron entries from `agent-job/CRONS.json`.
