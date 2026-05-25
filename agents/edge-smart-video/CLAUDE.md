# EDGE Smart Video Content Agent

This agent produces LinkedIn-ready video content from topic queue.

## Directory Structure

- `SYSTEM.md` — Agent identity and instructions
- `jobs/generate-content.md` — Content generation pipeline (the main job)
- `scripts/generate_images.py` — Image generation (Pollinations or Nano Banana)
- `scripts/compose_video.py` — Video composition (Shotstack or HTML fallback)
- `output/` — Generated content (images, video, post text)

## Pipeline

1. Read pending topic from Google Sheets (via curl + sheets API, or local file)
2. Generate LinkedIn post text and image prompts using LLM
3. Run `scripts/generate_images.py` to create 4 slides
4. Run `scripts/compose_video.py` to render video
5. Save all output to `output/YYYY-MM-DD-topic-slug/`
6. Send Telegram notification with post text + video link

## Configuration

Secrets are fetched via the `agent-job-secrets` skill:
- `SHOTSTACK_API_KEY`: For video rendering (stage API = free tier)
- `GEMINI_API_KEY`: For Nano Banana image generation (optional upgrade)
- `GOOGLE_SHEETS_ID`: Content tracker sheet ID

## Topics Source

Topics can come from:
1. **Google Sheets** (primary) — Requires sheet ID in secrets
2. **Local file** `input/topics.csv` — Fallback for local testing

Topic format: ID, Topic, Sector, Status, Notes
