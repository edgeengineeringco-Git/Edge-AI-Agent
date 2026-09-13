#!/usr/bin/env python3
"""Reusable grid sampler against a GSI MapServer raster layer via identify.
Returns exact per-cell values at a fixed ITM grid -> reused for L1/L2 cross-check."""
import requests, json, os
import numpy as np
from concurrent.futures import ThreadPoolExecutor

SR = 2157
def sample_service(base, ext, nx=40, ny=55, inset=2000, workers=12, timeout=25):
    xs = np.linspace(ext[0]+inset, ext[2]-inset, nx)
    ys = np.linspace(ext[1]+inset, ext[3]-inset, ny)
    pts = [(float(x), float(y)) for y in ys for x in xs]
    s = requests.Session(); s.headers.update({'User-Agent': 'ree-prospectivity/0.1'})
    def ident(p):
        x, y = p
        u = (f"{base}/identify?geometry={x},{y}&geometryType=esriGeometryPoint&sr={SR}"
             f"&layers=all:0&returnGeometry=false&f=json&tolerance=1")
        for _ in range(3):
            try:
                j = s.get(u, timeout=timeout).json()
                if j.get("results"):
                    r = j["results"][0]; v = r.get("value")
                    if v is None and r.get("attributes"):
                        v = r["attributes"].get("Pixel Value", r["attributes"].get("value"))
                    return (x, y, (float(v) if v not in (None, "") else None))
            except Exception:
                pass
        return (x, y, None)
    out = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for res in ex.map(ident, pts):
            out.append({"x": res[0], "y": res[1], "v": res[2]})
    return out

if __name__ == "__main__":
    import sys
    base = sys.argv[1]; ext = [float(a) for a in sys.argv[2:6]]
    out = sample_service(base, ext)
    print(json.dumps(out))
