---
name: geochem-pipeline
description: End-to-end geochemical data processing — moisture/matrix correction, TREO/HREO/CREO grade computation, CSV + JSON summary output, and HTML交互式报告 generation from a Jinja2 template.
---

# Geochemical Processing Pipeline

The main processing script for geochemical survey data. Normalises and corrects raw CSV → computes grades → writes processed CSV + summary JSON. Also includes a Jinja2 HTML report template for interactive survey summaries.

## When to use

- You have a fresh CSV of pXRF or ICP-MS results (after QC has passed) and need TREO, HREO:TREO, and CREO computed.
- You need a structured JSON summary to feed into downstream anomaly detection or resource estimation.
- You need an interactive HTML report for a survey — see `skills/geochem-pipeline/templates/report.html`.

## Usage — main processing

```bash
python3 skills/geochem-pipeline/scripts/process_geochemical.py \
    --input <csv> \
    --output-dir <dir> \
    [--data-type auto|pxrf|gamma|assay]
```

Arguments:
- `--input` — input CSV file (required)
- `--output-dir` — directory for processed CSV + summary JSON (required; created if missing)
- `--data-type` — `auto` (default), `pxrf`, `gamma`, or `assay`

Outputs (inside `--output-dir`):
- `<stem>_processed.csv` — input rows + `TREO_pct`, `HREO_TREO_ratio` columns added
- `<stem>_summary.json` — `{n_rows, date_processed, input_file, mean_treo_pct, max_treo_pct}`

## Usage — HTML report generation

The HTML report template lives at `skills/geochem-pipeline/templates/report.html`. To render it, use a small Python helper that fills it with your data:

```bash
python3 skills/geochem-pipeline/scripts/render_report.py \
    --summary <summary.json> \
    --anomalies <clusters.csv> \
    --resources <resource.json> \
    [--risk <risk.json>] \
    --output <report.html> \
    --survey-id SURVEY_2026_05_A
```

The template renders:
- Survey metadata (id, date, area, sensors, CRS)
- QC verdict table (samples, blanks, CRMs, duplicates)
- Anomaly cluster table with peak TREO, deposit type, risk, recommendation
- Top-5 resource estimates table
- Recommended actions section

**Important disclaimer baked into every report:** *"This is an AI-assisted analysis. Final interpretation requires Competent Person review per JORC 2012."*

## Processing steps

1. **Moisture flag** — if `moisture_pct` column is present, flag rows > 25 %.
2. **Fe matrix flag** — if `data_type == 'pxrf'` and `Fe_pct` present, flag rows > 15 % (matrix suppression warning).
3. **TREO** — sum the available REE oxide equivalents, with per-element oxide conversion factors (La 1.1728, Ce 1.2284, …). Divide by 10 000 to produce a percent.
4. **HREO:TREO** — (Gd + Tb + Dy + Ho + Er + Tm + Yb + Lu + Y) / (sum of all 15 REE + Y).

## REE → oxide conversion factors

| Element | Factor |
|---|---|
| La | 1.1728 |
| Ce | 1.2284 |
| Pr | 1.2082 |
| Nd | 1.1664 |
| Sm | 1.1596 |
| Eu | 1.1579 |
| Gd | 1.1526 |
| Tb | 1.1762 |
| Dy | 1.1477 |
| Ho | 1.1455 |
| Er | 1.1435 |
| Tm | 1.1421 |
| Yb | 1.1387 |
| Lu | 1.1371 |
| Y | 1.2699 |
| Sc | 1.5338 |

## Dependencies

- Python 3
- pandas
- numpy
- jinja2 (only needed for `render_report.py`)

Install with: `python3 -m pip install pandas numpy jinja2`
