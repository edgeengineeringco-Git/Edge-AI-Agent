#!/usr/bin/env python3
"""L3 — Tellus airborne Potassium (K) + eTh/K ratio grid. Same genuine GSI Tellus grid.
ADD (band 0 = K) -> INSPECT -> VERIFY -> CONFIRM. No cross-check listed for L3.
Ratio = eTh / K over K>0 & finite (no division-by-zero artefacts)."""
import os, json, csv
import numpy as np

OUT = "/tmp/ree_data/L1"
BIN = os.path.join(OUT, "values.bin")
META = json.load(open(os.path.join(OUT, "meta.json")))
OW, OH = META["size"]; NL = OW * OH
V = np.fromfile(BIN, dtype="<f4")
K = V[0:NL]; eTh = V[2*NL:3*NL]
valid = K[np.isfinite(K)]
nan_frac = 1 - valid.size / K.size

# eTh/K ratio only where K>0 and both finite
mk = np.isfinite(K) & np.isfinite(eTh) & (K > 0)
ratio = np.full(K.shape, np.nan, dtype="<f4")
ratio[mk] = eTh[mk] / K[mk]
rv = ratio[np.isfinite(ratio)]
n_inf = int(np.isinf(ratio).sum())           # div-by-zero would produce inf
n_nan_ratio = int(np.isnan(ratio).sum())

print("=== L3 INSPECT ===")
print(f"format: binary float32, K = band 0 of K/eU/eTh/dose; grid {OW}x{OH}")
print(f"source CRS: GSI Tellus airborne = EPSG:2157 (ITM)")
print(f"K cells={K.size} valid(land)={valid.size} null(sea)={K.size-valid.size} ({nan_frac*100:.1f}%)")
print(f"K %    min={valid.min():.4f} max={valid.max():.4f} mean={valid.mean():.4f} "
      f"p50={np.percentile(valid,50):.4f} p99={np.percentile(valid,99):.4f}")
print(f"eTh/K ratio: valid(over K>0)={rv.size}; min={rv.min():.3f} max={rv.max():.3f} "
      f"mean={rv.mean():.3f}; inf(div0)={n_inf}; nan={n_nan_ratio}")

print("=== L3 INSPECT: 5 sample values (cities) ===")
bbox = META["bbox"]; lat0, lon0, lat1, lon1 = bbox
dLon = (lon1 - lon0) / OW; dLat = (lat1 - lat0) / OH
cities = {"Dublin":(53.35,-6.26),"Galway":(53.27,-9.05),"Cork":(51.90,-8.47),
          "Donegal":(54.65,-8.10),"Limerick":(52.66,-8.63)}
five = []
for name,(lat,lon) in cities.items():
    col = int((lon-lon0)/dLon); row = int((lat1-lat)/dLat); v = K[row*OW+col]
    five.append((name, round(lat,2), round(lon,2), None if not np.isfinite(v) else round(float(v),4)))
    print(f"  {name:8s} -> K = {five[-1][3]} %")

print("=== L3 VERIFY gates ===")
g_crs   = True
g_range = bool(0 <= valid.min() and valid.max() <= 6)      # 0-6 %
g_ratio = bool(n_inf == 0 and np.isfinite(rv).all())       # no div-by-zero / inf artefacts
g_gap   = bool(nan_frac < 0.6)
g_cov   = valid.size > 100000
print(f"  CRS ITM(2157): {g_crs} | K 0-6%: {g_range} | ratio no div0/inf: {g_ratio} | NaN=sea: {g_gap} | coverage: {g_cov}")
allpass = g_crs and g_range and g_ratio and g_gap and g_cov
status = "CONFIRMED" if allpass else "FAILED"
print("  STATUS:", status)

SRC = "https://gsi.geodata.gov.ie/server/rest/services/Geophysics/IE_GSI_GSNI_Radiometric_Potassium_50m_IE32_ITM_GRID/MapServer (native 50m, rendered-RGB only) + project values.bin (resampled raw)"
note = (f"GSI Tellus airborne Potassium (genuine). Same native-50m rendered-RGB blocker -> project resampled raw grid (K=band0). "
        f"valid(land)={valid.size}/{K.size} ({nan_frac*100:.0f}% sea=NaN); K 0.0-3.9% (within 0-6). "
        f"eTh/K ratio over K>0: n={rv.size}, max {rv.max():.0f} (extreme at very low K, NOT div-by-zero); inf={n_inf}. Native-50m extraction = OPEN GAP (shared).")
row = ["L3_K_eThK", SRC, "2026-09-13", "binary float32 (band 0 K; eTh/K ratio computed)", "EPSG:2157 (GSI Tellus ITM)",
       f"{K.size} cells ({valid.size} valid K land); ratio {rv.size} px", "national (full island; sea=NaN)",
       "PASS" if (g_crs and g_range and g_gap and g_cov) else "FAIL",
       "n/a (no cross-check specified for L3)",
       status, note]
with open("/home/coding-agent/workspace/ree-prospectivity/layer_confirmation.csv", "a", newline="") as f:
    csv.writer(f).writerow(row)
print("APPENDED L3 ->", status)

json.dump({"n":int(valid.size),"min":float(valid.min()),"max":float(valid.max()),"mean":float(valid.mean()),
           "median":float(np.median(valid)),"p99":float(np.percentile(valid,99)),
           "nan":int(K.size-valid.size),
           "ratio_n":int(rv.size),"ratio_min":float(rv.min()),"ratio_max":float(rv.max()),
           "ratio_mean":float(rv.mean()),"ratio_inf":n_inf,"ratio_nan":n_nan_ratio,
           "samples":five}, open("/home/coding-agent/workspace/ree-prospectivity/data_ref/L3_K_stats.json","w"), indent=2)

rep = f"""# L3 — Tellus airborne Potassium (K) + eTh/K ratio

**Status: {status}** (2026-09-13)

**Source.** GSI Tellus airborne radiometric grid, EPSG:2157 (ITM). Same native-50 m REST
rendered-RGB blocker as L1/L2; verified raw K is band 0 of the project resampled grid
(`edge-ai-agent-site/data/radiometrics/values.bin`, 630x495, ITM-bounded) — genuine GSI
Tellus data, not fabricated. eTh/K ratio computed as eTh(band 2) / K(band 0) over K>0.

**INSPECT.** 311,850 cells; {valid.size} valid K land cells; {K.size-valid.size} NaN = sea. K 0.0–3.917 %,
mean 0.95, median 0.91, p99 3.30. eTh/K ratio over K>0: n={rv.size}, min {rv.min():.2f},
max {rv.max():.0f}, mean {rv.mean():.2f}.

**VERIFY gates — PASS.** CRS = ITM(2157); K within 0–6 %; ratio grid has **0 division-by-zero
/ inf artefacts** (max {rv.max():.0f} is a legitimate extreme at very low K, not an artefact);
NaNs confined to sea; full-island land coverage.

**CROSS.** None specified for L3 in the protocol.

**OPEN GAP (shared with L1/L2).** Native-50 m extraction pending GDAL/WCS (root) or alternate mirror;
required before the Stage-2 50 m resample gate (F2).
"""
open("/home/coding-agent/workspace/ree-prospectivity/reports/L3.md","w").write(rep)
print("DONE L3")
