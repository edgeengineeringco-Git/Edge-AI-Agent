# Deploy the EDGE Intake Portal (ready to go)

Your IDs are already filled in. You just need to deploy the backend and paste the URL.

---

## Your pre-configured IDs

| Item | Value |
|------|-------|
| **Drive Folder** | `1iqhbAZOqb1G-vV8658Ih2bqXzyeU4puO` |
| **Sheet ID** | `1YkQyyYkaLQUmauiGMVYpfxEauSI17t4l` |
| **Repo** | `https://github.com/edgeengineeringco-Git/Edge-AI-Agent` |
| **GitHub Pages URL** | `https://edgeengineeringco-git.github.io/Edge-AI-Agent/intake-portal/index.html` |

---

## Step 1 — Deploy the Google Apps Script backend (2 min)

1. Open [script.google.com](https://script.google.com) → **New project**
2. Delete the default code
3. Open `intake-portal/gas-backend/Code.gs` in this repo — **copy the entire file**
4. Paste it into the GAS editor → **Save** (Ctrl+S)
5. Click **Deploy → New deployment**
   - Type: **Web app**
   - Execute as: **Me**
   - Who has access: **Anyone**
6. Click **Deploy** → authorize when Google asks (allow Drive + Sheets access)
7. **Copy the Web App URL** — it looks like:
   ```
   https://script.google.com/macros/s/AKfycbzxxxxx/exec
   ```

---

## Step 2 — Paste the GAS URL into the forms (1 min)

Open these two files and replace the placeholder with your real URL:

**`intake-portal/project-setup.html`** (line ~398)
```html
<script>
  var GAS_URL = 'https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec';  // ← REPLACE THIS
</script>
```

**`intake-portal/data-upload.html`** (line ~464)
```html
<script>
  var GAS_URL = 'https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec';  // ← REPLACE THIS
</script>
```

---

## Step 3 — Push to GitHub (1 min)

```bash
git add intake-portal/
git commit -m "Add client intake portal with GAS backend"
git push
```

---

## Step 4 — Enable GitHub Pages (1 min)

1. Go to your repo on GitHub: `https://github.com/edgeengineeringco-Git/Edge-AI-Agent`
2. **Settings → Pages**
3. Source: **Deploy from a branch**
4. Branch: `main` → **/ (root)**
5. Click **Save**
6. Wait ~1 minute, then open:

   ```
   https://edgeengineeringco-git.github.io/Edge-AI-Agent/intake-portal/index.html
   ```

---

## Step 5 — Embed on your website

Use this exact link:

```html
<a href="https://edgeengineeringco-git.github.io/Edge-AI-Agent/intake-portal/index.html">
  Client Portal →
</a>
```

---

## Verify it works

1. Open the GitHub Pages link in an incognito window
2. Click **Project Setup**
3. Fill the form, attach a small test file
4. Submit
5. You should see a green success banner with a **View Drive folder →** link
6. Check your Drive folder — the submission folder should appear within seconds
7. Check your Google Sheet — a new row should be appended

---

## If something breaks

| Symptom | Check |
|---------|-------|
| "Form receiver not configured" | GAS_URL still has `YOUR_DEPLOYMENT_ID` |
| "Upload failed" in red | GAS execution log (View → Executions in Apps Script editor) |
| Nothing in Drive | GAS project authorized for Drive access? |
| Nothing in Sheet | Sheet ID `1YkQyyYkaLQUmauiGMVYpfxEauSI17t4l` correct? Sheet shared with you? |
| CORS error | GAS deployed as **Web app** with access **Anyone**? |
