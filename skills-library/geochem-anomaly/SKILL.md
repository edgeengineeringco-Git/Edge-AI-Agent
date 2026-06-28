---
name: geochem-anomaly
description: Detect and cluster geochemical anomalies in survey data using DBSCAN and classify deposit types (carbonatite, ion-adsorption clay, hydrothermal HREE, placer monazite) from REE patterns.
---

# Geochemical Anomaly Detection and Classification

Two operations on a geochemical point dataset:
1. **Cluster anomalies** with DBSCAN using a median + 3×MAD threshold.
2. **Classify deposit type** per sample from HREO:TREO ratios, Ce anomaly, and pathfinder element thresholds.

## When to use

- You have a validated CSV of pXRF or assay results with UTM coordinates and REE columns.
- You need to identify spatially coherent high-grade zones for follow-up.
- You need a first-pass deposit-type interpretation to guide exploration strategy.

## Usage

### Cluster anomalies

```bash
python3 skills/geochem-anomaly/scripts/cluster_anomalies.py \
    --input <csv> \
    --output <out.csv> \
    --element TREO \
    --x-col x_utm --y-col y_utm \
    --eps 100 --min-samples 3
```

Arguments:
- `--input` — CSV with at least UTM coords + one element column (required)
- `--output` — path for the cluster summary CSV (required)
- `--element` — column name to threshold on (default: `TREO`)
- `--x-col`, `--y-col` — coordinate column names (default: `x_utm`, `y_utm`)
- `--eps` — DBSCAN neighbourhood radius in **metres** (default: 100)
- `--min-samples` — minimum points per cluster (default: 3)
- `--threshold-sigma` — MAD multiplier for background threshold (default: 3)

Output CSV columns: `cluster_id, centroid_x, centroid_y, peak_value, mean_value, area_estimate_m2, sample_count`

### Classify deposit type

```bash
python3 skills/geochem-anomaly/scripts/classify_deposit.py \
    --input <csv> \
    --output <out.csv>
```

Arguments:
- `--input` — CSV with the 15 REE columns (La_ppm … Lu_ppm) plus Y_ppm, Th_ppm, Ti_ppm, Zr_ppm (required)
- `--output` — path for the annotated CSV (required)

Output: the input CSV with two appended columns:
- `hreo_treo` — HREO / TREO ratio
- `deposit_type` — one of `Carbonatite`, `Ion-adsorption clay`, `Hydrothermal HREE`, `Placer monazite`, `Unknown`

## How it works

### Clustering

1. Compute background as **median + 3 × MAD** of the chosen element.
2. Keep only samples above that threshold.
3. Standardise UTM coordinates with `StandardScaler`.
4. Run `sklearn.cluster.DBSCAN` with the requested `eps` (converted to scaled units) and `min_samples`.
5. Drop noise points (cluster_id == -1) and summarise each remaining cluster by centroid, peak, mean, area estimate, and sample count.

### Classification (chondrite-normalised)

| Rule | Deposit type |
|---|---|
| HREO:TREO < 0.15 AND Ce anomaly > 1.1 AND Th > 30 ppm | Carbonatite |
| HREO:TREO > 0.30 AND Th < 10 ppm | Ion-adsorption clay |
| Y > 50 ppm AND HREO:TREO > 0.35 | Hydrothermal HREE |
| Ti > 50 000 ppm AND Zr > 500 ppm | Placer monazite |

Ce anomaly = (Ce / Ce_chondrite) / sqrt((La / La_chondrite) × (Pr / Pr_chondrite))
with chondrite normalisers Ce=0.613, La=0.237, Pr=0.0928.

## Dependencies

- Python 3
- pandas
- numpy
- scikit-learn

Install with: `python3 -m pip install pandas numpy scikit-learn`
