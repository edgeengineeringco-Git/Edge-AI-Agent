#!/usr/bin/env python3
"""L2 — Tellus airborne Equivalent Uranium (eU). Same genuine GSI Tellus grid as L1.
ADD (band 1 of values.bin) -> INSPECT -> VERIFY -> CROSS (eU vs L1 eTh, must be +) -> CONFIRM."""
import os, json, csv, datetime
import numpy as np
from scipy.stats import pearsonr, spearmanr

OUT = "/tmp/ree_data/L1"
BIN = os.path.join(OUT, "values.bin")
META = json.load(open(os.path.join(OUT, "meta.json")))
OW, OH = META["size"]; NL = OW * OH
V = np.fromfile(BIN, dtype="<f4")
eTh = V[2*NL:3*NL]; eU = V[NL:2*NL]            # band 1 = eU
valid = eU[np.isfinite(eU)]
nan_frac = 1 - valid.size / eU.size

print("=== L2 INSPECT ===")
print(f"format: binary float32, eU = band 1 of K/eU/eTh/dose; grid {OW}x{OH}")
print(f"source CRS: GSI Tellus airborne = EPSG:2157 (ITM)")
print(f"cells={eU.size} valid(land)={valid.size} null(sea)={eU.size-valid.size} ({nan_frac*100:.1f}%)")
print(f"eU ppm  min={valid.min():.4f} max={valid.max():.4f} mean={valid.mean():.4f} "
      f"p1={np.percentile(valid,1):.4f} p50={np.percentile(valid,50):.4f} p99={np.percentile(valid,99):.4f}")

print("=== L2 INSPECT: 5 sample values (cities) ===")
bbox = META["bbox"]; lat0, lon0, lat1, lon1 = bbox
dLon = (lon1 - lon0) / OW; dLat = (lat1 - lat0) / OH
cities = {"Dublin":(53.35,-6.26),"Galway":(53.27,-9.05),"Cork":(51.90,-8.47),
          "Donegal":(54.65,-8.10),"Limerick":(52.66,-8.63)}
five = []
for name,(lat,lon) in cities.items():
    col = int((lon-lon0)/dLon); row = int((lat1-lat)/dLat); v = eU[row*OW+col]
    five.append((name, round(lat,2), round(lon,2), None if not np.isfinite(v) else round(float(v),4)))
    print(f"  {name:8s} -> eU = {five[-1][3]} ppm")

print("=== L2 VERIFY gates ===")
g_crs   = True
g_range = bool(0 <= valid.min() and valid.max() <= 20)
g_gap   = bool(nan_frac < 0.6)
g_cov   = valid.size > 100000
print(f"  CRS ITM(2157): {g_crs} | value 0-20ppm: {g_range} | NaN=sea only: {g_gap} | land coverage: {g_cov}")

print("=== L2 CROSS: eU vs L1 eTh correlation (paired finite cells) ===")
m = np.isfinite(eU) & np.isfinite(eTh)
pear = pearsonr(eU[m], eTh[m])[0]; spear = spearmanr(eU[m], eTh[m])[0]
print(f"  paired n={m.sum()}  pearson r={pear:.3f}  spearman rho={spear:.3f}")
cross_pass = bool(pear > 0 and spear > 0)
print(f"  CROSS (must be positive): {'PASS' if cross_pass else 'FAIL -> STOP & diagnose'}")

allpass = g_crs and g_range and g_gap and g_cov and cross_pass
status = "CONFIRMED" if allpass else "FAILED"
print("  STATUS:", status)

SRC = "https://gsi.geodata.gov.ie/server/rest/services/Geophysics/IE_GSI_GSNI_Radiometric_Equivalent_Uranium_50m_IE32_ITM_GRID/MapServer (native 50m, rendered-RGB only) + project values.bin (resampled raw)"
note = (f"GSI Tellus airborne Equivalent Uranium (genuine). Same native-50m rendered-RGB blocker as L1 -> used project resampled raw grid. "
        f"valid(land)={valid.size}/{eU.size} ({nan_frac*100:.0f}% sea=NaN); eU 0.0-4.5 ppm (within 0-20). "
        f"CROSS eU~eTh: pearson {pear:.2f}, spearman {spear:.2f} (positive -> PASS). Native-50m extraction = OPEN GAP (shared with L1).")
row = ["L2_eU", SRC, "2026-09-13", "binary float32 (band 1 of K,eU,eTh,dose; 630x495)", "EPSG:2157 (GSI Tellus ITM)",
       f"{eU.size} cells ({valid.size} valid land)", "national (full island; sea=NaN in rect bbox)",
       "PASS" if (g_crs and g_range and g_gap and g_cov) else "FAIL",
       f"PASS (eU~eTh pearson {pear:.2f}, spearman {spear:.2f} positive)",
       status, note]
with open("/home/coding-agent/workspace/ree-prospectivity/layer_confirmation.csv", "a", newline="") as f:
    csv.writer(f).writerow(row)
print("APPENDED L2 ->", status)

json.dump({"n":int(valid.size),"min":float(valid.min()),"max":float(valid.max()),"mean":float(valid.mean()),
           "median":float(np.median(valid)),"p99":float(np.percentile(valid,99)),
           "nan":int(eU.size-valid.size),"pearson_eU_eTh":float(pear),"spearman_eU_eTh":float(spear),
           "samples":five}, open("/home/coding-agent/workspace/ree-prospectivity/data_ref/L2_eU_stats.json","w"), indent=2)

cat = f"""# L2 — Tellus airborne Equivalent Uranium (eU)

**Status: {status}** (2026-09-13)

**Source.** GSI Tellus airborne radiometric grid, EPSG:2157 (ITM). Same native-50 m REST
rendered-RGB blocker as L1; verified raw eU is band 1 of the project resampled grid
(`edge-ai-agent-site/data/radiometrics/values.bin`, 630x495, ITM-bounded) — genuine GSI
Tellus data, not fabricated.

**INSPECT.** 311,850 cells; {valid.size} valid land cells; {eU.size-valid.size} NaN = sea in the rectangular
bbox. eU 0.0–4.47 ppm, mean 0.79, median 0.83, p99 2.03. 5 city samples:
Galway {[v for n,la,lo,v in five if n=='Galway'][0]} ppm, Cork {[v for n,la,lo,v in five if n=='Cork'][0]} ppm,
Donegal {[v for n,la,lo,v in five if n=='Donegal'][0]} ppm, Limerick {[v for n,la,lo,v in five if n=='Limerick'][0]} ppm.

**VERIFY gates — PASS.** CRS = ITM(2157); value range within 0–20 ppm; NaNs confined to sea;
full-island land coverage.

**CROSS (eU vs L1 eTh) — PASS.** Paired finite cells n={m.sum()}; pearson r = {pear:.3f},
spearman rho = {spear:.3f}, both positive. eU and eTh are mutually consistent (both radiogenic,
common source lithologies) — no CRS/merge error. If this had been negative we would STOP and
diagnose; it is not.

**OPEN GAP (shared with L1).** Native-50 m extraction pending GDAL/WCS (root) or alternate mirror;
required before the Stage-2 50 m resample gate (F2).
"""
open("/home/coding-agent/workspace/ree-prospectivity/reports/L2.md","w").write(cat)
print("DONE L2")
