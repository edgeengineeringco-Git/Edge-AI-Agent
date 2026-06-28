---
name: spectral-interpret
description: Interpret gamma-ray spectrometry and pXRF spectral data for REE and critical mineral exploration — data quality assessment, background characterization, REE pattern analysis, chondrite normalization, Ce/Eu anomaly interpretation, deposit-type fingerprinting, and radiometric ratio analysis.
---

# Spectral Data Interpretation

Interpret gamma-ray spectrometry and pXRF data to identify REE and critical mineral anomalies, assess data quality, and produce structured interpretation reports.

## When to use

- You have a gamma-ray spectrometry CSV (K_pct, eU_ppm, eTh_ppm) and need to map radiometric anomalies and Th/U ratios.
- You have a pXRF CSV with REE columns and need to compute TREO, HREO:TREO, Ce anomaly, Eu anomaly, and chondrite-normalized patterns.
- You need to fingerprint a deposit type from its REE signature.
- You need to merge gamma-ray and pXRF data into a bivariate interpretation.

## Usage

```bash
python3 skills/spectral-interpret/scripts/interpret_spectral.py \
    --input <csv> \
    --output <report.json> \
    [--data-type gamma|pxrf|auto] \
    [--anomaly-sigma 3] \
    [--cluster-distance 200]
```

Arguments:
- `--input` — CSV file (required)
- `--output` — path for the JSON interpretation report (required)
- `--data-type` — `gamma`, `pxrf`, or `auto` (default: auto-detect from columns)
- `--anomaly-sigma` — MAD multiplier for anomaly threshold (default: 3)
- `--cluster-distance` — max distance in metres for spatial clustering (default: 200)

Output JSON:

```json
{
  "data_type": "pxrf",
  "qc_tier": "PASS",
  "qc_flags": [],
  "n_samples": 450,
  "background": {"La_ppm": {"median": 45.2, "mad": 12.1, "anomaly_threshold": 81.5}, ...},
  "anomalies": [
    {
      "cluster_id": 1,
      "centroid_x": 450123.0,
      "centroid_y": 6200456.0,
      "peak_treo_pct": 2.15,
      "mean_treo_pct": 1.34,
      "hreo_treo_ratio": 0.22,
      "ce_anomaly": 1.08,
      "eu_anomaly": 0.94,
      "deposit_type_fingerprint": "Carbonatite",
      "n_points": 18
    }
  ],
  "gamma_summary": null
}
```

## Step-by-step methodology

### 1. Data quality assessment

**Gamma-ray checks:**
- Acquisition time < 60 s (ground) or < 1 s (airborne) → flag as unreliable
- Total count rate < 50 cps → possible instrument malfunction
- K/eTh and eU/eTh ratios should be broadly consistent within a lithological unit; step changes suggest drift or crew error
- Exact duplicate values → equipment freeze or data entry error

**pXRF checks:**
- Reading time < 30 s → semi-quantitative only
- Fe_pct > 15 % → matrix suppression likely → flag "Fe-matrix correction required"
- Ca_pct > 20 % → carbonate matrix may inflate Ce and La → flag
- Blank readings: La, Ce < 5 ppm acceptable; above indicates contamination
- Values at/below LOD → note as censored data

**QC tier:** PASS / CONDITIONAL / FAIL (same logic as `geochem-qc`).

### 2. Background characterization

For each element:
- **Median** and **MAD** (more robust than mean/std with outliers)
- Background threshold = median + 2 × MAD (~95th percentile under log-normal)
- Anomaly threshold = median + 3 × MAD (strong anomaly)

**Typical crustal background for comparison:**

| Element | Crustal Avg (ppm) | Typical soil anomaly threshold |
|---|---|---|
| Ce | 60 | > 200 |
| La | 30 | > 100 |
| Nd | 27 | > 90 |
| Y | 21 | > 70 |
| Dy | 3 | > 15 |
| Th | 10 | > 40 |
| eTh (gamma) | varies | > 25 in most terranes |

### 3. REE signature identification

Compute per sample:
- **TREO** = Σ(element_ppm × oxide_factor) for La, Ce, Pr, Nd, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu, Y, Sc
  - Oxide factors: La×1.173, Ce×1.228, Pr×1.208, Nd×1.166, Sm×1.160, Eu×1.158, Gd×1.153, Tb×1.176, Dy×1.148, Ho×1.146, Er×1.143, Tm×1.142, Yb×1.139, Lu×1.137, Y×1.270, Sc×1.534
- **LREO** = La₂O₃ + CeO₂ + Pr₆O₁₁ + Nd₂O₃
- **HREO** = Gd₂O₃ + Tb₄O₇ + Dy₂O₃ + Ho₂O₃ + Er₂O₃ + Tm₂O₃ + Yb₂O₃ + Lu₂O₃ + Y₂O₃
- **HREO:TREO** — > 0.30 is HREE-enriched; typical carbonatite is 0.01–0.08
- **La/Lu chondrite-normalized** — steep positive slope (La/Lu > 50) = LREE enrichment; flat/negative = HREE enrichment
- **Ce anomaly** = Ce_N / √(La_N × Pr_N) where _N = chondrite-normalized. Ce/Ce* > 1.2 (positive) or < 0.8 (negative) is significant
- **Eu anomaly** = Eu_N / √(Sm_N × Gd_N). Eu/Eu* < 0.7 → evolved granite; > 1.3 → plagioclase cumulate or hydrothermal

### 4. Chondrite normalization values (CI chondrite, McDonough & Sun 1995)

La=0.237, Ce=0.613, Pr=0.0928, Nd=0.457, Sm=0.148, Eu=0.0563, Gd=0.199, Tb=0.0361, Dy=0.246, Ho=0.0546, Er=0.160, Tm=0.0247, Yb=0.161, Lu=0.0246

### 5. Deposit-type fingerprinting

| Pattern | Likely Deposit Type |
|---|---|
| Strong LREE enrichment, positive Ce anomaly, high Th/U, high Nb | Carbonatite |
| Flat to HREE enrichment, negative Eu anomaly, low Th | Ion-adsorption clay on granite |
| High Y, Dy, Er relative to La, Ce; xenotime indicator | Hydrothermal (skarn or vein) |
| High Sc, Cr, Ni association | Laterite / ophiolite-related |
| High Ti, Zr, Th, P correlation | Placer monazite-xenotime |

### 6. Gamma-spectrometry interpretation

Radiometric ratios:
- **Th/U ratio:** > 4 = REE-fertile (monazite, bastnäsite, thorite); < 1 = U-dominant (uraninite, coffinite)
- **Th/K ratio:** high Th with low K distinguishes carbonatite/alkaline from granite
- **F-parameter (fertility index):** (eTh + 3.5 × eU) / K_pct — elevated values indicate differentiated, REE-fertile intrusions

Anomaly mapping:
1. Classify each point: background / elevated / anomalous / strong anomaly
2. Spatial clusters: anomalies within 200 m of each other (ground survey)
3. Per cluster: center coordinates, max/mean eTh, Th/U ratio, area, point count
4. Rank by: peak eTh, Th/U ratio, spatial extent

Noise vs. signal:
- Single-point spikes with no spatial neighbors → likely artifact → do not promote
- Linear anomalies along topographic breaks → possible radon emanation → verify
- Coherent spatial patterns matching mapped lithology → geological signal → promote
- Bull's-eye on gridded airborne data → check for flight line artifacts first

## Dependencies

- Python 3
- pandas, numpy, scikit-learn
