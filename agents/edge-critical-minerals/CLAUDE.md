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
  "schedule": "0 7 * * 1",
  "type": "agent",
  "scope": "agents/edge-critical-minerals",
  "job": "Read agents/edge-critical-minerals/jobs/weekly-report.md and execute the full pipeline described there.",
  "user_id": "4ab4ba80-a095-4c07-bb61-3e3471545055",
  "enabled": true
}
```

Schedule: Every Monday at 08:00 Ireland time (07:00 UTC during summer).

## Pipeline Steps

1. Research (7 sections) using web search
2. Compute metadata fields (report_date, week_number, filename)
3. Build styled HTML report
4. Send report to Telegram via Bot API (sendDocument)
5. Upload to Google Drive (folder ID: `1ECFvfIafuyRqgU4fV9jFMt9GXzTRLO5T`)
6. Archive the HTML file in `agents/edge-critical-minerals/reports/`
