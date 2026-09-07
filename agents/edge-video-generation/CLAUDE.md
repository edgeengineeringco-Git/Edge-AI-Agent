# EDGE Video Generation Agent

This scoped agent turns a structured creative brief into an approved, cost-controlled AI-video production. It is separate from `edge-smart-video`, which remains the LinkedIn topic/slideshow agent.

## Files

- `SYSTEM.md` — agent identity and safety rules
- `jobs/generate-video.md` — execution contract
- `scripts/edge_video_agent.py` — reusable planning, validation, generation, QC, editing, and packaging engine
- `project/` — runtime project tree; generated project artifacts are intentionally ignored from source control when appropriate

## Provider adapter

The provider API is deliberately isolated in `scripts/edge_video_agent.py`. The adapter requires a documented base URL and endpoint from the configured secret/provider metadata and refuses to guess. It supports environment overrides only for non-secret endpoint metadata:

- `VIDEO_GENERATION_API_BASE_URL`
- `VIDEO_GENERATION_API_MODELS_URL`
- `VIDEO_GENERATION_API_GENERATE_PATH`
- `VIDEO_GENERATION_API_STATUS_PATH`
- `VIDEO_GENERATION_API_DOWNLOAD_PATH`

The API key/credential itself must come from `VIDEO_GENERATION_API_KEYS` via the secrets skill and is never written to disk or logs.

## Important behavior

Planning mode is safe and does not spend money. Generation mode requires an explicit approval phrase and approved maximum budget. If provider metadata cannot be validated, the agent stops before paid generation and explains the limitation without exposing credentials.
