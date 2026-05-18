# EDGE Weekly Critical Minerals Intel — Pipeline Execution

Execute every step in order. Do not stop or ask for input. If something fails, retry once with a different approach, then report the error clearly via the Telegram notification.

---

## Step 1 — Research the Intelligence Report

Using your WebSearch tool, research and compile a comprehensive weekly briefing covering all 7 sections below. Be thorough — verify dates, deadlines, and amounts with live sources. Priority regions: Ireland, EU, Scandinavia, UK, then US/Canada/Australia.

### Research approach

1. First, check if there are any previous reports in this repo by running `ls agents/edge-critical-minerals/reports/ 2>/dev/null` or checking the Google Drive folder. Read the most recent report so you know what was covered before. This allows you to prioritise genuinely new or changed items and avoid repeating stale ones.
2. For each of the 7 sections below, run focused web searches to find current opportunities, events, and policy developments.
3. Verify every date, deadline, and funding amount by cross-referencing multiple sources.
4. Every single item MUST include a real, working URL.

### ⚠️ CRITICAL FRESHNESS RULE

This report must be 100% self-contained and genuinely current. Do NOT reference "last week", "the previous report", "as mentioned before", "continuing from last week", or any similar phrase. Every item you include must be presented as if it is being discovered and reported for the first time. Write entirely in the present tense. Do not use labels like [UPDATED], [STILL HIGH PRIORITY] — omit those entirely.

### Section 1 — Funding, Grants, and Investment Opportunities

For each item include: Title, Funding Body, Stage, Ticket Size, Why it fits EDGE's REE / K–Th–U prospecting platform, Eligibility, Deadline, URL.
Highlight 3–5 highest-priority picks for EDGE with 2–3 sentence justification each.

### Section 2 — Scale-Up, Accelerator and Commercialisation Programmes

For each: Programme name, Organiser, Focus, Cohort timing, What they offer, URL.
Include ESA, EIT RawMaterials, EIC, national schemes, notable private accelerators.

### Section 3 — Training, Workshops and Courses

Short courses, summer schools, workshops in: critical minerals/REE, geoscience AI/ML, mineral exploration technology, geo-data science, deep-tech entrepreneurship.
For each: Title, Organiser, Location/Online, Dates, Level, Cost, Scholarship options, URL.

### Section 4 — Conferences, Events and Partnering Opportunities

Events in the next 12–18 months where EDGE can present, meet investors, form R&D consortia, or meet government stakeholders.
For each: Name, Organiser, City/Country, Dates, Audience, URL.
Mark 3–5 must-attend with one sentence reason each.

### Section 5 — Research, R&D and Collaboration Calls

Horizon Europe, EIC, EIT RawMaterials, national councils — calls for critical raw materials, AI/ML for geoscience, remote sensing, drone surveys.
For each: Call title, Programme, TRL range, Lead type, Budget, Deadline, URL.
Highlight top 5 fits for EDGE.

### Section 6 — Policy, Regulation and Strategic Context

Current and active policies: EU Critical Raw Materials Act, national strategies, US/Canada/Australia initiatives, ESG rules, defence/dual-use interest.
For each: Jurisdiction, 2–4 sentence summary, authoritative URL.
Present all items as current facts — do not describe them as "new" relative to a previous report.

### Section 7 — Action List for This Week

5–10 concrete actions for EDGE in the next 1–4 weeks.
Mark each as [HIGH] or [MEDIUM] priority.
Make them specific with deadlines where known.
Write each action as a standalone task — do not refer to any previous action list.

### Research output format

Format everything as clean Markdown:

- Use `##` for section headings, `###` for sub-headings
- Use `*` bullet points for all list items
- Every single item MUST end with a real, working URL on its own bullet: `* **URL:** [Full title of link](https://actual-url.com)`
- Use `**bold**` for field labels like **Title:**, **Deadline:**, **URL:** etc.
- Do NOT use tables. Use bullets only.
- Do NOT add any footer, signature, or "this message was sent" text.

Store the complete research output in a variable for use in Step 3.

---

## Step 2 — Compute Metadata Fields

Compute these values from the current timestamp:

| Field | How to compute | Example |
|-------|---------------|---------|
| report_date | Current date in "DD MMMM YYYY" format | "19 May 2026" |
| week_number | ISO week number, zero-padded to 2 digits | "21" |
| year | 4-digit year | "2026" |
| month | 2-digit month | "05" |
| day | 2-digit day | "19" |
| filename | `EDGE_CriticalMinerals_Week{week_number}_{YYYY-MM-DD}.html` | `EDGE_CriticalMinerals_Week21_2026-05-19.html` |

---

## Step 3 — Build the Styled HTML Report

Take the Markdown research output from Step 1 and convert it into a full, standalone styled HTML document saved to `/tmp/{filename}`.

### HTML template

The report must use this structure and styling:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EDGE Critical Minerals Intel – Week {week_number} / {year}</title>
<style>
  /* Use this exact styling */
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'Segoe UI',Arial,sans-serif;background:#eef1f5;color:#1f2937;padding:24px 12px;font-size:15px;line-height:1.75}
  .wrap{max-width:980px;margin:0 auto;background:#fff;border-radius:18px;overflow:hidden;box-shadow:0 16px 48px rgba(0,0,0,.12)}
  .hdr{background:linear-gradient(135deg,#0f766e 0%,#1d4ed8 100%);color:#fff;padding:36px 44px 30px}
  .hdr .pill{display:inline-block;background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.35);border-radius:999px;font-size:11.5px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;padding:3px 14px;margin-bottom:16px}
  .hdr h1{font-size:27px;font-weight:800;line-height:1.22;margin-bottom:14px}
  .hdr .meta{display:flex;flex-wrap:wrap;gap:18px;font-size:13.5px;opacity:.93}
  .body{padding:36px 44px}
  .body h2{font-size:18px;font-weight:800;color:#0f766e;border-left:4px solid #0f766e;padding-left:14px;margin:36px 0 14px;line-height:1.3}
  .body h3{font-size:15px;font-weight:700;color:#1f2937;margin:22px 0 8px;padding-left:4px}
  .body p{margin-bottom:10px;max-width:840px}
  .body hr{border:none;border-top:2px solid #e5e7eb;margin:30px 0}
  .body ol{margin:8px 0 16px 22px}
  .body ol li{margin-bottom:10px;padding-left:6px}
  .body ul{list-style:none;padding:0;margin:6px 0 16px}
  .body ul li{padding:7px 8px 7px 26px;position:relative;border-bottom:1px solid #f3f4f6;max-width:840px}
  .body ul li:last-child{border-bottom:none}
  .body ul li::before{content:"▸";color:#0f766e;position:absolute;left:6px;top:9px;font-size:12px}
  .body a{color:#1d4ed8;text-decoration:none;font-weight:500;border-bottom:1px solid rgba(29,78,216,.22);transition:border-color .15s}
  .body a:hover{border-color:#1d4ed8}
  .ext{font-size:11px;opacity:.65;margin-left:2px}
  strong{color:#111827}
  code{background:#f1f5f9;border-radius:4px;padding:1px 6px;font-family:monospace;font-size:13px}
  .ftr{background:#f8fafc;border-top:1px solid #e5e7eb;padding:16px 44px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;font-size:12px;color:#6b7280}
  @media(max-width:640px){.hdr,.body,.ftr{padding-left:18px;padding-right:18px}.hdr h1{font-size:21px}}
</style>
</head>
<body>
<div class="wrap">
  <div class="hdr">
    <div class="pill">🌍 Weekly Intelligence Report</div>
    <h1>EDGE Critical Minerals GeoIntel<br>Week {week_number} &nbsp;·&nbsp; {year}</h1>
    <div class="meta">
      <span>📅 {report_date}</span>
      <span>📊 REE · K-Th-U Prospecting</span>
      <span>🌐 Web Researched</span>
      <span>🇮🇪 Ireland · EU · Scandinavia · UK · Global</span>
    </div>
  </div>
  <div class="body">
    {CONVERTED MARKDOWN CONTENT}
  </div>
  <div class="ftr">
    <span>EDGE GeoIntelligence · Automated Weekly Report · {report_date}</span>
    <span class="fn">{filename}</span>
  </div>
</div>
</body>
</html>
```

### Markdown conversion rules

Convert the research output to HTML inline:
- `## heading` → `<h2>heading</h2>`
- `### heading` → `<h3>heading</h3>`
- `* bullet` → `<ul><li>bullet</li></ul>`
- `1. list` → `<ol><li>list</li></ol>`
- `[text](url)` → `<a href="url" target="_blank">text ↗</a>`
- `**bold**` → `<strong>bold</strong>`
- Backtick code → `<code>code</code>`
- Blank lines separate paragraphs

### Save the file

Write the complete HTML to `/tmp/{filename}`. Verify the file was written correctly by reading the first and last few lines.

---

## Step 4 — Send Report to Telegram

Send the HTML report file directly to the subscribed admins via Telegram using the Telegram Bot API.

The Telegram bot token is available via the `agent-job-secrets` skill or as the `TELEGRAM_BOT_TOKEN` environment variable.

### Check the bot token

```bash
node skills/agent-job-secrets/agent-job-secrets.js get TELEGRAM_BOT_TOKEN
```

Or check if it's in the environment:

```bash
echo "TELEGRAM_BOT_TOKEN set: ${TELEGRAM_BOT_TOKEN:+yes}"
```

### Send the file

Use curl to send the HTML file as a document with a summary caption:

```bash
TELEGRAM_TOKEN="$TELEGRAM_BOT_TOKEN"
CHAT_ID="466297056"

curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendDocument" \
  -F "chat_id=$CHAT_ID" \
  -F "document=@/tmp/{filename}" \
  -F "caption=🌍 EDGE Weekly Critical Minerals Intel
📅 {report_date} · Week {week_number}

Full report attached with 7 sections:
• Funding & Grants
• Accelerator Programmes
• Training & Courses
• Conferences & Events
• R&D Collaboration Calls
• Policy & Regulation
• Action List

EDGE GeoIntelligence · Automated Report"
```

### Fallback: send just a text notification

If the file upload fails, send a text-only notification:

```bash
TELEGRAM_TOKEN="$TELEGRAM_BOT_TOKEN"
CHAT_ID="466297056"

curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage" \
  -d "chat_id=$CHAT_ID" \
  -d "text=🌍 EDGE Weekly Critical Minerals Intel
📅 {report_date} · Week {week_number}
📄 {filename}

Report generated. File archived in workspace.

EDGE GeoIntelligence · Automated Report"
```

> **Note on available method:** If `TELEGRAM_BOT_TOKEN` is not available as an env var and you cannot fetch it via `agent-job-secrets`, fall back to using the `agent-job-dm` skill with `--broadcast` for a text-only notification.

---

## Step 5 — Try Google Drive Upload (Optional)

If the `GOOGLE_DRIVE_CREDENTIALS` secret is available (check with `agent-job-secrets list`), attempt to upload to Google Drive:

```bash
skills/google-drive-upload/upload.sh /tmp/{filename} 1ECFvfIafuyRqgU4fV9jFMt9GXzTRLO5T
```

The folder ID `1ECFvfIafuyRqgU4fV9jFMt9GXzTRLO5T` is the EDGE reports folder on Google Drive.

If it fails, log the error and continue. The file has already been delivered via Telegram in Step 4, so Drive is optional/secondary.

---

## Step 6 — Archive the Report in the Workspace

Save a copy of the report in the workspace for git archival:

```bash
mkdir -p agents/edge-critical-minerals/reports/
cp /tmp/{filename} agents/edge-critical-minerals/reports/{filename}
```

This ensures each week's report is committed and pushed automatically when the job finishes.

---

## Self-Correction Rules

- **Web search fails to find a section**: Include a note in the report "Unable to verify from live sources this week" and move on. Do not block the entire pipeline.
- **Google Drive upload fails**: Log the error, include it in the Telegram notification, continue to Step 5.
- **Telegram notification fails (DM broadcast fails)**: Try `echo`-ing the message to stdout as a fallback so it appears in the job log.
- **HTML file write fails**: Retry once with a simpler template. If still fails, write the plain Markdown as the report body.

**Never stop and ask for human input.** If the entire pipeline fails, the job log will contain the error details.
