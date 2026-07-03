---
name: structural-geology
description: Structural geology analysis for REE and critical mineral exploration — fault kinematics, fold geometry, lineament analysis, stress field reconstruction, and structural controls on mineralization.
---

# Structural Geology for REE Exploration

## When to use

- You need to understand how structures control REE mineralization (faults as fluid conduits, folds as traps).
- You want to analyze drill core for structural features (foliation, lineation, shear zones).
- You need to reconstruct paleo-stress fields to predict mineralized trends.
- You want to generate 3D structural models from map and drill data.

## Key Structural Controls on REE Deposits

| Deposit Type | Key Structures | Mineralization Pattern |
|---|---|---|
| **Carbonatite** | Ring faults, radial dykes, caldera collapse | Concentric + radial ore zones |
| **Alkaline Complex** | Cone sheets, ring dykes,fenite aureole faults | Contact breccia, stockwork |
| **Hydrothermal HREE** | Shear zones, brittle-ductile faults, fold hinges | Vein arrays, replacement fronts |
| **IOCG** | Major crustal faults, transtensional pull-aparts | Stratabound + discordant breccia |
| **IAC Clay** | Sub-horizontal, gravity-driven | No strong structural control |
| **Pegmatite (Li)** | Tensional fractures, boudin necks, fold hinges | Podiform, zoned |

## Fault Analysis

### Kinematic Indicators
- **Slickenlines:** Pitch on fault plane indicates slip direction
- **Drag folds:** Indicate sense of movement
- **Riedel shears:** R (15°), R' (75°), P (opposite R), Y (parallel to main) — indicate shear sense
- **Mineral fibers:** Growth direction shows opening vector

### Fault Classification for Exploration
```python
def classify_fault_exploration_relevance(fault):
    """
    Score fault for REE exploration potential
    """
    score = 0
    
    # Orientation relative to regional trend
    if 45 <= abs(fault['azimuth'] - regional_trend) <= 135:
        score += 30  # Oblique faults = fluid pathways
    
    # Kinematics
    if fault['kinematics'] in ['extensional', 'transtensional']:
        score += 40  # Dilatant = fluid flow
    elif fault['kinematics'] == 'strike-slip':
        score += 25  # Can be fluid conduit
    elif fault['kinematics'] == 'compressional':
        score += 5   # Less favorable
    
    # Association with intrusions
    if fault['dist_to_intrusion'] < 500:
        score += 20
    
    # Evidence of alteration
    if fault['alteration'] in ['fenitization', 'hematite', 'silicification']:
        score += 15
    
    # Length
    if fault['length_m'] > 1000:
        score += 10  # Major structures control camp-scale
    
    return min(score, 100)
```

## Stereonet Analysis

```python
import mplstereonet
import matplotlib.pyplot as plt
import numpy as np

# Structural measurements from field/drill core
strikes = [45, 50, 48, 52, 47, 49, 51]  # foliation strikes
dips = [35, 38, 36, 40, 37, 39, 38]     # foliation dips

# Plot on stereonet
fig = plt.figure()
ax = fig.add_subplot(111, projection='stereonet')
ax.pole(strikes, dips, markersize=5, label='Foliation poles')

# Contour the poles
ax.density_contourf(strikes, dips, measurement='poles', cmap='Reds', alpha=0.5)

# Best-fit girdle = fold axis
plunge, bearing = ax.fit_girdle(strikes, dips)
ax.plane(bearing, 90-plunge, color='blue', linewidth=2, label=f'Fold axis: {plunge:.1f}/{bearing:.1f}')

plt.legend()
plt.title('Structural Fabric Analysis')
```

## 3D Structural Modeling

```python
import pyvista as pv
import numpy as np

# Fault surfaces from drill intercepts and map traces
fault1_points = np.array([[x1, y1, z1], [x2, y2, z2], ...])
fault1_surface = pv.PolyData(fault1_points).delaunay_2d()

# Folded stratigraphic surface
strat_points = np.array([[x, y, z] for x, y, z in stratigraphy])
strat_surface = pv.PolyData(strat_points).delaunay_2d()

# Visualization
plotter = pv.Plotter()
plotter.add_mesh(fault1_surface, color='red', opacity=0.7, label='Fault')
plotter.add_mesh(strat_surface, color='green', opacity=0.5, label='Stratigraphy')
plotter.add_legend()
plotter.show()
```

## Stress Field Reconstruction

```python
def reconstruct_stress_tensor(fault_data):
    """
    Use fault slip data to reconstruct paleo-stress tensor
    fault_data: list of {'strike', 'dip', 'rake', 'slip_sense'}
    """
    from scipy.optimize import minimize
    
    def misfit(stress_tensor, fault_data):
        total_misfit = 0
        for fault in fault_data:
            # Predicted shear stress direction
            predicted_rake = compute_shear_direction(stress_tensor, fault)
            # Angular misfit
            misfit = angular_difference(predicted_rake, fault['rake'])
            total_misfit += misfit
        return total_misfit
    
    # Optimize stress tensor (3 principal stresses + 3 orientations)
    result = minimize(misfit, x0=initial_guess, args=(fault_data,))
    return result.x
```

## Structural Target Generation

```python
def generate_structural_targets(faults, folds, intrusions, geochem_anomalies):
    """
    Generate targets at structural intersections
    """
    targets = []
    
    # Fault intersections
    for i, f1 in enumerate(faults):
        for f2 in faults[i+1:]:
            if intersects(f1, f2):
                intersection = compute_intersection(f1, f2)
                score = structural_intersection_score(f1, f2)
                
                # Boost if near geochem anomaly
                if min_distance(intersection, geochem_anomalies) < 200:
                    score += 30
                
                if score > 60:
                    targets.append({
                        'type': 'fault_intersection',
                        'location': intersection,
                        'score': score,
                        'rationale': f'{f1["id"]} x {f2["id"]} intersection'
                    })
    
    # Fold hinge zones near faults
    for fold in folds:
        hinge = fold['hinge_line']
        nearby_faults = [f for f in faults if distance(hinge, f) < 300]
        for fault in nearby_faults:
            target = nearest_point(hinge, fault)
            targets.append({
                'type': 'fold_hinge_fault',
                'location': target,
                'score': 75,
                'rationale': 'Fold hinge near fault = dilation zone'
            })
    
    return targets
```

## Drill Core Structural Logging

```python
def log_core_structure(image_path):
    """
    Automated core photo analysis for structural features
    """
    import cv2
    
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detect foliation/banding
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, 
                            minLineLength=100, maxLineGap=10)
    
    # Measure alpha angle (angle between structure and core axis)
    core_axis = 90  # vertical core
    if lines is not None:
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.degrees(np.arctan2(y2-y1, x2-x1))
            angles.append(abs(angle - core_axis))
        
        alpha = np.median(angles)
        return {
            'alpha_angle': alpha,
            'n_structures': len(lines),
            'structure_intensity': len(lines) / img.shape[0]  # per metre
        }
```

## Best Practices

1. **Map at multiple scales:** Regional (1:50,000) for camp-scale control, local (1:5,000) for target-scale.
2. **Measure everything:** Strike, dip, kinematic indicators, mineralization relationship.
3. **3D thinking:** Structures are not 2D lines on maps. Use drill data to understand plunge and dip.
4. **Timing:** Establish paragenesis — pre-mineralization vs. syn-mineralization vs. post-mineralization structures.
5. **Anisotropy:** Structural anisotropy controls kriging search ellipses — feed this into geostatistics.
