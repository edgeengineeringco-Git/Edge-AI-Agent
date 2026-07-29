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

## Vault Structure

| Folder | Purpose |
|---|---|
| `00-Inbox` | Drop new papers, clippings, quick notes here |
| `01-Sources` | Processed bibliographic notes with DOI tracking |
| `02-Elements` | 17 lanthanides + Scandium + Yttrium (full data seeded) |
| `03-Deposits` | Deposit-type profiles (carbonatite, IAC, hydrothermal, placer) |
| `04-Processing` | Extraction, beneficiation, separation, refining |
| `05-Markets` | Prices, demand forecasts, geopolitics |
| `06-Exploration` | Methods, pathfinders, grid design, case studies |
| `07-Projects` | Specific mining/exploration projects worldwide |
| `08-Concepts` | Geochemical principles, anomalies, calculations |
| `09-Maps-of-Content` | Index hub notes — start here! |
| `Templates` | Reusable note templates |

## Start Here

→ Open **`09-Maps-of-Content/MOC — REE Master Index.md`** for the central hub.

## Dataview Queries

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

## Graph View

Open **Graph View** (left sidebar icon or Ctrl/Cmd+G) to visualize the link network between elements, deposits, and concepts.

## Adding Content

1. Drop files into `00-Inbox/`
2. The `ree-obsidian-curate` agent (Sundays 09:00 UTC) will process them automatically
3. Or trigger the agent manually for immediate curation

## Agent Source

This vault is maintained by the `ree-obsidian-brain` agent in the thepopebot instance:
- Agent: `agents/ree-obsidian-brain/`
- Cron: `ree-obsidian-curate` in `agent-job/CRONS.json`
- Pipeline: Inbox → Source notes → Atomic claims → Wiki-links → MOC updates → Telegram notification

---

*Vault seeded: 2026-07-29 | 19 element notes | 4 deposit notes | 8 MOCs | Dataview 0.5.70*
