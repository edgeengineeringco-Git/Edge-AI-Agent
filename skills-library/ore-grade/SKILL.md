---
name: ore-grade
description: Interpret predicted REE grades and assess economic viability — confidence verification, uncertainty ranges, tonnage and contained metal, cut-off grade assessment, HREE premium, JORC-aligned resource classification, and risk matrix per zone.
---

# Ore Grade Interpretation and Economic Assessment

Assess economic viability, classify the resource, and produce structured grade reports with risk assessment. Works on JSON or CSV input describing one or more mineralised zones/blocks.

## When to use

- You have predicted REE grades (from model inference, assay data, or both) and need an economic read.
- You need to classify a zone to JORC / NI 43-101 category.
- You need a consistent, regulation-safe phrasing for public or investor reports.

## Usage

```bash
python3 skills/ore-grade/scripts/assess_grade.py \
    --input <zones.json|zones.csv> \
    --output <report.json> \
    [--basket-price <USD/kg>] \
    [--metallurgical-recovery <pct>]
```

Arguments:
- `--input` — JSON array or CSV of zone objects (required)
- `--output` — path for the structured report JSON (required)
- `--basket-price` — TREO basket price in USD/kg (default: 30.0; used for economic tier context only)
- `--metallurgical-recovery` — global recovery override in % (default: from input or 70)

### Input schema

Per-zone fields (all optional except `zone_id` and `treo_pct`; defaults applied for missing values):

```
zone_id, x_utm, y_utm, area_m2, depth_m, treo_pct, hreo_treo_ratio,
creo_pct, confidence_score, confidence_tier, data_source,
icp_validation_pts, deposit_type, bulk_density_t_m3,
metallurgical_recovery_pct, notes
```

Confidence tier: `high`, `medium`, `low`, `unreliable`.

### Output schema

```json
{
  "report_date": "2026-06-28",
  "basket_price_usd_kg": 30.0,
  "zones": [
    {
      "zone_id": "A",
      "input": { ... },
      "verified_confidence_tier": "medium",
      "confidence_flag": null,
      "grade_summary": {
        "treo_pct": 1.34,
        "treo_range": [0.94, 1.74],
        "hreo_treo_ratio": 0.22,
        "creo_pct": 0.31,
        "labels": ["HREE-enriched"]
      },
      "tonnage": {
        "area_m2": 45000,
        "depth_m": 50,
        "bulk_density_t_m3": 2.5,
        "tonnage_t": 5625000,
        "treo_tonnes": 75375,
        "recoverable_treo_tonnes": 52762,
        "creo_tonnes": 6457
      },
      "economic": {
        "deposit_type": "carbonatite",
        "cut_off_treo_pct": 1.0,
        "economic_tier": "Economic",
        "hree_premium_applied": false,
        "metallurgical_risk_flags": []
      },
      "risk": {
        "geological": "Medium",
        "analytical": "Low",
        "economic": "Low",
        "overall": "Medium"
      },
      "classification": "Exploration Target",
      "classification_note": "Competent Person review required for Inferred or higher",
      "phrasing": "The data supports a potential economic REE concentration subject to Competent Person review.",
      "warnings": []
    }
  ]
}
```

## Step-by-step methodology

### 1. Confidence tier verification

| Condition | Verified tier |
|---|---|
| ≥ 5 ICP-MS points, CRM in spec, duplicate RPD < 20 %, no matrix flags | High |
| 2–4 ICP-MS points OR pXRF with FP calibration + CRM in spec | Medium |
| pXRF only, no ICP confirmation, or CRM slightly out of spec | Low |
| No QC data, CRM out of spec, matrix flags, < 2 ICP points | Unreliable |

If the verified tier is more conservative than the input `confidence_tier`, both are reported and a flag is added.

**Unreliable zones:** no tonnage or economic estimate is produced; a warning banner is attached.

### 2. Grade uncertainty

Uncertainty multiplier by tier:
- High: ± 15 % relative
- Medium: ± 30 % relative
- Low: ± 50 % relative (order-of-magnitude only)

HREO:TREO > 0.30 → label `HREE-enriched`.
CREO/TREO > 0.25 → label `magnet REE dominant`.

### 3. Tonnage (Medium+ only)

```
Tonnage (t) = area_m2 × depth_m × bulk_density_t_m3
TREO_tonnes = Tonnage × treo_pct / 100
Recoverable_TREO = TREO_tonnes × metallurgical_recovery_pct / 100
CREO_tonnes = Tonnage × creo_pct / 100 × metallurgical_recovery_pct / 100
```

Bulk density defaults by deposit type:
- IAC clay / residual soil: 1.5–1.7 t/m³
- Soft carbonatite / weathered: 2.0–2.3 t/m³
- Fresh carbonatite / hard rock: 2.6–2.9 t/m³
- Beach placer: 1.8–2.0 t/m³

Depth assumption is always reported explicitly — it is the highest-uncertainty parameter.

### 4. Cut-off grade assessment

| Deposit Type | Subeconomic | Marginal | Economic | High Grade |
|---|---|---|---|---|
| Carbonatite (open pit) | < 0.5 % | 0.5–1.0 % | 1.0–3.0 % | > 3.0 % |
| Carbonatite (underground) | < 2.0 % | 2.0–4.0 % | 4.0–8.0 % | > 8.0 % |
| Ion-adsorption clay | < 0.04 % | 0.04–0.07 % | 0.07–0.20 % | > 0.20 % |
| Alkaline / peralkaline | < 0.3 % | 0.3–0.7 % | 0.7–2.5 % | > 2.5 % |
| Placer monazite | < 0.5 % monazite | 0.5–1.0 % | 1.0–3.0 % | > 3.0 % |

**HREE premium:** if HREO:TREO > 0.25, the effective cut-off is reduced 30–50 % and flagged. Compare `treo_pct` against the lower-bound uncertainty range for a conservative read.

### 5. Resource classification (JORC 2012 / NI 43-101)

| Classification | Requirements |
|---|---|
| Exploration Target | Any tier; report as range only; not for public statements |
| Inferred Resource | Low–Medium; geological continuity assumed; 200–400 m spacing |
| Indicated Resource | Medium–High; reasonable continuity; 100–200 m spacing |
| Measured Resource | High only; well-constrained; < 100 m spacing |

**You may only use Inferred or higher if a Competent Person is cited.** Without one, classify as `Exploration Target` regardless of data quality.

### 6. Risk matrix

Geological · Analytical · Economic → Overall = worst axis.

**Geological:** Low (multiple holes, known type) / Medium (surface only, interpreted) / High (single anomaly, no drill control)
**Analytical:** Low (High tier + full QC) / Medium (Medium tier + partial QC) / High (Low/Unreliable)
**Economic:** Low (well above cut-off, robust CREO, simple metallurgy) / Medium (near cut-off, mixed REE, moderate Th) / High (at/below cut-off, complex processing, high Th, LREE-dominant)

### 7. Reporting language (regulatory-safe)

| Situation | Correct phrasing |
|---|---|
| High confidence, above cut-off | "The data supports a potential economic REE concentration subject to Competent Person review." |
| Medium confidence, marginal grade | "Preliminary results are encouraging but require ICP-MS confirmation and additional sampling before economic significance can be assessed." |
| Low confidence | "These results are indicative only. They should not be used for resource estimation or investment decisions." |
| Unreliable data | "Data quality is insufficient for grade interpretation. Re-assay is required before any assessment." |
| Anomaly present, not economic | "A geochemical anomaly is present. Grade is below current economic thresholds but warrants further investigation to characterize extent and depth." |

## Dependencies

- Python 3
- pandas, numpy
