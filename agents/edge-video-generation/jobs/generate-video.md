# Generate an EDGE corporate video

Accept one structured creative brief, for example:

```json
{
  "title": "EDGE company introduction",
  "target_duration_seconds": 30,
  "audience": "European critical-minerals and geospatial partners",
  "brand_style": "restrained documentary corporate, deep navy and charcoal",
  "narration": {"text": "...", "audio_file": null},
  "shots": [
    {"id": "shot-01", "description": "Aerial Irish terrain at dawn", "duration_seconds": 5, "category": "landscape"}
  ],
  "aspect_ratio": "16:9",
  "resolution": "1920x1080",
  "visual_constraints": ["no text in generated footage", "no watermark"],
  "budget_ceiling_usd": 15,
  "delivery_format": "H.264/AAC MP4, SRT, ZIP"
}
```

## Phase 1 — plan only

Run:

```bash
python3 scripts/edge_video_agent.py plan --brief /path/to/brief.json --project project
```

The command creates the required project folders and plan/manifests without making paid requests. It validates the brief and writes a redacted plan.

Return the approval summary:

- final duration
- number of clips
- exact model route per clip
- tests
- resolution
- estimated maximum cost
- delivery estimate
- risks/limitations

Then ask exactly:

> Approve this generation plan and maximum budget of USD $[amount]?

Do not proceed until the user explicitly confirms.

## Phase 2 — execute after approval

After explicit approval, run:

```bash
python3 scripts/edge_video_agent.py execute --brief /path/to/brief.json --project project --approved-budget 15.00 --approval "Approve this generation plan and maximum budget of USD $15?"
```

Use the configured `VIDEO_GENERATION_API_KEYS` secret. The engine performs validation, cheap category tests, final generations, clip downloads, narration/subtitles, FFmpeg editing, ffprobe validation, manifest writing, and ZIP packaging. It never logs credential values.

Send concise progress updates after tests, final clips, narration, edit, and export. If a request fails, record a redacted error, use the shot fallback once, and stop retries when the budget or attempt limit is reached.
