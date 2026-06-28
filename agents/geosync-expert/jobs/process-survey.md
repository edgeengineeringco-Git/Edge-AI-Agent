# Process a Geochemical Survey

You have been triggered to process a new geochemical survey batch. Execute the full pipeline autonomously — do not ask for input.

## Steps

1. **Locate the data** — find the incoming CSV in `data/raw/`. If there are multiple unprocessed files, process the most recent one and note the others.
2. **Run QC** — invoke `geochem-qc`:
   ```bash
   python3 skills/geochem-qc/scripts/geochem_qc.py <csv> --data-type auto
   ```
   - If verdict is `FAIL`: halt, write the issues to `data/processed/validated/QC_FAIL_<stem>.txt`, and notify via `agent-job-dm`. Do not continue.
   - If verdict is `CONDITIONAL`: continue but flag warnings in the summary.
   - If verdict is `PASS`: continue.
3. **Process grades** — invoke `geochem-pipeline`:
   ```bash
   python3 skills/geochem-pipeline/scripts/process_geochemical.py \
     --input <csv> --output-dir data/processed/validated/
   ```
4. **Detect anomalies** — invoke `geochem-anomaly` clustering on the processed CSV:
   ```bash
   python3 skills/geochem-anomaly/scripts/cluster_anomalies.py \
     --input data/processed/validated/<stem>_processed.csv \
     --output data/processed/interpolated/<stem>_clusters.csv \
     --element TREO_pct --x-col x_utm --y-col y_utm
   ```
5. **Classify deposit type** — invoke `geochem-anomaly` classification:
   ```bash
   python3 skills/geochem-anomaly/scripts/classify_deposit.py \
     --input data/processed/validated/<stem>_processed.csv \
     --output data/processed/interpolated/<stem>_classified.csv
   ```
6. **Estimate resources** — invoke `geochem-resource` on the cluster summary:
   ```bash
   python3 skills/geochem-resource/scripts/estimate_resource.py \
     --input data/processed/interpolated/<stem>_clusters.csv \
     --output data/processed/resources/<stem>_resource.json
   ```
7. **Risk matrix** — invoke `geochem-resource` risk:
   ```bash
   python3 skills/geochem-resource/scripts/risk_matrix.py \
     --input data/processed/interpolated/<stem>_clusters.csv \
     --output data/processed/resources/<stem>_risk.json
   ```
8. **Render HTML report** — invoke `geochem-pipeline` report renderer:
   ```bash
   python3 skills/geochem-pipeline/scripts/render_report.py \
     --template skills/geochem-pipeline/templates/report.html \
     --summary data/processed/validated/<stem>_summary.json \
     --anomalies data/processed/interpolated/<stem>_clusters.csv \
     --resources data/processed/resources/<stem>_resource.json \
     --risk data/processed/resources/<stem>_risk.json \
     --output reports/daily/<stem>_report.html \
     --survey-id <stem>
   ```
9. **Notify** — send a concise summary via `agent-job-dm` including: QC verdict, number of clusters, peak TREO, top deposit type, overall risk, and recommendation. If peak TREO > 2.0%, prepend 🚨 HIGH-PRIORITY to the message.

## Notes

- Use `/tmp` for any intermediate working files.
- If any step fails, log the error, skip that step, and continue with the next — do not abort the whole pipeline.
- Always include the JORC disclaimer in any outbound message.
