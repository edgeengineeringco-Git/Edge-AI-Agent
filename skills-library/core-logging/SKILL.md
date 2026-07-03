---
name: core-logging
description: Digital drill core logging for REE and critical mineral exploration — lithology, alteration, mineralization, structure, geotechnical parameters, and automated photo interpretation.
---

# Drill Core Logging for REE Exploration

## When to use

- You need to log drill core for lithology, alteration, and mineralization.
- You want standardized logging codes for database entry.
- You have core photos and want automated feature detection.
- You need to calculate RQD, fracture density, and other geotechnical parameters.

## Standard Logging Codes

### Lithology Codes (Simplified)
| Code | Description | REE Relevance |
|---|---|---|
| **CARB** | Carbonatite (sövite, beforsite, rauhaugite) | Primary ore host |
| **FEN** | Fenite (Na-K metasomatized host rock) | Alteration aureole, pathfinder |
| **SYEN** | Syenite / Nepheline syenite | Common alkaline association |
| **PHON** | Phonolite | Alkaline volcanic association |
| **GRAN** | Granite / Leucogranite | Parent of IAC weathering |
| **PEGM** | Pegmatite | LCT (Li-Cs-Ta) mineralization |
| **SHAL** | Shale / Mudstone | SEDEX host |
| **BREC** | Breccia | Hydrothermal / IOCG ore |
| **OXID** | Oxidized zone / Gossan | Secondary enrichment |
| **SAPR** | Saprolite / Laterite | Ni-Co, IAC weathering |

### Alteration Codes
| Code | Minerals | Interpretation |
|---|---|---|
| **FENI** | Albite, orthoclase, aegirine, arfvedsonite | Fenitization — carbonatite proximity |
| **HEMI** | Hematite, goethite | Oxidation — near-surface or fluid flow |
| **SILI** | Quartz, chalcedony | Silicification — hydrothermal |
| **CHLO** | Chlorite, epidote | Propylitic — distal alteration |
| **ARGI** | Kaolinite, smectite | Argillic — acid alteration |
| **PHYL** | Sericite, pyrite | Phyllic — intermediate alteration |
| **POTA** | K-feldspar, biotite | Potassic — proximal porphyry |
| **FLUO** | Fluorite, apatite | F-rich hydrothermal — REE association |
| **BARI** | Barite, celestine | Ba-Sr enrichment — carbonatite |

### Mineralization Codes
| Code | Description | Grade Indicator |
|---|---|---|
| **BAST** | Bastnäsite visible | High LREE |
| **MONA** | Monazite visible | High Th, LREE-MREE |
| **XENO** | Xenotime visible | High HREE, Y |
| **ALLA** | Allanite visible | LREE in silicate |
| **APAT** | Apatite — fluorapatite | P-REE association |
| **SYNC** | Synchysite, parisite | Secondary REE carbonate |
| **SPOD** | Spodumene visible | Li pegmatite |
| **COBA** | Cobaltite, erythrite | Co mineralization |
| **PENT** | Pentlandite | Ni-Co sulfide |

## Digital Logging Form

```python
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class CoreLogInterval:
    hole_id: str
    from_m: float
    to_m: float
    lith_code: str
    lith_description: str
    
    # Alteration
    alt_code: Optional[str] = None
    alt_intensity: int = 0  # 0-100%
    
    # Mineralization
    min_code: Optional[str] = None
    min_form: str = "disseminated"  # disseminated, vein, massive, stockwork, replacement
    min_abundance: int = 0  # 0-100%
    
    # Structure
    foliation_dip: Optional[float] = None
    foliation_strike: Optional[float] = None
    fracture_density: Optional[float] = None  # per metre
    fracture_fill: Optional[str] = None
    
    # Geotechnical
    rqd: Optional[float] = None  # Rock Quality Designation
    core_recovery: Optional[float] = None  # %
    hardness: str = "medium"  # very_soft, soft, medium, hard, very_hard
    
    # Color (Munsell or simple)
    color: str = ""
    
    # Photos
    photo_ids: List[str] = None
    
    # Assay link
    sample_id: Optional[str] = None
    
    # Logger info
    logged_by: str = ""
    logged_date: str = ""
    reviewed_by: Optional[str] = None
    
    def thickness(self):
        return self.to_m - self.from_m
```

## RQD Calculation

```python
def calculate_rqd(core_pieces: list, interval_length: float):
    """
    Calculate Rock Quality Designation
    core_pieces: list of piece lengths in metres
    interval_length: total interval length in metres
    """
    # Sum of core pieces > 10 cm (0.1 m)
    sum_qualifying = sum(p for p in core_pieces if p >= 0.1)
    rqd = (sum_qualifying / interval_length) * 100
    
    # Classification
    if rqd > 90:
        quality = "Excellent"
    elif rqd > 75:
        quality = "Good"
    elif rqd > 50:
        quality = "Fair"
    elif rqd > 25:
        quality = "Poor"
    else:
        quality = "Very Poor"
    
    return rqd, quality
```

## Automated Core Photo Analysis

```python
import cv2
import numpy as np
from sklearn.cluster import KMeans

def analyze_core_photo(image_path):
    """
    Automated analysis of core tray photo
    """
    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # 1. Core recovery estimation
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Count core pixels vs tray pixels
    core_pixels = np.sum(binary > 0)
    total_pixels = binary.size
    recovery_estimate = (core_pixels / total_pixels) * 100
    
    # 2. Color analysis (alteration/mineralization indicator)
    pixels = img_rgb.reshape(-1, 3)
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    colors = kmeans.cluster_centers_.astype(int)
    labels = kmeans.labels_
    color_percentages = np.bincount(labels) / len(labels)
    
    # Identify dominant colors
    dominant_colors = []
    for color, pct in zip(colors, color_percentages):
        dominant_colors.append({
            'rgb': color.tolist(),
            'percentage': float(pct),
            'description': describe_color(color)
        })
    
    # 3. Texture analysis (fracture density proxy)
    edges = cv2.Canny(gray, 50, 150)
    edge_density = np.sum(edges > 0) / edges.size
    
    # 4. Fluorescence detection (scheelite, fluorite)
    # Would need UV photo separately
    
    return {
        'recovery_estimate': float(recovery_estimate),
        'dominant_colors': dominant_colors,
        'edge_density': float(edge_density),
        'fracture_proxy': 'high' if edge_density > 0.1 else 'low'
    }

def describe_color(rgb):
    """Simple color descriptor for geological logging"""
    r, g, b = rgb
    if r > 150 and g < 100 and b < 100:
        return "red_brown (hematite/oxidized)"
    elif r > 150 and g > 150 and b < 100:
        return "yellow_brown (goethite/limonite)"
    elif g > 150 and r < 100:
        return "green (chlorite/epidote)"
    elif r > 200 and g > 200 and b > 200:
        return "white/pale (silica/carbonate)"
    elif r < 80 and g < 80 and b < 80:
        return "dark (sulfide/magnetite)"
    else:
        return "mixed/intermediate"
```

## Core Photo Stitching

```python
def stitch_core_photos(photo_paths):
    """
    Stitch multiple core tray photos into continuous log image
    """
    images = [cv2.imread(p) for p in photo_paths]
    
    # Detect tray edges for alignment
    stitched = cv2.hconcat(images)
    
    # Add depth markers
    depth_interval = 1.0  # metres per photo
    for i, img in enumerate(images):
        depth = i * depth_interval
        cv2.putText(stitched, f"{depth:.1f}m", 
                   (i * img.shape[1] + 10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    return stitched
```

## Best Practices

1. **Log before assaying:** Complete geological log before seeing assays to avoid bias.
2. **Consistent intervals:** Use 1m or 2m standard intervals for geochemical comparison.
3. **Photo every box:** Core tray photos are legal records. Include scale, hole ID, depth.
4. **Wet and dry:** Photograph core both wet (color enhanced) and dry (texture visible).
5. **UV light:** Check for scheelite (blue-white fluorescence) and fluorite (violet).
6. **Magnet test:** Simple field test for magnetite content.
7. **Acid test:** 10% HCl on carbonate — vigorous effervescence = calcite, weak = dolomite.
