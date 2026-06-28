# GeoSync Expert Agent

This agent processes geochemical survey data through a full QC → anomaly → resource → reporting pipeline for REE prospecting.

## Directory Structure

- `SYSTEM.md` — Agent identity and instructions (replaces `agent-job/SYSTEM.md` when scoped)
- `CLAUDE.md` — This file; guidance for AI assistants editing this agent
- `jobs/` — Reusable job prompts referenced from `agent-job/CRONS.json`

## Pipeline

```
Raw CSV → geochem-qc (PASS/CONDITIONAL/FAIL)
         → geochem-pipeline (TREO, HREO:TREO)
         → geochem-anomaly (DBSCAN clustering + deposit classification)
         → geochem-resource (tonnage + risk matrix)
         → geochem-pipeline render_report.py (HTML report)
         → agent-job-dm (Telegram notification)
```

## Reference Skills

- `critical-minerals-ref` — REE element tables, deposit-type TREO ranges, pathfinder elements, Li/Co/Cu/Ni/W thresholds
- `geochem-exploration` — Sampling, grid spacing, field QA, continue/cease criteria

## Dependencies

- Python 3 with: pandas, numpy, scipy, scikit-learn, jinja2
- `agent-job-dm` for Telegram delivery
- `agent-job-secrets` for optional Google Drive OAuth

## Data Layout

```
data/
├── raw/                              (immutable source CSVs)
├── processed/
│   ├── validated/                    (QC-cleared CSVs + QC reports)
│   ├── interpolated/                 (grids, anomaly shapefiles)
│   └── resources/                    (resource + risk JSON)
└── reports/
    ├── daily/                        (per-survey HTML reports)
    ├── weekly/                       (weekly summaries)
    └── alerts/                       (high-priority anomaly alerts)
```
