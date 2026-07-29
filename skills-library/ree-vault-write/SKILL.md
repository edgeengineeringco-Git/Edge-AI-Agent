---
name: ree-vault-write
description: Write scientific notes, papers, or data directly into the REE Obsidian Brain vault. Any agent can use this skill to create properly formatted Markdown notes with YAML frontmatter, wiki-links, and tags in the shared knowledge vault.
---

# REE Vault Write Skill

Use this skill to save data, papers, findings, or any scientific content to the **REE Obsidian Brain** — a shared Obsidian-compatible Markdown vault for Rare Earth Element critical minerals research.

## Vault Location

```
agents/ree-obsidian-brain/vault/
```

## How to Write a Note

### 1. Determine the correct folder

| Content Type | Target Folder | Template |
|---|---|---|
| Scientific paper / report | `01-Sources/` | `Templates/Source Template.md` |
| REE element data | `02-Elements/` | `Templates/Element Template.md` |
| Deposit type profile | `03-Deposits/` | — |
| Processing method | `04-Processing/` | — |
| Market / price data | `05-Markets/` | — |
| Exploration case study | `06-Exploration/` | — |
| Mine / project profile | `07-Projects/` | `Templates/Project Template.md` |
| Geochemical concept | `08-Concepts/` | — |
| Index / hub note | `09-Maps-of-Content/` | — |

### 2. Use proper frontmatter

Every note MUST include YAML frontmatter:

```yaml
---
title: "Note Title"
date_created: YYYY-MM-DD
date_modified: YYYY-MM-DD
tags: [tag1, tag2, tag3]
status: seed|growing|evergreen
---
```

- `seed` = just planted, minimal content
- `growing` = actively developed
- `evergreen` = mature, reference-grade

### 3. Use wiki-links for connections

Link to existing notes using `[[WikiLinks]]`:
- `[[Carbonatite Deposits]]`
- `[[Dysprosium]]`
- `[[Mountain Pass]]`
- `[[MOC — REE Master Index]]`

Always add backlinks — if you create a new note about a project, add a link from `MOC — Projects Index`.

### 4. Write in Markdown

- Use `#` headers for structure
- Use tables for data
- Use `> ` blockquotes for key findings
- Use `[^1]` footnotes for citations
- Use Mermaid diagrams for workflows

### 5. Commit the note

After writing the note, commit it:
```bash
cd /home/coding-agent/workspace
git add agents/ree-obsidian-brain/vault/...
git commit -m "vault: add [note title]"
git push
```

## Example: Adding a New Paper

User says: *"Save this paper: 'New carbonatite discovery in Greenland' by Smith et al. 2025. Key finding: 4.2% TREO with elevated Nd. DOI: 10.1234/ree.2025.001"*

You create:
```
agents/ree-obsidian-brain/vault/01-Sources/Smith et al 2025 — Greenland Carbonatite.md
```

With:
- Full frontmatter (DOI, authors, year)
- Abstract + key findings
- Links to `[[Carbonatite Deposits]]`, `[[Neodymium]]`, `[[Greenland]]`
- Backlink added to `MOC — Sources Index`
- Status: `growing`

## Example: Adding a New Project

User says: *"Add the Kvanefjeld project in Greenland"*

You create:
```
agents/ree-obsidian-brain/vault/07-Projects/Kvanefjeld.md
```

With:
- Project Template frontmatter
- Location, ownership, resources
- Links to deposit type, key elements
- Backlink in `MOC — Projects Index`

## User Delivery Protocol

**CRITICAL**: After every vault write, the dated-folder delivery protocol applies:

1. Create dated folder `YYYY-MM-DD` in Google Drive: `1TeA2-iAs5QLYK1cpT8HWbMeDAxWFHUf7`
2. ZIP the vault (`agents/ree-obsidian-brain/vault/`)
3. Upload ZIP to dated folder
4. Give user the direct download link

## Rules

- Never delete existing notes without user confirmation
- Always check if a note already exists before creating duplicates
- Maintain consistent frontmatter format across all notes
- Every new note must link to at least one MOC or existing note
- Use scientific but accessible language
