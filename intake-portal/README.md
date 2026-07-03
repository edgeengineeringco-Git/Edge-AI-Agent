# EDGE Intake Portal

Client intake forms for project setup and data upload. Hosted on **GitHub Pages** — no server required.

## How it works

```
┌─────────────────┐      JSON + base64 files       ┌──────────────────────┐
│  GitHub Pages   │  ───────────────────────────►  │  Google Apps Script  │
│  (static HTML)  │                                │     (free backend)   │
└─────────────────┘                                └──────────────────────┘
                                                            │
                                                            ▼
                                                   ┌──────────────────────┐
                                                   │   Google Drive       │
                                                   │   + Google Sheet     │
                                                   └──────────────────────┘
```

1. **Client fills out the form** in their browser (project setup or data upload).
2. **JavaScript converts files to base64** and sends everything as JSON to a Google Apps Script web app.
3. **GAS creates a timestamped folder** in your Drive, saves all uploaded files, and appends a row to a Google Sheet log.
4. **Client sees a success message** with a link to their Drive folder.

## Files

| File | Purpose |
|------|---------|
| `index.html` | Landing page — link to project setup |
| `project-setup.html` | Form 1: project details, area map, services, contact |
| `data-upload.html` | Form 2: multi-block data upload (geochem, drilling, geophysics, etc.) |
| `gas-backend/Code.gs` | Google Apps Script backend — copy this into a new GAS project |

## Setup (one-time)

### 1. Create the Google Drive folder
- In Google Drive, create a folder called **"EDGE Intake Submissions"** (or any name).
- Open it and copy the folder ID from the URL:
  ```
  https://drive.google.com/drive/folders/1ABC123xyz...
                              └──────────┬──────────┘
                                    folder ID
  ```

### 2. Create the Google Sheet log
- Create a new Google Sheet (or reuse an existing one).
- Copy the **Sheet ID** from the URL:
  ```
  https://docs.google.com/spreadsheets/d/1XYZ456abc.../edit
                                           └──────┬──────┘
                                              sheet ID
  ```

### 3. Deploy the Google Apps Script backend
1. Go to [script.google.com](https://script.google.com) and create a **new project**.
2. Delete the default `myFunction` and paste the entire contents of `gas-backend/Code.gs`.
3. In the `CONFIG` section at the top, replace:
   - `YOUR_DRIVE_FOLDER_ID_HERE` → your Drive folder ID
   - `YOUR_SHEET_ID_HERE` → your Sheet ID
4. Save the project (Ctrl+S).
5. Click **Deploy → New deployment**:
   - Type: **Web app**
   - Execute as: **Me**
   - Who has access: **Anyone**
   - Click **Deploy**
6. Authorize the script when prompted (it needs permission to access Drive and Sheets).
7. Copy the **Web App URL** — it looks like:
   ```
   https://script.google.com/macros/s/AKfycbzxxxxxxxx/exec
   ```

### 4. Configure the HTML forms
Open both `project-setup.html` and `data-upload.html` and find this block near the bottom:

```html
<script>
  var GAS_URL = 'https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec';
</script>
```

Replace the URL with your actual deployed GAS URL in **both files**.

### 5. Host on GitHub Pages
1. Push this `intake-portal/` folder to a GitHub repository.
2. In the repo settings, enable **GitHub Pages** from the `main` branch `/ (root)` or `/docs` folder.
3. If using a sub-folder, update the internal links (`project-setup.html`, `data-upload.html`, `index.html`) to include the correct path.

The live URL will be something like:
```
https://yourusername.github.io/intake-portal/
```

### 6. Add the link to your website
Use this link anywhere on your site:
```html
<a href="https://yourusername.github.io/intake-portal/">
  Client Portal →
</a>
```

## Data flow summary

| What | Where |
|------|-------|
| Uploaded files | `EDGE Intake Submissions/YYYY-MM-DD_HHmmss — Project Name/` |
| Submission log | Google Sheet → `Submissions` tab |
| Client confirmation | On-screen success message + Drive folder link |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Form receiver not configured" | You haven't replaced `YOUR_DEPLOYMENT_ID` with the real GAS URL |
| "Upload failed" in red banner | Check the GAS execution log (View → Executions in Apps Script editor) |
| Files not appearing in Drive | Make sure the GAS project has been authorized to access Drive |
| CORS / network error | The GAS web app must be deployed with **"Who has access: Anyone"** |
| Sheet not logging | Make sure `SHEET_ID` is correct and the Sheet is shared with you |

## Notes

- **File size limit**: Google Apps Script has a ~50 MB payload limit. For very large files, ask clients to upload to Drive and paste a share link in the notes field.
- **Security**: The GAS endpoint is public (Anyone can access). There is no password — this is standard for contact-form-style use cases. The data goes straight into your own Drive.
- **No server maintenance**: Once deployed, this runs entirely on Google's infrastructure. You only need to update the HTML if you change the GAS URL.
