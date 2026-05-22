# EDGE K/U/Th Portal Agent

This agent processes gamma-ray spectral analysis jobs (K/U/Th estimation from .spc files).

## Directory Structure

- `SYSTEM.md` — Agent identity and instructions
- `jobs/` — Job task prompts

## Related Files

- `edge-kuth-portal/estimate_k_u_th_matrix.py` — Core estimation Python script
- `edge-kuth-portal/upload-server.mjs` — Node.js multipart upload receiver (Docker container, zero npm deps)
- `edge-kuth-portal/handle-upload.sh` — Upload handler orchestrator
- `edge-kuth-portal/generate_test_data.py` — Test data generator for validation
- `edge-kuth-portal/workflow-config.json` — Workflow configuration document detailing CLI args, energy calibration, reference lines, ROI integration, PAD specs, composition matrix, spectral unmixing, and processing pipeline steps
- `docker-compose.custom.yml` — Upload-server service definition (node:22-alpine, port 3001, Traefik at `/edge-kuth/upload-page`)

## Pipeline Flow

1. Client submits form at `https://senanaghdam-ai.github.io/Kuth-tools/` (GitHub Pages)
2. Form POSTs multipart data to thepopebot's upload server at `/edge-kuth/upload-page`
3. Upload server saves .spc files and metadata to `edge-kuth-portal/jobs/{job_id}/`
4. Upload server forwards job metadata to event-handler at `/edge-kuth/upload`
5. TRIGGERS.json fires the `agents/edge-kuth-portal` agent
6. Agent runs estimation, sends results via Telegram (agent-job-dm skill)

## Dependencies

The Python engine requires numpy (`python3 -m pip install numpy`).
