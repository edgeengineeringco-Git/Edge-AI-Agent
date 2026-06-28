---
name: geochem-resource
description: Compute quick resource estimates (tonnage, contained metal, JORC-aligned confidence tier) from anomaly clusters and produce a geological/analytical/economic risk matrix with recommendations.
---

# Geochemical Resource Estimation and Risk Assessment

Two operations on an anomaly cluster summary (the output of `geochem-anomaly`):
1. **Resource estimate** — tonnage, contained TREO and CREO metal, confidence tier, economic status.
2. **Risk matrix** — geological, analytical, and economic risk axes with an overall recommendation.

## When to use

- You have a cluster summary CSV and need a first-pass resource number to decide whether to advance or abandon a target.
- You need a standardised risk summary to put in a report or send to the chief geologist.

## Usage

### Resource estimate

```bash
python3 skills/geochem-resource/scripts/estimate_resource.py \
    --input <cluster_summary.csv> \
    --output <resource.json> \
    --bulk-density 2.5 --depth 50
```

Arguments:
- `--input` — cluster summary CSV from `geochem-anomaly` (required)
- `--output` — path for the JSON resource summary (required)
- `--bulk-density` — t/m³, default 2.5 (carbonatite)
- `--depth` — assumed mineralised thickness in metres, default 50

Output JSON:

```json
{
  "area_m2": 45000,
  "tonnage_t": 5625000,
  "mean_treo_pct": 1.34,
  "treo_tonnes": 75375.0,
  "creo_tonnes": 9156.6,
  "mean_hreo_treo_ratio": 0.22,
  "confidence_tier": "Medium",
  "economic_status": "Potentially Economic",
  "depth_assumption_m": 50,
  "bulk_density_assumption": 2.5
}
```

Confidence tiers:
- `n_samples >= 5` → `Medium`
- `n_samples >= 2` → `Low`
- otherwise → `Unreliable`

Economic status: TREO > 1.0 % → `Potentially Economic`; > 0.5 % → `Marginal`; else `Subeconomic`.

### Risk matrix

```bash
python3 skills/geochem-resource/scripts/risk_matrix.py \
    --input <cluster_summary.csv> \
    --output <risk.json> \
    [--drill-csv <drill.csv>]
```

Arguments:
- `--input` — cluster summary CSV (required)
- `--output` — path for the JSON risk matrix (required)
- `--drill-csv` — optional drill-hole data CSV; if present with > 3 holes, geological risk is forced `Low`

Output JSON:

```json
{
  "geological_risk": "Medium",
  "analytical_risk": "Low",
  "economic_risk": "Low",
  "overall_risk": "Medium",
  "recommendation": "Gather more data"
}
|}

Recommendation mapping: `Low` → "Advance to drilling"; `Medium` → "Gather more data"; `High` → "Do not advance".

## Dependencies

- Python 3
- pandas
- numpy
