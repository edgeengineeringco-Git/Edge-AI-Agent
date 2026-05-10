---
name: agent-job-dm
description: Send a direct message to a user OR broadcast to all subscribed admins via their default channel (currently Telegram). Also looks up users when a specific person is named. Trigger when the user says "let me know when…", "DM me", "send X to <name>", "tell <name> that…", "notify the admins", "alert everyone", "broadcast this", "let the team know", "tell all admins", or asks "who are the users?", "list users".
---

## The three modes — pick one

Read the request and route to **exactly one** of these. Do NOT mix them.

### Mode 1 — Broadcast to admins

Trigger phrases: "notify the admins", "alert everyone", "broadcast this", "let the team know", "tell all admins", "send to admins".

```bash
node skills/agent-job-dm/agent-job-dm.js send "<message>" --broadcast
```

**DO NOT** run `list` first. **DO NOT** look up any user ids. The `--broadcast` flag handles fan-out internally — it sends to every admin where `subscribed_to_system_messages=true` automatically. Calling `list` and then sending one-at-a-time is wrong and skips the subscription filter.

### Mode 2 — DM the originator (the user who started this job)

Trigger phrases: "DM me", "let me know when…", "tell me when…", "ping me", "send me".

```bash
node skills/agent-job-dm/agent-job-dm.js send "<message>"
```

No flags. The skill reads `USER_ID` from the environment (the originator) and sends to them. **Don't** look them up — `USER_ID` is already correct.

### Mode 3 — DM a specific named user

Trigger phrases: "tell Alice…", "send this to bob@…", "DM <name>", "message <person>".

```bash
node skills/agent-job-dm/agent-job-dm.js list
node skills/agent-job-dm/agent-job-dm.js send --user-id <id> "<message>"
```

1. Run `list` to get the directory.
2. Match the requested name against `nickname`, `first_name`, `last_name`, or `email`. If multiple match, ask which one.
3. Send with `--user-id <id>`.

## Other commands

```bash
# List users (id, email, first/last name, nickname, role, available DM channels)
node skills/agent-job-dm/agent-job-dm.js list
```

## Rules

- The `<message>` arg is sent verbatim. Don't rewrite it unless the requester asked you to.
- `AGENT_JOB_TOKEN`, `APP_URL`, and `USER_ID` are injected automatically — no setup required.
- Every DM is stored in the recipient's inbox in the event handler, regardless of delivery channel.
- Users link their DM channel themselves in `/profile/telegram`. If a target user has no verified channel, the message still lands in their inbox.
