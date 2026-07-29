# REE Obsidian Brain Vault

## What This Is

An **Obsidian-compatible knowledge vault** for Rare Earth Element (REE) critical minerals exploration and research. Maintained autonomously by the `ree-obsidian-brain` agent running on thepopebot.

## How to Open

### Desktop (Windows/Mac/Linux)
1. Install [Obsidian](https://obsidian.md/) if you haven't already
2. Click **Open folder as vault**
3. Select this `vault/` folder
4. When prompted about **Safe Mode**, click **Turn off Safe Mode** to enable the Dataview plugin
5. The Dataview plugin will be ready to use immediately

### Mobile (iOS/Android)
1. Install Obsidian mobile app
2. Sync this vault via Obsidian Sync, Git, or your preferred sync method
3. Open the vault

---

## 🔄 Sync Methods

### Method A: Obsidian Git Plugin (Recommended)

You have the **Obsidian Git** plugin installed. This keeps your vault synced with the GitHub repo automatically.

**Setup:**
1. Open **Command Palette** (`Ctrl/Cmd + P`)
2. Type **"Git: Open source control view"**
3. The plugin will auto-pull on boot
4. To push your changes: **"Git: Commit all changes"** then **"Git: Push"**

**Daily workflow:**
```
Open Obsidian → Git auto-pulls latest updates
    ↓
Add notes, edit, create links
    ↓
Command Palette → "Git: Commit all changes"
Command Palette → "Git: Push"
    ↓
Your changes go to GitHub; agent sees them on next run
```

**To get agent updates:** Just open Obsidian — the Git plugin auto-pulls on boot. Or run **"Git: Pull"** manually.

### Method B: Google Drive ZIP (Fallback)

If Git sync fails, download the latest ZIP from your Google Drive delivery folder:
- **Delivery folder:** `https://drive.google.com/drive/folders/1TeA2-iAs5QLYK1cpT8HWbMeDAxWFHUf7`
- Each update is in a **dated subfolder** (`YYYY-MM-DD/`)
- Extract the ZIP and replace your vault folder

### Method C: Git Clone (Advanced)

```bash
git clone -b thepopebot/youthful-lamarr-1a95cbfe \
  https://github.com/edgeengineeringco-Git/Edge-AI-Agent.git
# Open: Edge-AI-Agent/agents/ree-obsidian-brain/vault/
```

---

## Vault Structure

| Folder | Purpose |
|---|---|
| `00-Inbox` | Drop new papers, clippings, quick notes here |
| `01-Sources` | Processed bibliographic notes (DOI-tracked) |
| `02-Elements` | 17 lanthanides + Scandium + Yttrium (full data seeded) |
| `03-Deposits` | Deposit-type profiles (carbonatite, IAC, hydrothermal, placer) |
| `04-Processing` | Extraction, beneficiation, separation, refining |
| `05-Markets` | Prices, demand forecasts, geopolitics |
| `06-Exploration` | Methods, pathfinders, grid design, case studies |
| `07-Projects` | Specific mining/exploration projects worldwide |
| `08-Concepts` | Geochemical principles, anomalies, calculations |
| `09-Maps-of-Content` | Index hub notes — start here! |
| `Templates` | Reusable note templates |

---

## 🔍 Start Here

→ Open **`09-Maps-of-Content/MOC — REE Master Index.md`** for the central hub.

---

## 🔎 Omni Search Tips

You have **Omni Search** installed. Press `Ctrl/Cmd + O` to open it.

**Search tricks:**
- `Dy price` → finds all notes mentioning dysprosium prices
- `carbonatite AND Nb` → notes with both terms
- `"Mountain Pass"` → exact phrase search
- `path:07-Projects` → only search project notes
- `tag:#critical` → notes tagged critical

---

## 📊 Dataview Queries

The [Dataview](https://blacksmithgu.github.io/obsidian-dataview/) plugin is pre-installed. Try these queries in any note:

### List all critical magnet REEs
```dataview
TABLE symbol, atomic_number, crustal_ppm as "Crustal (ppm)"
FROM "02-Elements"
WHERE contains(tags, "magnet-ree")
SORT atomic_number
```

### List all HREE
```dataview
TABLE symbol, atomic_weight, oxide
FROM "02-Elements"
WHERE group = "HREE"
SORT atomic_number
```

### List deposit types by HREO ratio
```dataview
TABLE
FROM "03-Deposits"
SORT file.name
```

### Find seed notes that need growth
```dataview
TABLE date_created, date_modified
FROM vault
WHERE status = "seed"
SORT date_created DESC
```

---

## 🌐 Graph View

Open **Graph View** (left sidebar icon or `Ctrl/Cmd + G`) to visualize the link network between elements, deposits, and concepts.

**Tip:** In Graph View settings, turn on **"Existing files only"** to hide broken links.

---

## 📝 Adding Content

### Option 1: Inbox Drop (Agent Curates)
1. Drop files into `00-Inbox/`
2. The `ree-obsidian-curate` agent (Sundays 09:00 UTC) will process them
3. Git plugin auto-pulls the curated notes on next Obsidian launch

### Option 2: Ask the Pope Bot (Instant)
Paste a paper or finding in chat and say:
> *"Save this to my REE vault"*

The agent creates the note, links it, updates MOCs, and commits. You pull the update.

### Option 3: Write Directly in Obsidian
1. Create a new note in the right folder
2. Copy frontmatter from an existing note
3. Add `[[WikiLinks]]` to connect
4. Git commit + push when done
5. The agent sees your changes and can build on them

---

## 📅 Auto-Update Schedule

| Job | When | What |
|---|---|---|
| **Monthly update** | 1st of every month @ 09:00 UTC | Full curation + dated Google Drive ZIP |
| **Weekly curation** | Every Sunday @ 09:00 UTC | Inbox processing + link maintenance |

You don't need to do anything — just open Obsidian and the Git plugin pulls updates.

---

## 🤝 Collaborative Workflow

```
You in Obsidian          Pope Bot Agent           GitHub Repo
     │                         │                        │
     │  Write notes            │                        │
     │  → Git commit + push    │                        │
     │────────────────────────>│                        │
     │                         │  Sees your changes     │
     │                         │  → Curates, adds links │
     │                         │  → Commits updates     │
     │                         │───────────────────────>│
     │  Open Obsidian          │                        │
     │  → Git auto-pull        │                        │
     │<────────────────────────│                        │
     │  New notes appear!      │                        │
```

---

## Agent Source

This vault is maintained by the `ree-obsidian-brain` agent in the thepopebot instance:
- **Agent:** `agents/ree-obsidian-brain/`
- **Cron:** `ree-obsidian-curate` (weekly) + `ree-obsidian-monthly-update` (monthly)
- **Pipeline:** Inbox → Source notes → Atomic claims → Wiki-links → MOC updates → Telegram notification
- **Universal write:** Any chat can save to this vault via the `ree-vault-write` skill

---

*Vault seeded: 2026-07-29 | 52 notes | Dataview 0.5.70 | Omni Search | Obsidian Git*
