# agents/edge-critical-minerals/ — EDGE Critical Minerals Intel Agent

This agent runs the weekly EDGE Critical Minerals Intelligence Briefing pipeline. It is triggered by a cron job in `agent-job/CRONS.json` every Monday at 08:00 Ireland time.

## Files

- **`SYSTEM.md`** — Agent system prompt: identity, runtime environment, and workflow overview.
- **`CLAUDE.md`** — This file. Context for AI assistants editing this agent.
- **`jobs/weekly-report.md`** — The full pipeline instructions executed each Monday. The cron job's `job` field references this file.

## Requirements

The agent relies on:

1. **Web Search** — Built into the coding agent (WebSearch tool). No external API needed.
2. **Google Drive Upload** — Uses OAuth refresh token auth. The `GOOGLE_DRIVE_OAUTH` secret (JSON with client_id, client_secret, refresh_token, token_uri) is stored as an agent job secret and auto-injected into agent-job containers. The target Google Drive folder (ID: `1ECFvfIafuyRqgU4fV9jFMt9GXzTRLO5T`) must be accessible by the authenticated Google user.
3. **Telegram Notifications** — Uses Telegram Bot API directly with bot token configured via webhook. Chat ID: `466297056`.

## Skills

The agent inherits root-level skills (`agent-job-dm`, `agent-job-secrets`, `google-drive-upload`). No agent-specific skills are needed.

## Cron Schedule

Defined in `agent-job/CRONS.json`:

```json
{
  "name": "edge-weekly-critical-minerals",
  "schedule": "0 8 * * 1",
  "type": "agent",
  "scope": "agents/edge-critical-minerals",
  "job": "Read jobs/weekly-report.md and execute the full pipeline described there.",
  "enabled": true
}
```

Schedule: Every Monday at 08:00 Ireland time (Europe/Dublin).

## Pipeline Steps

1. Research (7 sections) using web search
2. Compute metadata fields (report_date, week_number, filename)
3. Build styled HTML report
4. Upload to Google Drive (folder ID: `1ECFvfIafuyRqgU4fV9jFMt9GXzTRLO5T`)
5. Send Telegram notification via agent-job-dm (broadcast to admins)
6. Archive the HTML file in `agents/edge-critical-minerals/reports/`
