# EDGE Smart Video — Content Generation Pipeline

Execute the following pipeline sequentially. Each phase builds on the previous.

**Sheet ID:** `1xeLg8mnRrgF6jlW97JcJDk1ODcbsdbaydQjohaVf5x8`
**Sheet Name:** `Edge_topics_sample`

---

## Phase 0: Setup

1. Get secrets via `agent-job-secrets`:
   - `GOOGLE_DRIVE_OAUTH` — for Google Sheets access (already in env for scoped agent jobs)
   - `MOONSHOT_API_KEY` — for SVG schematic generation (set in admin panel as agent-job-secret)

   Note: agent-job-secrets returns the full JSON object. Extract the value like this:
   ```bash
   MOONSHOT_JSON=$(node skills/agent-job-secrets/agent-job-secrets.js get MOONSHOT_API_KEY 2>/dev/null || echo "")
   MOONSHOT_API_KEY=$(echo "$MOONSHOT_JSON" | python3 -c "import json,sys; print(json.load(sys.stdin)['value'])" 2>/dev/null || echo "")
   export MOONSHOT_API_KEY
   ```

2. Create dated output directory:
   ```bash
   DATE_DIR=$(date +%Y-%m-%d)
   mkdir -p "output/$DATE_DIR"
   ```

3. Verify Python3 and scripts:
   ```bash
   python3 scripts/compose_video.py --help > /dev/null && echo "OK"
   python3 scripts/generate_schematics.py --help > /dev/null && echo "OK"
   python3 scripts/sheets_handler.py --help > /dev/null && echo "OK"
   python3 scripts/drive_upload.py --help > /dev/null && echo "OK"
   ```

---

## Phase 1: Fetch Pending Topic

Run the sheets handler to find the next pending topic:

```bash
python3 scripts/sheets_handler.py read \
  --sheet-id 1xeLg8mnRrgF6jlW97JcJDk1ODcbsdbaydQjohaVf5x8 \
  --find-pending \
  --output-dir "output/$DATE_DIR"
```

This saves `output/$DATE_DIR/topic.json`. Read it:

```bash
TOPIC_ID=$(python3 -c "import json; d=json.load(open('output/$DATE_DIR/topic.json')); print(d['id'])")
TOPIC=$(python3 -c "import json; d=json.load(open('output/$DATE_DIR/topic.json')); print(d['topic'])")
SECTOR=$(python3 -c "import json; d=json.load(open('output/$DATE_DIR/topic.json')); print(d['sector'])")
SHEET_ROW=$(python3 -c "import json; d=json.load(open('output/$DATE_DIR/topic.json')); print(d.get('sheet_row', ''))")

echo "Topic: $TOPIC_ID - $TOPIC ($SECTOR)"
```

If no pending topic found, STOP and report.

---

## Phase 2: Generate LinkedIn Post Text

Using LLM capabilities, generate a LinkedIn post.

### Post Requirements

| Aspect | Specification |
|--------|--------------|
| **Hook** | First line stops the scroll — bold claim, surprising fact, provocative question |
| **Structure** | 2-3 short punchy paragraphs |
| **Business value** | Specific: cost savings, time reduction, accuracy improvement, risk mitigation |
| **Tone** | C-suite / Project Director / Engineering Manager. Thought leader, not marketer |
| **Length** | Max 250 words |
| **Emojis** | Strategic only, max 6. Not decorative. |
| **CTA** | Visit www.edgeengineers.net |
| **Hashtags** | Exactly 4 relevant hashtags at the end |

Save the post text:

```bash
cat > "output/$DATE_DIR/post.json" << 'EOF'
{
  "id": "TOPIC_ID_REPLACE",
  "topic": "TOPIC_REPLACE",
  "sector": "SECTOR_REPLACE",
  "post_text": "FULL POST TEXT HERE\n\nwww.edgeengineers.net\n\n#Hashtag1 #Hashtag2 #Hashtag3 #Hashtag4"
}
EOF
```

(Replace placeholders with actual values.)

---

## Phase 3: Generate Structured Slide Content

Generate structured slide content for the video. Two approaches:

### Option A: LLM-Generated Slides (Recommended)

Use LLM capabilities to create structured slide content from the post. Create a `slides.json` file:

```json
[
  {
    "type": "title",
    "headline": "Main Topic Headline",
    "subtitle": "Sector | EDGE Engineers",
    "sector": "SECTOR_NAME"
  },
  {
    "type": "content",
    "headline": "The Challenge",
    "bullets": [
      "Specific industry pain point or problem",
      "Another key challenge",
      "A third critical issue"
    ]
  },
  {
    "type": "content",
    "headline": "The EDGE Solution",
    "bullets": [
      "How EDGE solves the problem",
      "Key benefit or differentiator",
      "Measurable outcome"
    ]
  },
  {
    "type": "cta",
    "headline": "Ready to transform your operations?",
    "url": "www.edgeengineers.net",
    "subtitle": "ESA Incubatee | MaynoothWorks, Co. Kildare"
  }
]
```

Save as `output/$DATE_DIR/slides.json`.

### Option B: Auto-Generate from Post Text

```bash
POST_TEXT=$(python3 -c "import json; print(json.load(open('output/$DATE_DIR/post.json'))['post_text'])" 2>/dev/null || echo "Post not saved")
```

Then pass `--post-text` to compose (see Phase 7) — it will auto-extract slide content.

---

## Phase 4: Generate SVG Schematics via Moonshot Kimi

Generates professional SVG diagrams and info-graphics using the Moonshot Kimi API.
These are embedded directly into the video slideshow — no image hosting needed.

**Requires:** MOONSHOT_API_KEY set in environment or admin panel.

```bash
if [ -f "output/$DATE_DIR/slides.json" ] && [ -n "$MOONSHOT_API_KEY" ]; then
  python3 scripts/generate_schematics.py \
    --slides "output/$DATE_DIR/slides.json" \
    --topic "$TOPIC" \
    --sector "$SECTOR" \
    --model kimi-k2.6 \
    --moonshot-key "$MOONSHOT_API_KEY" \
    --output-dir "output/$DATE_DIR"
else
  echo "  MOONSHOT_API_KEY not available — skipping schematics"
fi
```

The output is `output/$DATE_DIR/schematics.json` with inline SVGs for each slide.
Content slides get technical diagrams (flowcharts, comparison charts), title/CTA slides get decorative background graphics.

---

## Phase 5: Compose Video

Generates a professional HTML video slideshow. No API keys needed.

```bash
SLIDES_FLAG=""
if [ -f "output/$DATE_DIR/slides.json" ]; then
  SLIDES_FLAG="--slides output/$DATE_DIR/slides.json"
fi

SCHEMATICS_FLAG=""
if [ -f "output/$DATE_DIR/schematics.json" ]; then
  SCHEMATICS_FLAG="--schematics output/$DATE_DIR/schematics.json"
fi

python3 scripts/compose_video.py \
  $SLIDES_FLAG \
  $SCHEMATICS_FLAG \
  --topic "$TOPIC" \
  --sector "$SECTOR" \
  --post-text "$(python3 -c "import json; print(json.load(open('output/$DATE_DIR/post.json'))['post_text'])" 2>/dev/null || echo 'Post not saved')" \
  --output-dir "output/$DATE_DIR"
```

The output is `output/$DATE_DIR/video.html` — a self-contained, auto-advancing video slideshow with:
- Branded EDGE design (light green-gray background, deep green accents, Inter font)
- 3 slide types: title, content (with animated bullets + optional SVG diagram), CTA
- SVG schematics generated by Moonshot Kimi on content slides (technical diagrams, flowcharts)
- Background decorative graphics on title and CTA slides
- Progress bar, dot navigation, keyboard arrow controls
- Slide crossfade + scale transitions with staggered element animations
- Responsive (works on mobile and desktop)

---

## Phase 6: Upload to Google Drive

Upload all generated files to a dated subfolder in the EDGE Smart Video Drive folder.

```bash
DRIVE_FOLDER_ID="1OFc_pa6G2w9GCvNbSvLN-Jn-5sjfVTiG"

python3 scripts/drive_upload.py \
  --folder-id "$DRIVE_FOLDER_ID" \
  --output-dir "output/$DATE_DIR" \
  --topic "$TOPIC"
```

This creates a subfolder like `YYYY-MM-DD-Topic-Name` and uploads all PNGs, HTML, JSON, and MP4 files.

Read the Drive folder URL from the result:

```bash
DRIVE_URL=$(python3 -c "import json; print(json.load(open('output/$DATE_DIR/drive_upload.json'))['folder_url'])")
echo "Drive folder: $DRIVE_URL"
```

---

## Phase 7: Update Sheet Status

Update the topic status in Google Sheets:

```bash
POST_TEXT=$(python3 -c "import json; print(json.load(open('output/$DATE_DIR/post.json'))['post_text'])" 2>/dev/null || echo "")

python3 scripts/sheets_handler.py update \
  --sheet-id 1xeLg8mnRrgF6jlW97JcJDk1ODcbsdbaydQjohaVf5x8 \
  --topic-id "$TOPIC_ID" \
  --row "$SHEET_ROW" \
  --status "Draft Ready" \
  --post-text "$POST_TEXT"
```

---

## Phase 8: Create Summary and Deliver (post-Telegram finalisation)

### Summary file

```bash
# Get Drive URL if uploaded
DRIVE_URL=""
if [ -f "output/$DATE_DIR/drive_upload.json" ]; then
  DRIVE_URL=$(python3 -c "import json; print(json.load(open('output/$DATE_DIR/drive_upload.json'))['folder_url'])")
fi

cat > "output/$DATE_DIR/summary.md" << SUMMARYEOF
# EDGE Smart Video — Content Summary

**Date:** $(date +%Y-%m-%d)
**Topic:** $TOPIC
**Sector:** $SECTOR
**Sheet ID:** $TOPIC_ID

## LinkedIn Post

[See post.json]

## Assets

- HTML Video Slideshow: video.html
- Slide Data: slides.json
- SVG Schematics: schematics.json (diagrams + graphics)
- Google Drive: $DRIVE_URL

## Status

Draft Ready — review and post on LinkedIn.
SUMMARYEOF
```

### Telegram notification

```bash
POST_TEXT_SNIPPET=$(echo "$POST_TEXT" | head -5 | cut -c1-200)

# Get Drive URL if uploaded
DRIVE_URL=""
if [ -f "output/$DATE_DIR/drive_upload.json" ]; then
  DRIVE_URL=$(python3 -c "import json; print(json.load(open('output/$DATE_DIR/drive_upload.json'))['folder_url'])")
fi

DRIVE_LINE=""
if [ -n "$DRIVE_URL" ]; then
  DRIVE_LINE="📁 Drive: $DRIVE_URL"
fi

# Use canonical skills-library path (works in scoped cron environments)
DM_SCRIPT="../../skills-library/agent-job-dm/agent-job-dm.js"
if [ ! -f "$DM_SCRIPT" ]; then
  DM_SCRIPT="skills/agent-job-dm/agent-job-dm.js"
fi

node "$DM_SCRIPT" send --broadcast \
  "🛰 *EDGE Smart Video — Draft Ready*
━━━━━━━━━━━━━━━━━━━━━
📌 *Topic:* $TOPIC
🏭 *Sector:* $SECTOR
🆔 *ID:* $TOPIC_ID
━━━━━━━━━━━━━━━━━━━━━

📝 *Post preview:*
$POST_TEXT_SNIPPET...

━━━━━━━━━━━━━━━━━━━━━
📁 Local: \`output/$(date +%Y-%m-%d)/\`
$DRIVE_LINE
🌐 www.edgeengineers.net

Reply: APPROVE / IMPROVE :suggestion / REJECT :reason"
```

---

## Phase 9: Report

```
╔═══════════════════════════════════════╗
║   EDGE Smart Video Pipeline Results    ║
╚═══════════════════════════════════════╝

📌 Topic:        $TOPIC_ID - $TOPIC
🏭 Sector:       $SECTOR
📊 Slides:       [count from slides.json]
🎨 SVGs:         [count from schematics.json]
📹 Video:        video.html
📊 Sheet:        Updated to Draft Ready
📁 Drive:         Uploaded
📨 Telegram:     Sent
```

---

## Error Recovery

| Failure | Action |
|---------|--------|
| Sheets OAuth fails | Retry `agent-job-secrets get GOOGLE_DRIVE_OAUTH` |
| No pending topics | Report and exit cleanly |
| Moonshot API unavailable | Skip schematics, continue without SVG diagrams |
| Moonshot schematic fails for a slide | Retry once, then continue — compose handles missing entries |
| Compose has no post-text | Use LLM-generated `slides.json` (Option A) instead |
| Drive upload fails | Log error, continue — files still exist locally |
| Telegram fails | Log message, continue |

## Important Notes

- **MOONSHOT_API_KEY** must be added as an agent-job-secret in the admin panel (key: `MOONSHOT_API_KEY`)
- **GOOGLE_DRIVE_OAUTH** is auto-injected for scoped agent jobs
- **Moonshot Kimi K2.6** is the recommended model — strong at technical diagrams, 262K context, supports reasoning
- **agent-job-secrets returns JSON** — always pipe through `python3 -c "import json,sys; print(json.load(sys.stdin)['value'])"` to extract the actual key value
- The HTML video slideshow is always created as the primary deliverable — no API keys needed
- SVG schematics are embedded directly in the HTML — no image hosting, always crisp
- For best results, generate `slides.json` using LLM (Phase 3 Option A) with structured slide content extracted from the LinkedIn post
- The slideshow auto-advances every 5 seconds, supports keyboard navigation, and works on any browser
