---
name: drone-survey
description: Plan and interpret aerial geochemical surveys for REE and critical minerals — drone platform selection, sensor specs, flight grid design, weather constraints, cost analysis, and data processing workflows for gamma / pXRF / hyperspectral / LiDAR.
---

# Drone Survey Systems for REE and Critical Minerals

Authoritative reference + planning tool for aerial survey design, execution, and data interpretation. Covers platform selection, sensor systems, flight planning, processing workflows, accuracy/QC, cost analysis, regulatory framework, ground-survey integration, and troubleshooting.

## When to use

- Planning an aerial survey campaign (platform + sensor selection, grid design, battery logistics)
- Deciding whether to use multirotor vs fixed-wing vs hybrid VTOL for a given area
- Interpreting airborne gamma-ray, pXRF, hyperspectral, or LiDAR data
- Estimating survey cost and ROI
- Troubleshooting airborne data quality issues
- Integrating drone data with ground-truth sampling

## Usage — flight planner

```bash
python3 skills/drone-survey/scripts/plan_flight.py \
    --area-km2 <area> \
    --platform <multirotor|fixed_wing|hybrid_vtol> \
    --sensor <gamma|pxrf|hyperspectral|lidar> \
    --target-type <carbonatite|iac_clay|ree_vein|pegmatite|porphyry> \
    [--output <plan.json>]
```

Arguments:
- `--area-km2` — survey area in km² (required)
- `--platform` — drone class (required)
- `--sensor` — primary sensor (required)
- `--target-type` — deposit type being targeted (required); drives default line spacing and altitude
- `--output` — optional JSON path; if omitted, plan is printed to stdout

Output JSON:

```json
{
  "platform": "fixed_wing",
  "sensor": "gamma",
  "target_type": "carbonatite",
  "line_spacing_m": 100,
  "altitude_m_agl": 150,
  "speed_m_s": 15,
  "flight_time_min": 90,
  "battery_swaps": 3,
  "daily_coverage_km2": 120,
  "survey_days": 4,
  "weather_constraints": "Any weather except icing",
  "estimated_cost_usd": 24000,
  "cost_per_km2": 200
}
```

## Sensor systems at a glance

| Sensor | Weight (kg) | Power (W) | Altitude (m AGL) | Line spacing (m) | Coverage (km²/day) | Direct REE? |
|---|---|---|---|---|---|---|
| Gamma-ray (NaI, 16–32L) | 20–40 | 200–500 | 100–200 | 50–100 | 50–100 | No (K/U/Th proxy) |
| pXRF (Olympus Vanta) | 3.8 | 50–80 | 10–50 | 20–50 | 5–15 | Yes |
| Hyperspectral (VNIR+SWIR) | 2–8 | 50–150 | 50–200 | 20–100 | 50–200 | No (mineral ID) |
| LiDAR | 3–8 | 50–150 | 50–200 | 50–200 | 50–200 | No (structure/DEM) |

## Platform selection

| Platform | Flight time (min) | Payload (kg) | Range (km) | Best for |
|---|---|---|---|---|
| Multirotor (quad) | 12–20 (w/ payload) | 1–2 | 2–5 | < 50 km², close-range detail |
| Multirotor (hex) | 25–45 | 2–5 | 2–5 | pXRF, LiDAR, heavier sensors |
| Multirotor (octo) | 30–50 | 5–10 | 2–5 | Hyperspectral, heavy gamma |
| Fixed-wing (electric) | 60–120 | 2–8 | 20–50 | 100–500 km² regional |
| Hybrid VTOL | 90–180 | 5–15 | 30–100 | Medium-scale mapping |

## Default survey parameters by target

| Target | Primary grid | Detail grid | Altitude (m AGL) |
|---|---|---|---|
| Porphyry Cu (> 1 km) | 400 m lines | 100 m lines | Gamma: 200; pXRF: 50 |
| Carbonatite (100–500 m) | 100 m lines | 50 m lines | Gamma: 150; pXRF: 30 |
| REE vein (10–100 m) | 50 m lines | 20 m lines | pXRF: 20–25 |
| IAC clay (> 1 km) | 200 m lines | 100 m lines | Gamma: 200; pXRF: 40 |
| Pegmatite field | 50 m lines | 25 m lines | pXRF: 20 |

## Weather constraints

| Condition | Gamma | pXRF | Hyperspectral |
|---|---|---|---|
| Rain / wet foliage | ✓ Accept | ✗ Avoid | ✗ (cloud) |
| Cloud cover | ✓ Accept | ✓ Accept | ✗ Clear sky only |
| Wind | < 12 m/s (multi) / < 15 m/s (fixed) | same | same |
| Icing | ✗ No | ✗ No | ✗ No |

## Cost reference (2026 USD)

**Multirotor + pXRF:** $850–1,500/day → $57–100/km²
**Fixed-wing + gamma:** $950–1,500/day → $7.50–30/km² (depends on area)

Cost scales: small (10–50 km²) $60–100/km² · medium (50–500 km²) $30–60/km² · large (> 500 km²) $10–30/km².

## Data processing workflows

### Gamma-ray
1. Download raw (lat, lon, alt, K, eU, eTh, cps, timestamp)
2. QC: dropouts, altitude spikes, cosmic background subtraction, radon stripping
3. Altitude correction: `corrected = raw × (ref_alt / actual_alt)²`
4. Grid via kriging / IDW at 20–50 m
5. Anomaly extraction: pixels > mean + 2σ
6. Report: top-10 clusters with coordinates, peak eU/eTh, Th/U ratio

### pXRF
1. Extract readings (1 per 2–5 s)
2. QC: discard Fe > 20 % or moisture > 25 %, discard reading_time < 30 s
3. Spatial dedup, grid at 10–20 m
4. Feature calc: TREO, HREO:TREO, Ce/Ce*, Eu/Eu*
5. Anomaly detection: median + 3×MAD per lithological domain
6. Merge with gamma grid for bivariate (eU × TREO) maps

### Hyperspectral
1. Geometric correction via GPS/IMU + GCPs
2. Atmospheric correction (ELC or FLAASH/QUAC)
3. Spectral library matching (SAM / SCM) against known minerals
4. Classification: bastnäsite probability > 60 %, kaolinite+goethite > 50 % → IAC clay
5. Merge with pXRF/gamma for quantitative overlay

## Accuracy expectations

| Sensor | Horizontal | Vertical / elemental |
|---|---|---|
| Gamma-ray | ±50–100 m (footprint) | ±20–30 % (eTh, eU) |
| pXRF (drone) | ±3–5 m (RTK) | ±15–30 % (REE) |
| Hyperspectral | ±10–50 cm (georef) | Mineral ID only (80–95 % class. accuracy) |
| LiDAR | ±15–30 cm | ±10–20 cm vertical |

## Regulatory (USA / Canada)

- **Part 107** license required for commercial ops; visual line-of-sight, < 400 ft AGL
- **BVLOS** (beyond visual line of sight): Certificate of Authorization required
- **Class B/C/D** airspace: airspace authorization + NOTAMs
- **Restricted** airspace: Special Flight Authorization
- **Timeline:** Part 107: 2–4 weeks · COA: 4–8 weeks · SFA: 6–12 weeks · Indigenous consultation: 4–16 weeks

## Troubleshooting quick reference

| Symptom | Likely cause | Fix |
|---|---|---|
| Flat gamma signal | Detector malfunction or altitude too high | Lower to 100 m AGL; recalibrate |
| High gamma noise | Solar activity / radon | Re-fly; apply radon stripping |
| pXRF matrix flags (Fe > 20 %) | Natural high-Fe soil | Expected; apply matrix correction |
| pXRF moisture bias | Morning dew / recent rain | Re-fly after 4 hrs sun |
| Kriging huge prediction intervals | Sparse data | Infill sampling or accept uncertainty |
| Hyperspectral mineral ID fails | Calibration off | Re-run atmospheric correction; check GCPs |

## Dependencies

- Python 3
- pandas, numpy (for the planner script)
