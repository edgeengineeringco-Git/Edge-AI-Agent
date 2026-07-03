# EDGE Intake Portal

Client intake forms — completely separate from the K/U/Th portal.

| Folder | Purpose |
|--------|---------|
| `intake-portal/` | Client-facing intake forms (GitHub Pages + Google Apps Script) |
| `edge-kuth-portal/` | K/U/Th spectral analysis pipeline (thepopebot / Docker) |

---

## Files

| File | Purpose |
|------|---------|
| `index.html` | Landing page — links to both forms |
| `project-setup.html` | **Form 1** — project details, services, contact info |
| `data-upload.html` | **Form 2** — multi-block data upload with file attachments |
| `gas-backend/Code.gs` | Google Apps Script backend — receives submissions, saves to Drive, logs to Sheet |

---

## How it works

```
Client browser (GitHub Pages)
        ↓  JSON + base64 files
Google Apps Script Web App
        ↓
├── Creates timestamped sub-folder in your Drive
├── Decodes & saves uploaded files
├── Appends row to Google Sheet log
├── Generates HTML summary inside the folder
└── Sends you an email alert (optional)
```

---

## Deploy (one-time, ~5 minutes)

### Step 1 — Deploy the GAS backend

1. Go to [script.google.com](https://script.google.com) → **New project**
2. Delete the default code
3. Paste the entire contents of `gas-backend/Code.gs`
   - Your Drive folder ID (`1iqhbAZOqb1G-vV8658Ih2bqXzyeU4puO`) is already pre-filled
   - The Sheet will be **auto-created** on the first submission — no manual setup needed
4. **Deploy → New deployment**
   - Type: **Web app**
   - Execute as: **Me**
   - Who has access: **Anyone**
5. **Authorize** when Google asks (needs Drive + Sheets permissions)
6. Copy the **Web App URL**

### Step 2 — Connect the forms

Open both HTML files and paste your GAS URL:

- `project-setup.html` → line ~401
- `data-upload.html` → line ~467

Replace:
```javascript
var GAS_URL = 'https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec';
```

with your real URL:
```javascript
var GAS_URL = 'https://script.google.com/macros/s/AKfycbzXXXXXXXX/exec';
```

### Step 3 — Host on GitHub Pages

```bash
git add intake-portal/
git commit -m "Add client intake portal"
git push
```

Then in your repo: **Settings → Pages → Source**: select your branch and `/ (root)`.

---

## Browser links for verification

After deploying, you can verify everything works by opening these links:

### 1. Health check (GAS backend is alive)
```
https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec
```
You should see JSON: `{ "ok": true, "service": "EDGE Intake Portal", ... }`

### 2. Intake portal landing page (GitHub Pages)
```
https://yourusername.github.io/your-repo-name/intake-portal/index.html
```

### 3. Direct form links
- Project Setup: `.../intake-portal/project-setup.html`
- Data Upload: `.../intake-portal/data-upload.html`

---

## What you get in Google Drive

Each submission creates a folder like:

```
EDGE_Intake_Log/                    ← auto-created Google Sheet
└── 20250703_143000 — Project Name (project_setup)/
    ├── data.csv
    ├── survey.zip
    └── submission-summary.html     ← pretty HTML summary
```

The Google Sheet log has these columns:
`Timestamp | Form Type | Project Name | Organisation | Contact Name | Email | Area | Country | Services | Detector Type | Detector Model | Start Date | Referral | File Count | Drive Folder | Notes`

---

## Embed on your website

Use this link anywhere on your site:

```html
<a href="https://yourusername.github.io/your-repo-name/intake-portal/index.html">
  Client Portal →
</a>
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Form receiver not configured" | You forgot to paste the GAS_URL in the HTML files |
| CORS error in browser console | Make sure GAS deployment is set to "Anyone" access |
| Files not appearing in Drive | Check GAS execution log (View → Executions in script.google.com) |
| Sheet not created | The script auto-creates it on first submission. Check the target Drive folder for `EDGE_Intake_Log`. |
