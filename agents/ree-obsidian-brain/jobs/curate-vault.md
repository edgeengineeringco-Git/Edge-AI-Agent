# Weekly Vault Curation Job

## Objective
Maintain the REE Obsidian Brain vault by processing the inbox, curating links, updating Maps of Content, and ensuring data integrity.

## Steps

### 1. Process Inbox
- Read all files in `vault/00-Inbox/`
- For each file:
  - Extract title, authors, DOI (if present)
  - Create a source note in `vault/01-Sources/` using the Source Template
  - Extract 3–5 atomic claims
  - Link atomic claims to relevant element/deposit/concept notes
  - Add backlinks from topic notes to the new source
- Move processed files to `vault/00-Inbox/.processed/` or delete

### 2. Link Maintenance
- Scan all notes for `[[WikiLinks]]`
- Identify broken links (target file does not exist)
- Create stub notes for missing targets OR fix broken links
- Ensure every source note links to at least one MOC

### 3. MOC Updates
- Review `09-Maps-of-Content/` notes
- Add new links if topics have expanded
- Update statistics if data has changed (prices, production)
- Ensure all MOCs link back to `[[MOC — REE Master Index]]`

### 4. Integrity Check
- Verify all element notes have consistent frontmatter
- Check that `date_modified` is current
- Confirm no duplicate filenames

### 5. Deliver to User

**MANDATORY — After every curation:**

1. Create a dated folder (`YYYY-MM-DD`) inside the user's Google Drive folder: `1TeA2-iAs5QLYK1cpT8HWbMeDAxWFHUf7`
2. ZIP the vault (`agents/ree-obsidian-brain/vault/`)
3. Upload the ZIP to the dated folder
4. Provide the user with the Google Drive folder URL

### 6. Notification
- When complete, send a Telegram summary:
  - Items processed from inbox
  - New links created
  - Google Drive dated folder URL
  - Any issues found

## Output
- Curated vault with clean links and up-to-date MOCs
- Dated folder in user's Google Drive with ZIP upload
- Telegram notification to admins
