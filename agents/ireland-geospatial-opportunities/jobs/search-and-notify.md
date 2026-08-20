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
Send one concise Telegram message via the `agent-job-dm` skill:
- heading and run date
- number of new/changed validated opportunities
- for each: title, employer, Irish location, type, closing date (or “not stated”), why it matches, and the direct original URL
- a clear note that expired and repeated unchanged positions were excluded
- if zero: say no new qualifying positions were found; do not resend prior listings

Keep within Telegram message limits; split into numbered messages if necessary. Update state only after successful delivery. If delivery fails, do not mark candidates as sent.
