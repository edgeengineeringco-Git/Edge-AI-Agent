# EDGE Smart Video — Content Generation Pipeline

Execute the following pipeline sequentially. Each phase builds on the previous.

## Phase 0: Setup

1. Create dated output directory: `output/YYYY-MM-DD-topic-slug/`
2. Fetch secrets:
   - `SHOTSTACK_API_KEY` — for video rendering (optional, HTML fallback works without it)
   - `GEMINI_API_KEY` — for Nano Banana image backend (optional, Pollinations is free)
   - `GOOGLE_SHEETS_ID` — content tracker sheet ID (optional, use local fallback)
3. Check Python3 available: `which python3`

## Phase 1: Fetch Topic

### Option A: Google Sheets (preferred if GOOGLE_SHEETS_ID is available)

Use Google Sheets API to fetch the first row where Status = "Pending":

```bash
# Alternative: Export sheet as CSV
curl -sL "https://docs.google.com/spreadsheets/d/$GOOGLE_SHEETS_ID/export?format=csv" \
  -o /tmp/edge_topics.csv
```

Parse the CSV to find the first Pending row. Extract: ID, Topic, Sector, Notes.

### Option B: Local file fallback

Check if `input/topics.csv` exists. If not, create a demo entry:

```csv
ID,Topic,Sector,Status,Notes
001,Advancements in Autonomous Drilling Systems,Civil Automation,Pending,
002,AI-Powered Geotechnical Analysis,Geo-Engineering,Pending,
```

Pick the first Pending entry.

### Validate

- Topic and Sector must be non-empty strings
- If no Pending topics found, report and exit

## Phase 2: Generate LinkedIn Post Text

Using your LLM capabilities, generate a LinkedIn post about the topic.

### Post Requirements

| Element | Specification |
|---------|--------------|
| **Hook** | First line must stop the scroll — bold claim, surprising fact, or provocative question |
| **Structure** | 2-3 short punchy paragraphs |
| **Business value** | Specific benefits (cost savings, time reduction, accuracy improvement, risk mitigation) |
| **Tone** | C-suite / Project Director / Engineering Manager audience. Thought leader, not marketer |
| **Length** | Max 250 words |
| **Emojis** | Strategic only, max 6. Not decorative. |
| **CTA** | Visit www.edgeengineers.net |
| **Hashtags** | Exactly 4 relevant hashtags at the end |

### Also Generate Image Prompts

Create 4 image prompts for the video slides:

| Slide | Style |
|-------|-------|
| **Slide 1** | Professional engineering/technology background related to the sector |
| **Slide 2** | Infographic/technical diagram style about the specific topic |
| **Slide 3** | Team/people working on the technology |
| **CTA Slide** | Abstract tech network background with EDGE branding colors (dark + cyan) |

Save the post text and image prompts to a content file:
```bash
cat > "output/$DATE_DIR/post_content.json" << 'CONTENT_EOF'
{
  "id": "TOPIC_ID",
  "topic": "TOPIC",
  "sector": "SECTOR",
  "post_text": "FULL_POST_TEXT",
  "image_prompts": {
    "slide1": "PROMPT_1",
    "slide2": "PROMPT_2",
    "slide3": "PROMPT_3",
    "cta": "PROMPT_CTA"
  }
}
CONTENT_EOF
```

## Phase 3: Generate Images

Run the image generation script:

```bash
# Default: Pollinations.ai (free, no API key needed)
python3 scripts/generate_images.py \
  --topic "$TOPIC" \
  --sector "$SECTOR" \
  --output-dir "output/$DATE_DIR" \
  --backend pollinations

# For better quality (if GEMINI_API_KEY is available):
# python3 scripts/generate_images.py \
#   --topic "$TOPIC" \
#   --sector "$SECTOR" \
#   --output-dir "output/$DATE_DIR" \
#   --backend nano-banana \
#   --gemini-key "$GEMINI_API_KEY"
```

### Verify Images

- Check each PNG file was created (> 2KB)
- If any image failed, note it but continue (the video composition handles missing images)

## Phase 4: Compose Video/Render

Run the video composition script:

```bash
# With Shotstack (needs SHOTSTACK_API_KEY)
python3 scripts/compose_video.py \
  --manifest "output/$DATE_DIR/image_manifest.json" \
  --sector "$SECTOR" \
  --topic "$TOPIC" \
  --post-text "$POST_TEXT" \
  --shotstack-key "$SHOTSTACK_API_KEY" \
  --output-dir "output/$DATE_DIR"

# Without Shotstack (creates HTML slideshow instead)
# python3 scripts/compose_video.py \
#   --manifest "output/$DATE_DIR/image_manifest.json" \
#   --sector "$SECTOR" \
#   --topic "$TOPIC" \
#   --post-text "$POST_TEXT" \
#   --output-dir "output/$DATE_DIR" \
#   --force-html
```

### Check result

Read `output/$DATE_DIR/video_result.json` to confirm:
- `video_url` (if Shotstack was used) or
- `html_slideshow` (HTML fallback path)

## Phase 5: Create Output Summary

Create a comprehensive summary file:

```bash
cat > "output/$DATE_DIR/summary.md" << 'EOF'
# EDGE Smart Video — Content Summary

**Date:** YYYY-MM-DD
**Topic:** [Topic]
**Sector:** [Sector]
**ID:** [Topic ID]

## LinkedIn Post

[Full post text]

## Video

- Shotstack URL: [URL or N/A]
- HTML Slideshow: [path or N/A]
- Images: slide1.png, slide2.png, slide3.png, cta.png

## Status

Ready for review.
EOF
```

## Phase 6: Deliver

### Update topic status

If using Google Sheets, mark the topic as "Draft Ready" (or record locally).

### Send via Telegram

Use the `agent-job-dm` skill to notify admins:

```bash
node skills/agent-job-dm/agent-job-dm.js send --broadcast \
  "🛰 *EDGE Video Draft Ready for Review*
━━━━━━━━━━━━━━━━━━━━━
📌 Topic: $TOPIC
🏭 Sector: $SECTOR
━━━━━━━━━━━━━━━━━━━━━

📝 *Post:*
$POST_TEXT

━━━━━━━━━━━━━━━━━━━━━
🎬 *Video:* $VIDEO_URL
🌐 www.edgeengineers.net
━━━━━━━━━━━━━━━━━━━━━
Reply:
✅ APPROVE
✏️ IMPROVE : suggestion
❌ REJECT : reason"
```

## Phase 7: Report

Output a final status report:

```
✅ Pipeline complete
📁 Output: output/$DATE_DIR/
📝 Post: [Saved]
🖼 Images: [X/4 generated]
🎬 Video: [URL or path]
📨 Telegram: [Sent/Not sent]
```

## Error Recovery

| Failure | Action |
|---------|--------|
| Image generation fails | Retry once, skip failed slide, continue |
| Shotstack fails | Fall back to HTML slideshow automatically |
| Telegram fails | Log the message, continue |
| Topic fetch fails | Use local demo topic |
| Script error | Check stderr, try with --help for options |

## Important Notes

- **Pollinations.ai is free** — rate limit to 1 request per 1.5 seconds (script handles this)
- **Shotstack stage** is free tier — 5 renders/day limit
- **Nano Banana** (Gemini API) is a paid upgrade — only use if GEMINI_API_KEY is available in secrets
- The HTML slideshow is always created as a backup
- All generated files go in the dated output directory
