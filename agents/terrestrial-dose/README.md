# Irish Terrestrial Dose Indicator

Interactive web GIS for **Ireland only** that estimates terrestrial radiation dose (radon-222, thoron-220, external gamma) at any land point using Irish open data.

**Measurement-grade where Tellus airborne radiometric covers the point.** Tellus measured K/U/Th overrides lithology prior. EPA radon map used as validation. Irish 200 Bq/m³ radon action level (stricter than EU 300).

## Architecture

```
terrestrial-dose/
├── dose_core/
│   └── dose_calculation_core.py   # Core dose formulas (DO NOT MODIFY)
├── tests/
│   └── test_dose_core.py          # 14 validation tests (incl. Irish-specific)
├── api/
│   └── main.py                    # FastAPI backend — Ireland only
├── models/
│   └── analyze_point.py           # Smart analysis on raw Irish data table
├── ingest/
│   ├── ireland_data.py            # Irish open data layer fetchers
│   └── point_sampler.py           # Point sampling (legacy Europe)
├── web/
│   ├── src/
│   │   ├── dose_core.ts           # TypeScript port with Irish radon method
│   │   ├── lithology.ts           # Irish geological provinces (GSI 1:100k)
│   │   ├── analysis.ts            # Templated "Why this dose?" generator
│   │   ├── Map.tsx                 # MapLibre satellite map of Ireland
│   │   ├── Panel.tsx              # Full analysis card
│   │   ├── Triangle.tsx           # D3 three-arm dose triangle
│   │   ├── App.tsx                # Main layout
│   │   └── styles.css             # Dark theme
│   ├── package.json
│   └── vite.config.ts
├── irish-dose-standalone.html     # Self-contained HTML for public repo
└── README.md
```

## Ireland-Specific Data

| Layer | Source | Resolution | Role |
|-------|--------|-----------|------|
| Bedrock geology | GSI 1:100k | 100 m | Lithology backbone |
| Tellus airborne radiometric | GSI Tellus | ~200 m flight line | **Measured K/U/Th — overrides prior** |
| Tellus soil geochemistry | GSI Tellus | point | Direct U/Th/K in soil |
| EPA radon risk map | EPA Ireland | 1 km grid | Predicted radon — validation |
| EPA radiation monitoring | EPA 26 stations | point | Real-time gamma |
| Teagasc soil | Irish SIS | 246 profiles + mapped | Soil properties, permeability |
| GSI faults | GSI structural | vector | Radon migration pathways |
| DEM | EU-DEM / GLO-30 | 25–30 m | Elevation, lineaments |
| Sentinel-2 | Copernicus | 10 m | NDVI, lithology refine |
| ERA5 | Copernicus CDS | ~10 km | Seasonal radon factor |

## Irish Risk Thresholds

| Metric | GREEN | AMBER | RED |
|--------|-------|-------|-----|
| Total dose (mSv/yr) | ≤ 2.2 | 2.2–6.6 | > 6.6 |
| Radon (Bq/m³) | ≤ 100 | 100–**200** | ≥ **200** |
| Gamma rate (nGy/h) | ≤ 59 | 59–1000 | ≥ 1000 |
| Ra-eq (Bq/kg) | ≤ 370 | 370–740 | ≥ 740 |

- **Irish national radon action level: 200 Bq/m³** (stricter than EU BSS 300)
- WHO reference: 100 Bq/m³
- UNSCEAR 2024 global average terrestrial dose: 2.2 mSv/yr

## Physics

All dose calculations originate in `dose_core/dose_calculation_core.py`:

1. **Lithology → Activities**: GSI 1:100k maps to typical Ra-226, Th-232, K-40 (Bq/kg) from UNSCEAR 2000 Annex B.
2. **Tellus override**: Where Tellus airborne K/U/Th available, measured values override lithology prior.
3. **EPA radon override**: Where EPA 1km grid predicted radon available, Irish factor (200 → 6.7 mSv/yr) used.
4. **External Gamma**: Saito & Jacob 1995 coefficients: D = 0.462×Ra + 0.604×Th + 0.041×K (nGy/h).
5. **Radon**: Geogenic Radon Potential (GRP) → indoor Rn (Bq/m³) → dose via Irish DCF (6.7 mSv/yr per 200 Bq/m³).
6. **Thoron**: Global Thoron Potential (GTP) → indoor Tn EEC → dose. Non-linear enhancement for Th-232 > 50 Bq/kg.
7. **Risk**: GREEN ≤ 2.2, AMBER 2.2–6.6, RED > 6.6 mSv/yr **or Rn ≥ 200** (Irish action level).

## Running Tests

```bash
cd terrestrial-dose
python3 -c "
import sys; sys.path.insert(0, '.')
from tests.test_dose_core import *
for fn in [test_world_average_soil, test_granite_radon_dominated_amber,
           test_carbonate_green, test_monazite_thoron_red,
           test_measurement_override, test_radon_action_level,
           test_irish_radon_factor, test_irish_radon_at_100,
           test_risk_class_irish_green, test_risk_class_irish_radon_amber,
           test_risk_class_irish_radon_red, test_risk_class_irish_high_dose_red,
           test_risk_class_irish_raeq_red, test_risk_class_irish_gamma_red]:
    fn(); print('PASS:', fn.__name__)
print('All 14 tests passed')
"
```

Expected: 14 tests pass (6 original + 8 Ireland-specific).

## Running the API

```bash
pip install fastapi uvicorn
cd terrestrial-dose
uvicorn api.main:app --reload --port 8000
```

Endpoints:
- `GET /health` — health check (Ireland-only coverage)
- `GET /sample?lat=53.35&lon=-6.26` — raw Irish data table
- `GET /dose?lat=53.35&lon=-6.26` — full dose fingerprint with Irish risk classification
- `GET /dose/bbox?south=51.4&west=-10.6&north=55.4&east=-5.3&step=0.1` — GeoJSON grid

## Running the Frontend

```bash
cd terrestrial-dose/web
npm install
npm run dev    # Development
npm run build  # Production → dist/
```

## Standalone HTML

`irish-dose-standalone.html` is a self-contained file with all CSS, JS, and MapLibre embedded. Copy this to any static hosting (GitHub Pages, S3, etc.) — no build step required.

## License

Open data. All radiation data from UNSCEAR, ICRP, EU BSS — public domain.
Geological data from GSI (CC BY 4.0), Tellus (open), EPA (open), Teagasc (open).
