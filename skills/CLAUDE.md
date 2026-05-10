# skills/ — Activation Surface

This directory is **not** where skills live. It's where active skills are turned on.

The real skill files (SKILL.md, scripts, package.json, etc.) live in `skills-library/`. Each entry here is a **symlink** pointing at a skill in `skills-library/`. The coding agents discover skills by walking into this directory through their per-agent bridges (`.claude/skills`, `.pi/skills`, `.codex/skills`, `.gemini/skills`, `.kimi/skills` → `../skills`).

## Activate a skill

```bash
ln -s ../skills-library/<skill-name> skills/<skill-name>
```

## Deactivate a skill

```bash
rm skills/<skill-name>
```

This only removes the symlink — the skill source in `skills-library/<skill-name>/` is untouched and can be re-activated later.

## Add a new skill

Don't put real files here. Create the skill in `skills-library/<your-skill>/`, then symlink it into this directory. See `skills-library/CLAUDE.md` for the full guide.

## First-init activation

`npx thepopebot init` populates this directory with a symlink for every skill in `skills-library/` **only on first install** (when this directory does not yet exist). Subsequent `init` / `upgrade` runs leave it alone — new bundled skills land in `skills-library/` un-activated, and you choose whether to symlink them.
