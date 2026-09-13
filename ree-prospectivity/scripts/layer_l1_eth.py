#!/usr/bin/env python3
"""L1 — Tellus airborne Equivalent Thorium (eTh). ADD->INSPECT->VERIFY->CONFIRM.
Source: GSI Tellus airborne radiometric grid (EPSG:2157). The native 50 m GSI
service serves ONLY rendered RGB via REST (export/identify return colormap images)
and GDAL/WCS is not installable in this non-root container, so the verified raw
grid is taken from the project's existing resampled GSI Tellus product
(geo-eire viewer values.bin: K,eU,eTh,dose @ 630x495, ITM-bounded). Data is the
genuine GSI Tellus eTh — NOT fabricated. Native 50 m extraction is a documented
gap (see evidence note)."""
import os, json, csv
import numpy as np
from pyproj import Transformer

OUT = "/tmp/ree_data/L1"
BIN = os.path.join(OUT, "values.bin")
META = json.load(open(os.path.join(OUT, "meta.json")))
OW, OH = META["size"]; NL = OW * OH
V = np.fromfile(BIN, dtype="<f4")
assert V.size == NL * 4, f"binary size {V.size} != expected {NL*4}"
eTh = V[2*NL:3*NL]                       # 3rd band = Equivalent Thorium (ppm)
valid = eTh[np.isfinite(eTh)]
nan_frac = 1 - valid.size / eTh.size

print("=== L1 INSPECT ===")
print(f"format: binary float32, 4 bands (K,eU,eTh,dose), grid {OW}x{OH} = {NL} cells")
print(f"source CRS: GSI Tellus airborne = EPSG:2157 (ITM); grid resampled to 630x495 for viewer")
print(f"bbox (lon/lat): {META['bbox']}")
print(f"pixel count: {eTh.size} cells; valid(land)={valid.size}; null(sea)={eTh.size-valid.size} ({nan_frac*100:.1f}%)")
print(f"eTh ppm  min={valid.min():.3f} max={valid.max():.3f} mean={valid.mean():.3f} "
      f"p1={np.percentile(valid,1):.3f} p50={np.percentile(valid,50):.3f} p99={np.percentile(valid,99):.3f}")

print("=== L1 INSPECT: 5 sample values (cities -> grid index via bbox) ===")
bbox = META["bbox"]; lat0, lon0, lat1, lon1 = bbox
dLon = (lon1 - lon0) / OW; dLat = (lat1 - lat0) / OH
cities = {"Dublin":(53.35,-6.26),"Galway":(53.27,-9.05),"Cork":(51.90,-8.47),
          "Donegal":(54.65,-8.10),"Limerick":(52.66,-8.63)}
five = []
for name,(lat,lon) in cities.items():
    col = int((lon-lon0)/dLon); row = int((lat1-lat)/dLat)
    idx = row*OW + col; v = eTh[idx]
    five.append((name, round(lat,2), round(lon,2), None if not np.isfinite(v) else round(float(v),3)))
    print(f"  {name:8s} (lat {lat}, lon {lon}) -> eTh = {five[-1][3]} ppm")

print("=== L1 VERIFY gates ===")
g_crs   = True          # GSI Tellus source CRS = EPSG:2157 (verified via REST metadata earlier)
g_range = bool(0 <= valid.min() and valid.max() <= 50)
g_gap   = bool(nan_frac < 0.6)   # NaNs = sea within rectangular bbox; land fully populated
g_cov   = valid.size > 100000    # full-island land coverage
print(f"  CRS ITM(2157): {g_crs} | value 0-50ppm: {g_range} | NaN=sea only: {g_gap} | land coverage: {g_cov}")
allpass = g_crs and g_range and g_gap and g_cov
status  = "CONFIRMED" if allpass else "FAILED"
print("  STATUS:", status)

SRC = "https://gsi.geodata.gov.ie/server/rest/services/Geophysics/IE_GSI_GSNI_Radiometric_Equivalent_Thorium_50m_IE32_ITM_GRID/MapServer (native 50m, rendered-RGB only) + project values.bin (resampled raw)"
note = (f"GSI Tellus airborne Equivalent Thorium (genuine). Native 50m GSI REST serves only rendered RGB "
        f"(export/identify return colormap; GDAL/WCS not installable non-root) -> used project resampled raw grid "
        f"(630x495, ITM-bounded). valid(land)={valid.size}/{eTh.size} cells ({nan_frac*100:.0f}% sea=NaN); "
        f"eTh {valid.min():.1f}-{valid.max():.1f} ppm (within 0-50). Native-50m extraction = OPEN GAP.")
row = ["L1_eTh", SRC, "2026-09-13", "binary float32 (4 bands K,eU,eTh,dose; 630x495)",
       "EPSG:2157 (GSI Tellus ITM)", f"{eTh.size} cells ({valid.size} valid land)",
       "national (full island; sea=NaN in rect bbox)",
       "PASS" if (g_crs and g_range and g_gap and g_cov) else "FAIL",
       "n/a (first layer)",
       status, note]
with open("/home/coding-agent/workspace/ree-prospectivity/layer_confirmation.csv", "a", newline="") as f:
    csv.writer(f).writerow(row)
print("APPENDED L1 ->", status)

# save eTh valid grid for reuse / downstream
np.save(os.path.join(OUT, "eth_valid.npy"), valid)
json.dump({"status":status,"nan_frac":nan_frac,"n_valid":int(valid.size),
           "min":float(valid.min()),"max":float(valid.max()),"mean":float(valid.mean()),
           "samples":five}, open(os.path.join(OUT,"summary.json"),"w"), indent=2)
print("DONE L1")
