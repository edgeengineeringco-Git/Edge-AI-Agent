---
name: geochem-qc
description: Validate geochemical CSV data (pXRF, gamma-ray, ICP-MS) with automated QC checks. Returns a PASS / CONDITIONAL / FAIL verdict based on structure, CRM recovery, duplicate RPD, range bounds, and IQR outlier detection.
---

# Geochemical Quality Control (QC)

Automated QC validation for geochemical survey data. Returns a structured verdict (`PASS`, `CONDITIONAL`, or `FAIL`) plus lists of issues and warnings.

## When to use

- A new CSV of pXRF, gamma-ray, or ICP-MS results has arrived and needs validation before processing.
- You need to decide whether to accept, flag, or reject a batch of assay data.
- You are building a data pipeline and need a QC gate between ingestion and processing.

## Usage

```bash
python3 skills/geochem-qc/scripts/geochem_qc.py <csv_file> [--data-type pxrf|gamma|assay]
```

Arguments:
- `<csv_file>` — path to the CSV file to validate (required)
- `--data-type` — `pxrf`, `gamma`, `assay`, or `auto` (default: `auto`, inferred from column names)

Output: JSON written to stdout with the structure:

```json
{
  "verdict": "PASS",
  "issues": [],
  "warnings": [],
  "n_samples": 450,
  "n_blanks": 22,
  "n_crms": 23,
  "n_duplicates": 45
}
```

## How it works

The script runs six checks in order:

1. **Structure check** — verifies required columns exist for the data type (`pxrf`: sample_id, x_utm, y_utm, La_ppm, Ce_ppm, Fe_pct · `gamma`: sample_id, x_utm, y_utm, K_pct, eU_ppm, eTh_ppm · `assay`: sample_id, La_ppm, Ce_ppm, Nd_ppm, Y_ppm).
2. **QC sample detection** — counts blanks (`BLANK`), certified reference materials (`CRM`/`STD`), and duplicates (`DUP`) by sample_id substring. Warns if none are present in a batch > 20 samples.
3. **CRM recovery** — for each CRM row, checks that element values fall within expected recovery windows (85–115% of certified value). Flags any element outside its window.
4. **Duplicate RPD** — pairs each `_DUP` row with its original and computes the relative percent difference. Warns when RPD > 30% for La, Ce, or Nd.
5. **Range validation** — flags values outside geochemically plausible bounds (e.g. La 0–50 000 ppm, Fe 0–80%, K 0–14%, eU 0–5000 ppm, eTh 0–10 000 ppm).
6. **Outlier detection** — for every numeric column, computes the 3×IQR fence. Warns when > 1% of values are extreme outliers.

**Verdict logic:**
- Any `issue` → `FAIL`
- More than 2 `warnings` (and no issues) → `CONDITIONAL`
- Otherwise → `PASS`

## Integration pattern

```
Trigger (file upload / new CSV)
  ↓
Run geochem_qc.py
  ↓
IF verdict = "PASS"   → continue to processing, log "QC cleared"
IF verdict = "CONDITIONAL" → continue with warning flag, notify analyst
IF verdict = "FAIL"   → HALT, alert analyst "Data rejected, re-assay required", archive failed file
```

## Dependencies

- Python 3
- pandas
- scipy

Install with: `python3 -m pip install pandas scipy`
