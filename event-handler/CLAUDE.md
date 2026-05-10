# event-handler/ — Event Handler Configuration

This directory holds configuration for the event handler: webhook triggers, chat system prompts, cluster role definitions, LiteLLM proxy routing, and the job-summary prompt. Edit these to shape how your handler reacts to events.

## Files

| File | Purpose |
|------|---------|
| `TRIGGERS.json` | Webhook trigger definitions — fires actions when matching paths receive HTTP requests |
| `agent-chat/SYSTEM.md` | System prompt for the chat agent (default chat mode) |
| `code-chat/SYSTEM.md` | System prompt for code mode chat (workspace-aware) |
| `clusters/SYSTEM.md` | System prompt prepended to every cluster worker |
| `clusters/ROLE.md` | Role-template snippet referenced by cluster role definitions |
| `litellm/main.yaml` | LiteLLM proxy config — routes Claude Code through other providers |
| `SUMMARY.md` | System prompt for the auto-summary that runs after agent jobs complete |

## TRIGGERS.json

JSON array of webhook trigger definitions. Loaded at server boot by `lib/triggers.js`.

```json
{
  "name": "review-github-event",
  "watch_path": "/github/webhook",
  "actions": [
    { "type": "agent", "job": "Summarize this GitHub event:\n{{body}}" }
  ],
  "enabled": true
}
```

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | Unique within the file |
| `watch_path` | Yes | Path to match (`/github/webhook`, `/webhook`, custom paths) |
| `actions` | Yes | Array — runs in order, fire-and-forget after auth |
| `enabled` | No | Defaults `true`. Set `false` to keep the entry but skip it |

### Action types

Three types — `agent`, `command`, `webhook`:

```json
{ "type": "agent", "scope": "agents/triage", "job": "Process: {{body}}" }
{ "type": "command", "command": "echo 'webhook received: {{body}}' >> logs/webhook.log" }
{ "type": "webhook", "url": "https://example.com/hook", "method": "POST", "headers": {}, "vars": { "source": "github" } }
```

#### Optional fields on `agent` actions

- **`"scope"`** *(recommended)* — e.g. `"agents/triage"`. Routes the action to a **scoped agent** under `agents/<name>/`. Its `SYSTEM.md`, skills directory, and working directory all switch to that subdirectory. Scoping is technically optional (an action without `scope` runs from the repo root using the default `agent-job/SYSTEM.md`), but in practice you almost always want a scoped agent so each trigger has a clearly-defined identity, prompt, and skill set. See `agents/CLAUDE.md` for the full pattern.
- **`"user_id"`** *(optional)* — sets the owner of the agent-job. Used by internal systems like `send-dm` to route the completion message; with no owner, the message goes to all admins. Set for per-user integrations; leave out for shared/system triggers. Find user ids in Admin > Users.
- `"agent_backend"` (e.g. `"claude-code"`, `"codex-cli"`, `"gemini-cli"`, `"pi"`, `"opencode"`, `"kimi-cli"`) — pick which coding agent runs the action, overriding the default set in Admin > Event Handler > Coding Agents.
- `"llm_model"` — override the model used within the selected coding agent (provider is implicit in the agent).

### Template tokens (in `job` and `command` strings)

`{{body}}`, `{{body.field}}`, `{{query}}`, `{{query.field}}`, `{{headers}}`, `{{headers.field}}`. Tokens are expanded when the trigger fires.

## Chat System Prompts

`agent-chat/SYSTEM.md` and `code-chat/SYSTEM.md` are the system prompts injected into chat sessions. They support `{{include path/to/file.md}}`, `{{datetime}}`, and `{{skills}}` variables (resolved by `lib/utils/render-md.js`).

- **Agent chat** (`agent-chat/`) — default chat mode. Workspace-agnostic.
- **Code chat** (`code-chat/`) — code-mode chat. Knows about the active code workspace, repo, branch, and feature branch.

Both can be scoped: a chat tied to a workspace with `scope: "agents/foo"` will load `agents/foo/SYSTEM.md` instead of these defaults.

## Cluster Configuration

`clusters/SYSTEM.md` is prepended to every cluster worker's system prompt. `clusters/ROLE.md` is a reusable role-template snippet that individual cluster role definitions can reference. Cluster behavior is configured in the Admin UI; these files supply the prompt context.

## LiteLLM Proxy

`litellm/main.yaml` is read by the optional LiteLLM sidecar (`docker-compose.litellm.yml`). It routes Claude Code's Anthropic-protocol calls to other providers (OpenAI, Gemini, custom OpenAI-compatible endpoints). Edit when you want to use Claude Code with a non-Anthropic backend. Refer to [LiteLLM docs](https://docs.litellm.ai/) for the schema.

## Summary Prompt

`SUMMARY.md` is the prompt for the helper LLM call that auto-summarizes agent job results (PR link, status, files changed). Tweak its tone or formatting here.

## Notes

- These files are user-owned — edits are preserved across `thepopebot upgrade`.
- The Admin UI (`/admin/event-handler/`) configures runtime defaults (LLM provider, coding agent backend, OAuth tokens). Trigger-level `agent_backend` / `llm_model` overrides those defaults.
