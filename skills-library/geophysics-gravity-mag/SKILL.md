---
name: geophysics-gravity-mag
description: Geophysical methods for REE and critical mineral exploration — magnetics, gravity, radiometrics, EM, and IP. Processing, interpretation, and integration with geochemical and geological data.
---

# Geophysics for REE and Critical Mineral Exploration

## When to use

- You need to delineate carbonatite/alkaline complexes (magnetic/radiometric signatures).
- You want to map bedrock geology beneath cover (gravity, magnetics).
- You need to detect sulfide mineralization (EM, IP).
- You want to map alteration zones (radiometrics, magnetics).

## Method Selection by Deposit Type

| Deposit Type | Primary Method | Secondary | Expected Signature |
|---|---|---|---|
| **Carbonatite REE** | Magnetics, Radiometrics | Gravity | High Th/U/K (radiometrics), magnetic low or high depending on Fe content |
| **Alkaline Complex** | Magnetics | Gravity, Radiometrics | Circular magnetic anomaly, gravity high (dense) |
| **Hydrothermal HREE** | Magnetics, EM/IP | Gravity | Magnetic lows (destructive alteration), conductive zones |
| **IOCG** | Magnetics, Gravity, EM | IP | Magnetic high (magnetite), gravity high, conductive |
| **IAC Clay** | Radiometrics | Magnetics | High Th/K (monazite), magnetic low |
| **LCT Pegmatite** | Magnetics, Radiometrics | Gravity | Magnetic low, K anomaly, Li (no direct detection) |
| **Laterite Ni-Co** | EM, Gravity | Magnetics | Conductive (saprolite), density contrast |
| **SEDEX Cu-Co** | Gravity, EM | Magnetics | Gravity low (shale basin), conductive |

## Magnetics

### Carbonatite Signatures
- **Fenitized country rock:** Often magnetic due to addition of magnetite/hematite
- **Carbonatite itself:** Can be magnetic (sövite with magnetite) or non-magnetic (dolomitic)
- **Ring structure:** Circular to elliptical magnetic anomaly with internal complexity
- **Diameter:** Typically 1–5 km for major complexes

### Processing Workflow
```python
import numpy as np
import rasterio
from scipy.ndimage import gaussian_filter, sobel

# Load TMI (Total Magnetic Intensity)
with rasterio.open('mag_tmi.tif') as src:
    tmi = src.read(1)
    profile = src.profile

# 1. Reduce to Pole (RTP) — essential in high latitudes
# Requires inclination (I) and declination (D)
I = -60  # degrees, negative in southern hemisphere
D = 15

# Simplified RTP filter (Fourier domain preferred for accuracy)
from scipy.fft import fft2, ifft2, fftshift

def rtp_filter(tmi, I, D):
    """Frequency domain reduction to pole"""
    ny, nx = tmi.shape
    ky = np.fft.fftfreq(ny)
    kx = np.fft.fftfreq(nx)
    KX, KY = np.meshgrid(kx, ky)
    k = np.sqrt(KX**2 + KY**2)
    k[0, 0] = 1e-10  # avoid division by zero
    
    theta = np.arctan2(KY, KX)
    
    # RTP operator
    rtp_op = 1 / ((np.sin(I) + 1j * np.cos(I) * np.sin(theta - np.radians(D)))**2)
    
    F_tmi = fft2(tmi)
    F_rtp = F_tmi * rtp_op
    return np.real(ifft2(F_rtp))

tmi_rtp = rtp_filter(tmi, I, D)

# 2. First vertical derivative (enhances edges)
dz = sobel(tmi_rtp, axis=0)  # approximate

# 3. Analytic signal amplitude (edge detection)
dx = sobel(tmi_rtp, axis=1)
dy = sobel(tmi_rtp, axis=0)
analytic_signal = np.sqrt(dx**2 + dy**2 + dz**2)

# 4. Tilt derivative (balances large and small anomalies)
# Tilt = arctan(Vertical Derivative / Horizontal Derivative)
from scipy.ndimage import laplace
vertical = laplace(tmi_rtp)
horizontal = np.sqrt(dx**2 + dy**2)
tilt = np.arctan2(vertical, horizontal)

# Save outputs
for name, data in [('rtp', tmi_rtp), ('tilt', tilt), ('analytic', analytic_signal)]:
    profile.update(dtype=rasterio.float32)
    with rasterio.open(f'mag_{name}.tif', 'w', **profile) as dst:
        dst.write(data.astype(rasterio.float32), 1)
```

## Radiometrics

### Uranium-Thorium-Potassium Signatures

| Deposit Type | eU (ppm) | eTh (ppm) | K (%) | Th/U | Interpretation |
|---|---|---|---|---|---|
| **Carbonatite** | 10–100 | 50–500 | 1–5 | 5–10 | Th-rich, U-depleted |
| **Fenite aureole** | 5–20 | 20–100 | 3–8 | 3–8 | K-metasomatism |
| **Monazite placer** | 20–200 | 100–1000 | 1–3 | 5–20 | Extreme Th enrichment |
| **IAC Clay** | 10–50 | 30–200 | 2–6 | 3–8 | Th + K from weathering |
| **Hydrothermal U** | 50–500 | 10–50 | 1–3 | 0.1–1 | U >> Th |
| **Background granite** | 3–10 | 10–40 | 2–5 | 3–5 | Typical crustal |

### Processing
```python
# Ternary radiometric image (RGB = K, eU, eTh)
with rasterio.open('rad_k.tif') as k_src:
    k = k_src.read(1)
with rasterio.open('rad_u.tif') as u_src:
    u = u_src.read(1)
with rasterio.open('rad_th.tif') as th_src:
    th = th_src.read(1)

# Normalize to 0-255 for visualization
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler(feature_range=(0, 255))
k_norm = scaler.fit_transform(k.reshape(-1, 1)).reshape(k.shape)
u_norm = scaler.fit_transform(u.reshape(-1, 1)).reshape(u.shape)
th_norm = scaler.fit_transform(th.reshape(-1, 1)).reshape(th.shape)

rgb = np.stack([k_norm, u_norm, th_norm], axis=-1).astype(np.uint8)

# Ratios
th_k_ratio = th / (k * 10000)  # Th/K ratio
th_u_ratio = th / u
```

## Gravity

### Density Contrast Table
| Rock Type | Density (g/cm³) | Contrast vs. Granite |
|---|---|---|
| Carbonatite | 2.7–3.0 | +0.1 to +0.4 |
| Fenite | 2.6–2.8 | 0 to +0.2 |
| Syenite/Nepehelinite | 2.6–2.7 | 0 to +0.1 |
| Iron Oxide (IOCG) | 4.0–5.0 | +1.5 to +2.5 |
| Shale/Clay | 2.3–2.5 | -0.2 to -0.4 |
| Weathered saprolite | 1.5–2.0 | -0.8 to -1.0 |

### Bouguer Anomaly Processing
```python
# Simple Bouguer correction
def bouguer_correction(elevation, density=2.67, latitude=0):
    """
    elevation: metres above sea level
    density: Bouguer density in g/cm³
    """
    # Free-air correction: +0.3086 mGal/m
    free_air = 0.3086 * elevation
    
    # Bouguer slab correction: -0.0419 * density * elevation
    bouguer_slab = -0.0419 * density * elevation
    
    # Latitude correction (normal gravity)
    sin2lat = np.sin(np.radians(latitude))**2
    normal_gravity = 978031.85 * (1 + 0.005278895 * sin2lat - 0.000023462 * sin2lat**2)
    
    return free_air + bouguer_slab

# Residual anomaly = regional trend removed
from scipy.signal import detrend
residual = detrend(bouguer_anomaly, type='linear')
```

## 3D Inversion (Magnetics)

```python
# SimPEG framework for 3D inversion
from SimPEG import maps, data, data_misfit, regularization, optimization, inverse_problem, directives
from SimPEG.electromagnetics import magnetics as mag

# Mesh definition
from discretize import TensorMesh
mesh = TensorMesh([50, 50, 30])  # dx, dy, dz
mesh.x0 = [-2500, -2500, -2000]  # origin

# Survey
src_field = mag.SourceField([mag.SrcVectMagnetization([0, 0, 1])])
survey = mag.Survey(src_field)

# Forward model
model = np.ones(mesh.nC) * 0.001  # initial susceptibility
sim = mag.Simulation3DIntegral(mesh, survey=survey, chiMap=maps.IdentityMap(mesh))
data = sim.dpred(model)

# Inversion
reg = regularization.WeightedLeastSquares(mesh)
opt = optimization.ProjectedGNCG(maxIter=20)
inv_prob = inverse_problem.BaseInvProblem(data_misfit.L2DataMisfit(sim, data), reg, opt)
```

## Integration with Geochemistry

```python
def integrate_geophysics_geochem(mag_anomaly, rad_th, geochem_points):
    """
    Find geochemical anomalies that correlate with geophysical signatures
    """
    targets = []
    
    for point in geochem_points:
        x, y = point['x'], point['y']
        mag_val = sample_raster(mag_anomaly, x, y)
        th_val = sample_raster(rad_th, x, y)
        
        # Scoring
        score = 0
        if mag_val > np.percentile(mag_anomaly, 90):
            score += 30  # High magnetic
        if th_val > np.percentile(rad_th, 90):
            score += 40  # High Th
        if point['treo_pct'] > 0.5:
            score += 30  # High grade
        
        if score > 60:
            targets.append({
                'x': x, 'y': y,
                'score': score,
                'mag': mag_val,
                'th': th_val,
                'treo': point['treo_pct']
            })
    
    return targets
```

## Best Practices

1. **Always RTP magnetic data** before interpretation (except near equator).
2. **Radiometric data needs stripping:** Remove cosmic, aircraft, and radon backgrounds.
3. **Gravity needs terrain correction** in rugged areas.
4. **Multi-method integration:** No single method is definitive. Magnetic + radiometric + geochem = strong target.
5. **Depth estimation:** Use Euler deconvolution or Werner filtering on magnetic data for source depth.
6. **Noise reduction:** Use upward continuation (smooths near-surface noise) or downward continuation (enhances shallow sources, but unstable).
