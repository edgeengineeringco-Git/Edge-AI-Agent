---
name: core-logging
description: Digital core logging workflows for REE exploration — lithology codes, alteration logging, geotechnical measurements, photo interpretation, and automated structure extraction.
---

# Core Logging for REE Exploration

## When to use

- You have drill core that needs systematic geological logging.
- You want standardized lithology, alteration, and structural codes.
- You need to correlate core logging with geochemistry and geophysics.
- You want to use computer vision to extract structures from core photos.

## Lithology Codes for REE Systems

| Code | Lithology | REE Relevance |
|---|---|---|
| **CBT** | Carbonatite | Primary ore host |
| **FEN** | Fenite (Na-metasomatized) | Alteration aureole, pathfinder |
| **SYE** | Syenite | Associated alkaline rock |
| **NPH** | Nepheline syenite | Associated alkaline rock |
| **ALK** | Alkali feldspar granite | Potential IAC source |
| **GRN** | Granite (biotite/muscovite) | IAC source rock |
| **PEGM** | Pegmatite | Li-Cs-Ta ± REE |
| **APB** | Apatite-biotite rock | REE-bearing accessory |
| **BRT** | Barite vein | Hydrothermal HREE pathfinder |
| **FLU** | Fluorite vein | F-rich hydrothermal system |
| **HMC** | Heavy mineral concentrate | Placer monazite/xenotime |
| **SAP** | Saprolite | Laterite Ni-Co, clay-hosted REE |
| **LIM** | Limonite | Laterite zone |
| **QFP** | Quartz-feldspar porphyry | Potential host |
| **BAS** | Basalt / mafic volcanic | Host in some systems |
| **ARG** | Argillite / shale | Sedimentary host |
| **CHT** | Chert | Banded iron formation assoc. |

## Alteration Codes

| Code | Alteration | Minerals | REE Significance |
|---|---|---|---|
| **ALB** | Albitization | Albite, ± scapolite | Fenitization, Na-metasomatism |
| **POT** | Potassic | K-feldspar, biotite | Carbonatite-related |
| **SIL** | Silicification | Quartz, chalcedony | Hydrothermal overprint |
| **SER** | Sericitization | Sericite, illite | Phyllic alteration |
| **CARB** | Carbonatization | Calcite, dolomite | Carbonatite emplacement |
| **FELD** | Feldspathization | K-feldspar, albite | Alkaline metasomatism |
| **CHL** | Chloritization | Chlorite, epidote | Propylitic, retrograde |
| **HEM** | Hematization | Hematite, goethite | Oxidation, gossan |
| **SAPR** | Saprolitization | Clay, goethite | Weathering, IAC formation |
| **GRE** | Greisenization | Muscovite, topaz, fluorite | Sn-W-REE association |
| **ARGI** | Argillic | Kaolinite, smectite | Advanced weathering |

## Logging Template

```python
CORE_LOG_SCHEMA = {
    "hole_id": "string",
    "from_m": "float",
    "to_m": "float",
    "lithology_code": "string",
    "lithology_description": "text",
    "alteration_codes": "list[string]",
    "alteration_intensity": "int (0-10)",
    "mineralization_codes": "list[string]",
    "mineralization_pct": "float",
    "texture": "string",
    "grain_size": "string",
    "color": "string",
    "hardness": "string",
    "fracture_count_per_m": "int",
    "rqd_pct": "float",
    "core_recovery_pct": "float",
    "structural_features": "list[dict]",
    "vein_description": "text",
    "oxidation_depth_m": "float",
    "photo_references": "list[string]",
    "logged_by": "string",
    "logged_date": "date",
    "reviewed_by": "string",
    "notes": "text"
}
```

## Automated Photo Analysis

```python
import cv2
import numpy as np
from sklearn.cluster import KMeans

def analyze_core_photo(image_path):
    """
    Extract color, texture, and structure from core tray photos
    """
    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Resize for processing
    img_small = cv2.resize(img_rgb, (400, 300))
    pixels = img_small.reshape(-1, 3)
    
    # Dominant colors (K-means)
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_.astype(int)
    
    # Texture analysis (GLCM)
    gray = cv2.cvtColor(img_small, cv2.COLOR_RGB2GRAY)
    
    # Simple edge density as texture proxy
    edges = cv2.Canny(gray, 50, 150)
    edge_density = np.sum(edges > 0) / edges.size
    
    # Fracture detection (horizontal lines in tray photo)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)
    n_fractures = len(lines) if lines is not None else 0
    
    return {
        'dominant_colors': colors.tolist(),
        'edge_density': float(edge_density),
        'detected_fractures': n_fractures,
        'brightness_mean': float(np.mean(gray)),
        'brightness_std': float(np.std(gray))
    }

def detect_core_boxes(image_path):
    """
    Detect individual core boxes in a tray photo for auto-segmentation
    """
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Threshold to find boxes
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 100 and h > 50:  # Filter small noise
            boxes.append({'x': x, 'y': y, 'w': w, 'h': h})
    
    return boxes
```

## Core-Geochemistry Integration

```python
def integrate_core_geochem(core_log_df, assay_df):
    """
    Join core logging with assay data by depth interval
    """
    # Ensure intervals don't overlap in core log
    core_log_df = core_log_df.sort_values(['hole_id', 'from_m'])
    
    results = []
    for _, core_row in core_log_df.iterrows():
        hole = core_row['hole_id']
        from_m = core_row['from_m']
        to_m = core_row['to_m']
        
        # Find overlapping assays
        overlapping = assay_df[
            (assay_df['hole_id'] == hole) &
            (assay_df['from_m'] < to_m) &
            (assay_df['to_m'] > from_m)
        ]
        
        if len(overlapping) > 0:
            # Weighted average by interval overlap
            overlaps = []
            for _, assay in overlapping.iterrows():
                overlap_start = max(from_m, assay['from_m'])
                overlap_end = min(to_m, assay['to_m'])
                overlap_length = overlap_end - overlap_start
                overlaps.append((overlap_length, assay['treo_pct']))
            
            total_overlap = sum(o[0] for o in overlaps)
            weighted_treo = sum(o[0] * o[1] for o in overlaps) / total_overlap
            
            core_row['avg_treo_pct'] = weighted_treo
            core_row['n_assays'] = len(overlapping)
        else:
            core_row['avg_treo_pct'] = None
            core_row['n_assays'] = 0
        
        results.append(core_row)
    
    return pd.DataFrame(results)
```

## Best Practices

1. **Log wet core:** Wetting enhances color and texture visibility. Photos should be wet.
2. **Consistent lighting:** Use the same light source and angle for all photos.
3. **Scale in every photo:** Include ruler or coin for scale.
4. **Depth markers:** Clearly mark meterage on core boxes.
5. **QC overlap:** Senior geologist should review 10% of all logging.
6. **Correlate immediately:** Log → photo → assay in same session when possible.
