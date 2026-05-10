# skills-library/ — Canonical Skill Store

All skill source files live here. This is the canonical location for SKILL.md files, scripts, package.json, etc.

Skills in this directory are **inactive by default**. To make a skill available to coding agents, create a symlink in `skills/` pointing here:

```bash
ln -s ../skills-library/<skill-name> skills/<skill-name>
```

The agents discover active skills through their per-agent bridges (`.claude/skills → ../skills`, etc.) — those bridges target `skills/`, which is just a curated set of symlinks back to here.

## Why two directories?

- **`skills-library/`** — the package. Source of truth, never deleted by deactivation.
- **`skills/`** — the activation surface. Add a symlink to turn a skill on; remove the symlink to turn it off without losing the skill source.

This makes it cheap to toggle skills on/off (especially when narrowing what a particular install exposes to agents) without copying, archiving, or version-controlling deletions.

## How Skills Work

1. **Discovery** — At system-prompt build time, the renderer scans `skills/` for entries with a `SKILL.md` (real or symlinked).
2. **Frontmatter loaded** — The `description` from YAML frontmatter is included in the system prompt under "Active skills" (via the `{{skills}}` template variable).
3. **Full SKILL.md read on demand** — When the agent decides to use a skill, it reads the full `SKILL.md` for detailed usage instructions.

All coding agents use the same activation set (`skills/`) via symlink bridges created by `npx thepopebot init`:

- `.claude/skills → ../skills` (Claude Code)
- `.pi/skills → ../skills` (Pi)
- `.codex/skills → ../skills` (Codex CLI)
- `.gemini/skills → ../skills` (Gemini CLI)
- `.kimi/skills → ../skills` (Kimi CLI)

## Conventions

### Language Preference

**Bash first.** Skills are glue code — API calls, data piping, file manipulation. Bash + curl + python3 (for JSON) handles nearly everything. No module systems, no dependency management, no surprises.

Use Node.js **only** when a required library has no alternative (e.g., `youtube-transcript-plus`). Never for new skills where bash + curl would work.

### Bash Script Standards

- Include `#!/bin/bash` and `set -euo pipefail` at the top
- `chmod +x` after creating

### Node.js Module Rules

The root `package.json` has `"type": "module"`, which forces **all** `.js` files in the project tree to be treated as ESM. This silently breaks any script using `require()`.

- **`.cjs`** — for CommonJS scripts (uses `require()`)
- **`.mjs`** — for ESM scripts (uses `import`)
- **Never use plain `.js`** for skill scripts. The behavior depends on the nearest `package.json` and will break unpredictably.

If you encounter a broken `.js` script in a skill, rename it to `.cjs` or `.mjs` as appropriate and update SKILL.md references.

### SKILL.md Format

Every skill must have a `SKILL.md` with YAML frontmatter:

```markdown
---
name: skill-name-in-kebab-case
description: One sentence describing what the skill does and when to use it.
---

# Skill Name

## Usage

```bash
skills/skill-name/script.sh <args>
```
```

- The `description` field appears in the system prompt — keep it concise and action-oriented.
- Use `skills/<skill-name>/...` paths in documentation (the symlink path the agent sees), not `skills-library/...`.

### Skill Structure

- **`SKILL.md`** (required) — YAML frontmatter + markdown documentation
- **Scripts** — bash (`.sh`) by default, `.cjs`/`.mjs` only when necessary
- **`package.json`** (optional) — only if Node.js dependencies are truly needed

### Credential Setup

If a skill needs an API key, add it via the admin UI (Settings > Agent Jobs > Secrets). The secret will be injected as an env var into Docker containers. The agent can discover available secrets via the `agent-job-secrets` skill.

## Creating a Skill

### Simple bash skill (most common)

1. Create the skill in `skills-library/`:

```bash
mkdir skills-library/my-skill
```

2. Add `skills-library/my-skill/SKILL.md`:

```markdown
---
name: my-skill
description: Does X when the agent needs to Y.
---

# My Skill

## Setup
Requires MY_API_KEY environment variable.

## Usage
```bash
skills/my-skill/run.sh <args>
```
```

3. Add `skills-library/my-skill/run.sh`:

```bash
#!/bin/bash
set -euo pipefail

if [ -z "$1" ]; then echo "Usage: run.sh <args>"; exit 1; fi
if [ -z "$MY_API_KEY" ]; then echo "Error: MY_API_KEY not set"; exit 1; fi
# ... skill logic
```

4. Make it executable and activate:

```bash
chmod +x skills-library/my-skill/run.sh
ln -s ../skills-library/my-skill skills/my-skill
```

### Node.js skill

Use only when a required library has no bash/curl alternative. Add a `package.json` with dependencies — they're installed automatically in Docker. Use `.cjs` for CommonJS or `.mjs` for ESM — never plain `.js`.

## Testing

Always build AND test a skill in the same job. Tell the agent to test with real input after creating the skill and fix any issues before committing.

## Default Skills

Bundled in this directory and activated by default on first install:

- `agent-job-secrets` — list/get agent-job secrets and OAuth credentials
- `agent-job-dm` — list users + send DMs/broadcasts via the recipient's default channel
- `agent-job-background` — spawn/check background agent jobs (defaults `--user-id` to the running container's `USER_ID`)
- `playwright-cli` — browser automation via Playwright CLI
