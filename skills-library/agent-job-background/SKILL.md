---
name: agent-job-background
description: Use to spawn or check on long-running background agent jobs (each launches a new Docker agent container that opens a PR when done). Trigger when the user says "create a background job", "spawn an agent", "kick off a job", "run this in the background", "check job status", or asks "what's the status of job <id>".
---

## Usage

```bash
# Run an agent job in the background
node skills/agent-job-background/agent-job-background.js create "Update the README with installation instructions"

# With overrides
node skills/agent-job-background/agent-job-background.js create "Refactor the auth module" \
  --llm-model claude-opus-4-7 \
  --agent-backend claude-code \
  --scope agents/refactor

# Status of running jobs (all, or one by id)
node skills/agent-job-background/agent-job-background.js status
node skills/agent-job-background/agent-job-background.js status <agent_job_id>
```

## Important: pass-through behavior for `create`

The `<description>` arg becomes the new job's prompt verbatim. **Pass it through unchanged — do not summarize, condense, or rewrite the user's request before calling.** The new job's agent reads this description directly as its task. If the user gave you a multi-paragraph spec, pass the multi-paragraph spec.

## Scope inheritance

If the calling agent is running with a `SCOPE` env var set, `create` defaults the new job to that same scope. Pass `--scope <value>` to override, or `--scope ""` to clear scope on the new job.

## Notes

- `AGENT_JOB_TOKEN`, `APP_URL`, and `USER_ID` are injected automatically — no setup required.
- The spawned job inherits `USER_ID` from the env if set, so it's attributed to the same originator as this chat/job.
