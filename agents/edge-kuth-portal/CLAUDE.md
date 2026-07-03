# EDGE K/U/Th Portal Agent

This agent processes gamma-ray spectral analysis jobs (K/U/Th estimation from .spc files).

## Directory Structure

- `SYSTEM.md` — Agent identity and instructions
- `jobs/` — Job task prompts

## Related Files

- `edge-kuth-portal/estimate_k_u_th_matrix.py` — Core estimation Python script
- `edge-kuth-portal/upload-server.mjs` — Node.js multipart upload receiver (Docker container, zero npm deps)
- `edge-kuth-portal/handle-upload.sh` — Upload handler orchestrator
- `edge-kuth-portal/workflow-config.json` — Workflow configuration document detailing CLI args, energy calibration, reference lines, ROI integration, PAD specs, composition matrix, spectral unmixing, and processing pipeline steps
- `docker-compose.custom.yml` — Upload-server service definition (node:22-alpine, port 3001, Traefik at `/edge-kuth/upload-page`)

## Intake Forms (separate system)

**The client intake forms (project setup + data upload) have been moved to `/intake-portal/`.**
They are completely separate from the K/U/Th pipeline. They run on GitHub Pages + Google Apps Script.

## K/U/Th Pipeline Flow

1. Client visits `/edge-kuth/upload-page` (served by `upload-server.mjs`) and uploads `.spc` files.
2. Upload server saves files to `edge-kuth-portal/jobs/{job_id}/spectra/`.
3. Upload server triggers event-handler webhook at `/edge-kuth/upload`.
4. TRIGGERS.json fires the `agents/edge-kuth-portal` agent.
5. Agent runs estimation via `handle-upload.sh`, sends results via Telegram (agent-job-dm skill).

## Dependencies

The Python engine requires numpy (`python3 -m pip install numpy`).
