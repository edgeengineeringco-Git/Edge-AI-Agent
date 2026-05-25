# EDGE Smart Video — Content Generation Pipeline

Execute the following pipeline sequentially. Each phase builds on the previous.

**Sheet ID:** `1xeLg8mnRrgF6jlW97JcJDk1ODcbsdbaydQjohaVf5x8`
**Sheet Name:** `Edge_topics_sample`

---

## Phase 0: Setup

1. Get secrets via `agent-job-secrets`:
   - `GOOGLE_DRIVE_OAUTH` — for Google Sheets access (already in env for scoped agent jobs)
   - `GEMINI_API_KEY` — for Nano Banana images + Veo video (set in admin panel)
   - `SHOTSTACK_API_KEY` — optional, for MP4 video output

2. Create dated output directory:
   ```bash
   DATE_DIR=$(date +%Y-%m-%d)
   mkdir -p "output/$DATE_DIR"
   ```

3. Verify Python3 and scripts:
   ```bash
   python3 scripts/generate_images.py --help > /dev/null && echo "OK"
   python3 scripts/generate_video.py --help > /dev/null && echo "OK"
   python3 scripts/compose_video.py --help > /dev/null && echo "OK"
   python3 scripts/sheets_handler.py --help > /dev/null && echo "OK"
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

## Phase 3: Generate Images

### Option A: Pollinations.ai (free, no key needed)

```bash
python3 scripts/generate_images.py \
  --topic "$TOPIC" \
  --sector "$SECTOR" \
  --output-dir "output/$DATE_DIR" \
  --backend pollinations
```

### Option B: Nano Banana (Gemini, better quality)

```bash
# Need GEMINI_API_KEY in env
python3 scripts/generate_images.py \
  --topic "$TOPIC" \
  --sector "$SECTOR" \
  --output-dir "output/$DATE_DIR" \
  --backend nano-banana \
  --gemini-key "$GEMINI_API_KEY"
```

Backend options:
- `pollinations` — Free, no key, variable quality
- `nano-banana` — Gemini 2.5 Flash Image (60/min free tier)
- `nano-banana-2` — Gemini 3.1 Flash Image Preview (higher quality)
- `nano-banana-pro` — Gemini 3 Pro Image (best quality, paid)

### Verify

Check `output/$DATE_DIR/image_manifest.json` has at least 2/4 success.

---

## Phase 4: Generate Veo 3.1 AI Video (Optional — skip if no GEMINI_API_KEY)

This generates a short AI video clip for use as background/visual content.

```bash
if [ -n "$GEMINI_API_KEY" ]; then
  python3 scripts/generate_video.py \
    --topic "$TOPIC" \
    --sector "$SECTOR" \
    --model veo-3.1-lite-generate-preview \
    --duration 5 \
    --output-dir "output/$DATE_DIR" \
    --gemini-key "$GEMINI_API_KEY"
fi
```

Model options (cheapest first):
- `veo-3.1-lite-generate-preview` — Cost-effective Lite
- `veo-3.1-fast-generate-preview` — Faster, lower quality
- `veo-3.1-generate-preview` — Standard quality

Note: Veo generation takes 30-120 seconds. Check `output/$DATE_DIR/veo_result.json` for status.

---

## Phase 5: Compose Video

```bash
VEO_FLAG=""
if [ -f "output/$DATE_DIR/veo_video.mp4" ]; then
  VEO_FLAG="--veo-video output/$DATE_DIR/veo_video.mp4"
fi

SHOTSTACK_FLAG=""
if [ -n "$SHOTSTACK_API_KEY" ]; then
  SHOTSTACK_FLAG="--shotstack-key $SHOTSTACK_API_KEY"
fi

python3 scripts/compose_video.py \
  --manifest "output/$DATE_DIR/image_manifest.json" \
  --sector "$SECTOR" \
  --topic "$TOPIC" \
  --post-text "$(python3 -c "import json; print(json.load(open('output/$DATE_DIR/post.json'))['post_text'])" 2>/dev/null || echo 'Post not saved')" \
  --output-dir "output/$DATE_DIR" \
  $SHOTSTACK_FLAG \
  $VEO_FLAG
```

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

- Images: slide1, slide2, slide3, cta
- Veo AI Video: veo_video.mp4
- Shotstack Video URL: [check video_result.json]
- HTML Slideshow: slideshow.html
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
  DRIVE_LINE="📁 Drive: \$DRIVE_URL"
fi

node skills/agent-job-dm/agent-job-dm.js send --broadcast \
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

## Phase 8: Report

```
╔═══════════════════════════════════════╗
║   EDGE Smart Video Pipeline Results    ║
╚═══════════════════════════════════════╝

📌 Topic:        $TOPIC_ID - $TOPIC
🏭 Sector:       $SECTOR
🖼 Images:       [check manifest]
🎬 Veo Video:    [check veo_result.json]
🎥 Composition:  [check video_result.json]
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
| Image generation fails | Retry once, skip failed, continue with fewer |
| Veo API quota exceeded | Skip Veo, continue without AI video |
| Shotstack fails | Falls back to HTML slideshow automatically |
| Drive upload fails | Log error, continue — files still exist locally |
| Telegram fails | Log message, continue |

## Important Notes

- **GEMINI_API_KEY** must be set in thepopebot admin panel (not in this repo)
- **GOOGLE_DRIVE_OAUTH** is auto-injected for scoped agent jobs
- **Pollinations.ai** is free but rate-limited (1.5s between requests)
- **Nano Banana** free tier: 60 images/min for Gemini 2.5 Flash
- **Veo 3.1 Lite**: ~$0.05/sec, or free tier with quota limits
- **Shotstack stage**: free tier, 5 renders/day
- The HTML slideshow is always created as a guaranteed deliverable
