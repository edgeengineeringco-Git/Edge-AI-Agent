# agent-job/ — Agent Job Configuration

This directory contains your agent job configuration files — system prompts, scheduling, and self-monitoring.

## Files

- **`SYSTEM.md`** — Agent system prompt: identity, runtime environment, and instructions. Rendered with full template support (`{{skills}}`, `{{datetime}}`, file includes).
- **`HEARTBEAT.md`** — Prompt for the agent's periodic heartbeat cron job.
- **`CRONS.json`** — Scheduled job definitions, loaded at server startup.

## Editing CRONS.json

`CRONS.json` is a JSON array of cron job objects. Each entry needs a `name`, `schedule` (cron expression), `type`, and `enabled` flag.

There are three action types:

**`agent`** — Launches a Docker agent container to execute an LLM task.

```json
{
  "name": "weekly-report",
  "schedule": "0 9 * * 1",
  "type": "agent",
  "scope": "agents/reporter",
  "job": "Generate the weekly report and open a PR.",
  "user_id": "57e959ab-d288-4623-8cda-829c995b7251",
  "enabled": false
}
```

Optional fields:

- **`"scope"`** *(recommended)* — e.g. `"agents/my-agent"`. Routes the cron to a **scoped agent** under `agents/<name>/`. Its `SYSTEM.md`, skills directory, and working directory all switch to that subdirectory. Scoping is technically optional (a cron without `scope` runs from the repo root using the default `agent-job/SYSTEM.md`), but in practice you almost always want a scoped agent so the job has a clearly-defined identity, prompt, and skill set. See `agents/CLAUDE.md` for the full pattern.
- **`"user_id"`** *(optional)* — sets the owner of the agent-job. Used by internal systems like `send-dm` to route the completion message; with no owner, the message goes to all admins. Set for personal crons; leave out for shared/system crons. Find user ids in Admin > Users.
- `"agent_backend"` (e.g. `"claude-code"`, `"codex-cli"`, `"gemini-cli"`, `"pi"`, `"opencode"`, `"kimi-cli"`) — pick which coding agent runs the job, overriding the default set in Admin > Event Handler > Coding Agents.
- `"llm_model"` — override the model used within the selected coding agent (provider is implicit in the agent).

**`command`** — Runs a shell command on the event handler (working directory: project root).

```json
{
  "name": "ping",
  "schedule": "*/1 * * * *",
  "type": "command",
  "command": "echo \"pong!\"",
  "enabled": true
}
```

**`webhook`** — Makes an HTTP request. `POST` (default) sends `vars` as the body; `GET` skips the body.

```json
{
  "name": "health-check",
  "schedule": "*/10 * * * *",
  "type": "webhook",
  "url": "https://example.com/health",
  "method": "GET",
  "enabled": false
}
```

Optional webhook fields: `"method"` (default `POST`), `"headers"`, `"vars"`.
