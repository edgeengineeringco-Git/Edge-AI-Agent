# Search and notify

Execute the Ireland Geospatial Opportunities Agent mission in `SYSTEM.md`.

## Research
Use live web research to search official Irish university, research-centre, public-sector and employer vacancy pages, plus reputable job boards. Search combinations of:
- remote sensing, Earth observation, satellite imagery
- GIS, geospatial, geomatics, geographic information systems
- UAV, UAS, drone, aerial survey, photogrammetry, LiDAR
- postdoctoral, postdoc, research fellow, research assistant, GIS analyst, remote sensing scientist, geospatial engineer, surveyor

Search Ireland locations including Dublin, Cork, Galway, Limerick, Maynooth, Waterford, Athlone, Sligo and other Republic of Ireland locations. Confirm the role location from the original listing, not only a search snippet.

## Validation and deduplication
Read `data/ireland-geospatial-opportunities/state.json` before compiling results. Apply every freshness and duplicate rule in `SYSTEM.md`. Use a small Python script if useful for URL canonicalisation, hashing and atomic JSON updates. Never put state in git-tracked files.

## Message
Send one polished, compact Telegram message via the `agent-job-dm` skill. The message is the user interface: use clear spacing, short sections, bullet points and restrained emojis. Show only the main information—do not paste research notes or long descriptions.

Use this layout:

🔎 **Ireland Geospatial Opportunities**
📅 Checked: DD Month YYYY · Europe/Dublin
📍 Republic of Ireland only

✅ **N new opportunities**

For each result:
**1. Role title**
🏢 Employer · 📍 Irish location
🎓 Type: job/postdoc/research role
⏳ Deadline: exact date and time, or “not stated”
🧭 Match: one short reason
🔗 Apply: direct original vacancy URL

Finish with:
🛡️ Expired, removed, duplicate and unchanged previously sent listings excluded.

If zero qualifying results survive validation, use:
📭 **No new qualifying opportunities found today.**
All checked listings were either outside the criteria, expired, duplicate, or could not be verified as open. No previous positions were resent.

Keep within Telegram message limits; split into numbered messages if necessary. Update state only after successful delivery. If delivery fails, do not mark candidates as sent.
