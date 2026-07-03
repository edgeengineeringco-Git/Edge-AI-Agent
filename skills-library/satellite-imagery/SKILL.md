---
name: satellite-imagery
description: Process Sentinel-2, ASTER, and Landsat satellite imagery for REE and critical mineral exploration — band ratios, alteration indices, mineral mapping, and automated target generation from remote sensing data.
---

# Satellite Imagery for REE and Critical Mineral Exploration

## When to use

- You need to map alteration zones associated with REE mineralization (fenitization, carbonatite-related, or hydrothermal).
- You want to identify structural lineaments controlling mineralization.
- You need to map iron oxides, clays, or vegetation stress as pathfinders.
- You want to generate exploration targets before boots-on-ground.

## Data Sources

| Sensor | Spatial Resolution | Spectral Bands | Best For |
|---|---|---|---|
| **Sentinel-2** | 10–60 m | 13 bands (VNIR + SWIR) | Clay/iron oxide mapping, vegetation |
| **Landsat-8/9** | 15–100 m | 11 bands | Regional alteration, long time series |
| **ASTER** | 15–90 m | 14 bands (VNIR + SWIR + TIR) | Silicate mineralogy, thermal anomalies |
| **PlanetScope** | 3–5 m | 4 bands (RGB + NIR) | High-res structural mapping |
| **WorldView-3** | 1.2–30 m | 16 bands + SWIR | Detailed mineralogy (expensive) |

## Critical Band Ratios for REE Pathfinders

### Iron Oxide (Gossan / Oxidized Carbonatite)
```
Iron Oxide = B4 (Red) / B2 (Blue)
# Sentinel-2: Band 4 / Band 2
# High values = hematite/goethite (oxidized zones)
```

### Clay Minerals (Alteration / Weathering)
```
Clay Index = B11 (SWIR1) / B12 (SWIR2)
# Sentinel-2: Band 11 / Band 12
# Low values = hydroxyl-bearing minerals (clays, micas)
```

### Carbonate / Fenite (Na-K metasomatism)
```
Carbonate Index = (B3 - B4) / (B3 + B4)  # NDVI-like for carbonate
# Or use ASTER band ratio: B13/B12 for carbonate
```

### Ferrous Iron (Magnetite / Unoxidized)
```
Ferrous Index = B6 / B5  # Landsat
# Or B11 / B8A for Sentinel-2
```

### Advanced Alteration Indices

**Alunite-Kaolinite-Pyrophyllite (AKP) Index:**
```
AKP = (B7 + B5) / B6   # ASTER bands
# High = advanced argillic alteration
```

**Ferrous Iron in Silicates:**
```
FIS = B5 / B4  # ASTER
# High = ferrous silicates (biotite, amphibole)
```

**Quartz Index:**
```
QI = B11 / (B10 + B12)  # ASTER TIR
# High = quartz-rich rocks
```

## Python Implementation

### Sentinel-2 Processing with Rasterio
```python
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.plot import show

# Open Sentinel-2 bands (Level-2A, bottom-of-atmosphere)
with rasterio.open('T33UUB_20240515T100031_B04_10m.jp2') as red_src:
    red = red_src.read(1).astype(float)
    profile = red_src.profile

with rasterio.open('T33UUB_20240515T100031_B02_10m.jp2') as blue_src:
    blue = blue_src.read(1).astype(float)

with rasterio.open('T33UUB_20240515T100031_B11_20m.jp2') as swir1_src:
    swir1 = swir1_src.read(1).astype(float)
    # Resample SWIR to 10m if needed

# Iron Oxide Ratio
iron_oxide = np.divide(red, blue, out=np.zeros_like(red), where=blue!=0)

# Clay Minerals
clay = np.divide(swir1, swir2, out=np.zeros_like(swir1), where=swir2!=0)

# Write output
profile.update(dtype=rasterio.float32, count=1)
with rasterio.open('iron_oxide_ratio.tif', 'w', **profile) as dst:
    dst.write(iron_oxide.astype(rasterio.float32), 1)
```

### Principal Component Analysis for Mineral Mapping
```python
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Stack relevant bands
bands = np.stack([b2, b3, b4, b5, b6, b7, b8, b8a, b11, b12], axis=-1)
rows, cols, n_bands = bands.shape

# Reshape and standardize
X = bands.reshape(-1, n_bands)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# PCA
pca = PCA(n_components=4)
X_pca = pca.fit_transform(X_scaled)

# Reshape back
pca_image = X_pca.reshape(rows, cols, 4)

# PC4 often highlights iron oxides / alteration
plt.imshow(pca_image[:,:,3], cmap='jet')
plt.title('PC4 - Alteration / Iron Oxide')
```

### Lineament Detection (Structural Control)
```python
import cv2
from scipy.ndimage import sobel

# Use panchromatic or NIR band
nir = bands[:,:,7]  # Sentinel-2 B8

# Edge detection (Sobel)
dx = sobel(nir, axis=1)
dy = sobel(nir, axis=0)
magnitude = np.sqrt(dx**2 + dy**2)

# Threshold and vectorize
threshold = np.percentile(magnitude, 95)
lineaments = magnitude > threshold

# Hough Transform for linear features
lines = cv2.HoughLinesP(
    (lineaments * 255).astype(np.uint8),
    rho=1, theta=np.pi/180,
    threshold=100, minLineLength=50, maxLineGap=10
)
# lines contains [x1, y1, x2, y2] for each detected lineament
```

## REE-Specific Remote Sensing Signatures

| Deposit Type | Spectral Signature | Key Bands |
|---|---|---|
| **Carbonatite** | High SWIR1 (clay), high TIR (carbonate), low NDVI | B11, ASTER B13/14 |
| **Fenite (aureole)** | High B6/B7 (Na-metasomatism), altered mafics | B6, B7, B12 |
| **Ion-Adsorption Clay** | Very high SWIR clay indices, vegetation stress | B11, B12, B8 |
| **Hydrothermal HREE** | Iron oxide + clay + quartz, structural control | B4, B11, B12 |
| **Laterite (Ni-Co)** | Iron oxide + Mg-OH, tropical weathering | B6, B11, NDVI |

## Automated Target Generation

```python
def generate_targets(iron_oxide, clay_index, structure, threshold_io=2.0, threshold_clay=0.8):
    """
    Generate exploration targets from multi-criteria analysis.
    """
    # Normalize all layers 0-1
    io_norm = (iron_oxide - iron_oxide.min()) / (iron_oxide.max() - iron_oxide.min())
    clay_norm = 1 - ((clay_index - clay_index.min()) / (clay_index.max() - clay_index.min()))
    struct_norm = (structure - structure.min()) / (structure.max() - structure.min())
    
    # Weighted overlay
    target_score = 0.4 * io_norm + 0.3 * clay_norm + 0.3 * struct_norm
    
    # Threshold for high-priority targets
    high_priority = target_score > np.percentile(target_score, 95)
    
    # Connected component analysis
    from scipy import ndimage
    labeled, n_targets = ndimage.label(high_priority)
    
    targets = []
    for i in range(1, n_targets + 1):
        mask = labeled == i
        y, x = np.where(mask)
        targets.append({
            'target_id': f'TGT_{i:03d}',
            'center_x': float(np.mean(x)),
            'center_y': float(np.mean(y)),
            'area_pixels': int(np.sum(mask)),
            'mean_score': float(np.mean(target_score[mask])),
            'max_io': float(np.max(iron_oxide[mask])),
            'max_clay': float(np.max(clay_norm[mask]))
        })
    
    return pd.DataFrame(targets)
```

## Best Practices

1. **Use Level-2A (BOA) data:** Atmospheric correction is essential for band ratios.
2. **Cloud masking:** Use QA bands or SCL (Scene Classification Layer). Mask clouds, shadows, snow.
3. **Seasonal consistency:** Compare same season images (dry season preferred for tropical areas).
4. **Ground truth:** Always validate satellite targets with field observations or existing drill data.
5. **Spatial resolution awareness:** Sentinel-2 10m pixels average over large areas — use as regional targeting, not precise localization.
6. **Combine with geophysics:** Satellite structure + magnetic/radiometric anomalies = stronger targets.

## Useful APIs and Tools

- **Google Earth Engine (GEE):** `earthengine-api` Python package — cloud-based processing at scale
- **SentinelHub:** Commercial API with free tier (250k requests/month)
- **USGS Earth Explorer:** Free Landsat + ASTER downloads
- **Copernicus Open Access Hub:** Direct Sentinel-2 downloads
- **SEN2COR:** Atmospheric correction processor for Sentinel-2
