---
name: geostatistics-kriging
description: Geostatistical analysis for REE prospecting — variography, ordinary/simple kriging, block modeling, uncertainty quantification, and JORC-aligned resource classification. Includes Python code with pykrige, scikit-gstat, and geostatspy.
---

# Geostatistics and Kriging for REE Resource Estimation

## When to use

- You have point sample data (drill holes, trenches, channel samples) with X, Y, Z coordinates and REE grades.
- You need to build a 3D block model or 2D grade surface.
- You need variography to understand spatial continuity and anisotropy.
- You need kriging variance for JORC confidence classification (Measured / Indicated / Inferred).

## Core Concepts

### 1. Variography

The experimental variogram measures spatial continuity:

```
γ(h) = 1/(2N(h)) * Σ [z(xi) - z(xi+h)]²
```

Where `h` is the lag distance, `N(h)` is the number of pairs at that lag.

**Key parameters from fitted model:**
- **Nugget (C₀):** Micro-scale variability + measurement error. High nugget = poor spatial continuity.
- **Sill (C₀ + C):** Total variance. Should approximate sample variance.
- **Range (a):** Distance beyond which samples are uncorrelated.

**Common models:**
| Model | Formula | Use case |
|---|---|---|
| Spherical | γ(h) = C₀ + C·[1.5(h/a) - 0.5(h/a)³] for h ≤ a | Most common for geology |
| Exponential | γ(h) = C₀ + C·[1 - exp(-3h/a)] | Sharp discontinuity near origin |
| Gaussian | γ(h) = C₀ + C·[1 - exp(-3(h/a)²)] | Very smooth continuity |

**Anisotropy:**
- **Geometric anisotropy:** Different ranges in different directions, same sill.
- **Zonal anisotropy:** Different sills in different directions.
- For REE deposits, check horizontal vs vertical continuity — often very different.

### 2. Kriging Types

| Type | When to use | Characteristics |
|---|---|---|
| **Ordinary Kriging (OK)** | Unknown mean, local stationarity | Most common for REE grades |
| **Simple Kriging (SK)** | Known global mean | Faster, used when mean is well-constrained |
| **Universal Kriging (UK)** | Trend present (e.g., depth-related) | Models drift + residuals |
| **Indicator Kriging (IK)** | Threshold exceedance probability | Probability of TREO > cut-off |
| **Co-Kriging** | Secondary correlated variable available | Uses pXRF to improve ICP-MS estimates |
| **Multiple Indicator Kriging** | Full conditional distribution | For simulation and uncertainty |

### 3. Block Kriging

For resource estimation, we krige to blocks (not points):

```python
# Block discretization
n_discretization = 4  # 4x4x4 = 64 points per block
block_variance = average_point_variance_within_block
```

Block kriging variance < point kriging variance because averaging reduces uncertainty.

### 4. JORC Confidence Tiers from Kriging Variance

| Classification | Typical Kriging Variance Threshold | Sample Spacing |
|---|---|---|
| **Measured** | σ²_k < 0.15 × sample variance | ≤ range/4 |
| **Indicated** | 0.15–0.35 × sample variance | range/4 to range/2 |
| **Inferred** | > 0.35 × sample variance | > range/2 |

*Note: These are rules of thumb. JORC requires qualitative assessment too.*

## Python Implementation

### Dependencies
```bash
pip install pykrige scikit-gstat geostatspy pandas numpy matplotlib scipy
```

### Variography workflow
```python
import pandas as pd
import numpy as np
import skgstat as skg
from pykrige.ok import OrdinaryKriging
import matplotlib.pyplot as plt

# Load drill data
df = pd.read_csv('drill_data.csv')  # columns: X, Y, Z, TREO_pct

# Experimental variogram
V = skg.Variogram(
    coordinates=df[['X', 'Y']].values,
    values=df['TREO_pct'].values,
    n_lags=15,
    maxlag=500,  # metres
    model='spherical',
    use_nugget=True
)

# Fit and plot
V.fit()
print(f"Nugget: {V.nugget:.4f}")
print(f"Sill: {V.sill:.4f}")
print(f"Range: {V.range:.1f} m")
print(f"Nugget/Sill ratio: {V.nugget/V.sill:.2%}")

# Directional variograms for anisotropy
angles = [0, 45, 90, 135]
for angle in angles:
    V_dir = skg.Variogram(
        coordinates=df[['X', 'Y']].values,
        values=df['TREO_pct'].values,
        n_lags=12,
        maxlag=500,
        model='spherical',
        directional=True,
        azimuth=angle,
        tolerance=22.5
    )
    V_dir.fit()
    print(f"Angle {angle}°: Range={V_dir.range:.1f}m")
```

### 2D Ordinary Kriging
```python
# Grid definition
grid_x = np.linspace(df['X'].min(), df['X'].max(), 200)
grid_y = np.linspace(df['Y'].min(), df['Y'].max(), 200)

# Ordinary Kriging
OK = OrdinaryKriging(
    x=df['X'].values,
    y=df['Y'].values,
    z=df['TREO_pct'].values,
    variogram_model='spherical',
    variogram_parameters={
        'sill': V.sill,
        'range': V.range,
        'nugget': V.nugget
    },
    verbose=False,
    enable_plotting=False
)

z_krige, ss = OK.execute('grid', grid_x, grid_y)
# z_krige = estimated grades
# ss = kriging variance
```

### 3D Block Model
```python
from pykrige.uk3d import UniversalKriging3D

# Block model grid
block_size = 10  # metres
x_grid = np.arange(df['X'].min(), df['X'].max(), block_size)
y_grid = np.arange(df['Y'].min(), df['Y'].max(), block_size)
z_grid = np.arange(df['Z'].min(), df['Z'].max(), block_size)

UK3D = UniversalKriging3D(
    x=df['X'].values,
    y=df['Y'].values,
    z=df['Z'].values,
    val=df['TREO_pct'].values,
    variogram_model='spherical',
    variogram_parameters={'sill': V.sill, 'range': V.range, 'nugget': V.nugget},
    drift_equations=[1]  # linear drift in Z
)

k3d, v3d = UK3D.execute('grid', x_grid, y_grid, z_grid)

# Build block model DataFrame
blocks = []
for i, x in enumerate(x_grid):
    for j, y in enumerate(y_grid):
        for k, z in enumerate(z_grid):
            blocks.append({
                'X': x, 'Y': y, 'Z': z,
                'TREO_estimate': k3d[i,j,k],
                'kriging_variance': v3d[i,j,k],
                'tonnage': block_size**3 * bulk_density,
                'classification': classify_jorc(v3d[i,j,k], sample_var)
            })
block_model = pd.DataFrame(blocks)
```

### Indicator Kriging (probability above cut-off)
```python
cutoff = 0.5  # % TREO
indicator = (df['TREO_pct'] > cutoff).astype(int)

OK_ind = OrdinaryKriging(
    x=df['X'].values,
    y=df['Y'].values,
    z=indicator.values,
    variogram_model='spherical',
    variogram_parameters={'sill': 0.25, 'range': V.range, 'nugget': 0.01}
)

prob_above, _ = OK_ind.execute('grid', grid_x, grid_y)
# prob_above contains P(TREO > 0.5%) at each grid node
```

## Best Practices for REE

1. **Log-transform if skewed:** REE grades are often lognormal. Work in log-space, back-transform with bias correction (Yamamoto, 2005).
2. **Domain hard boundaries:** Don't krige across geological domains (carbonatite vs. fenite vs. host rock).
3. **Composite to equal length:** Standardize drill composites to 1m or 2m before variography.
4. **Check for trends:** If grade decreases with depth, use Universal Kriging or detrend first.
5. **Validate with cross-validation:** Leave-one-out or k-fold. Compare kriged vs. actual.
6. **Swath plots:** Compare kriged estimates vs. nearest-neighbour in E-W, N-S, and vertical swaths.

## Validation Metrics

| Metric | Formula | Good Value |
|---|---|---|
| Mean Error (ME) | Σ(z* - z)/n | Near 0 (unbiased) |
| Mean Squared Error (MSE) | Σ(z* - z)²/n | Minimized |
| Standardized MSE | Σ[(z* - z)/σ]²/n | Near 1.0 |
| Correlation (ρ) | corr(z*, z) | > 0.7 |

Where z* = kriged estimate, z = actual value, σ = kriging standard deviation.
