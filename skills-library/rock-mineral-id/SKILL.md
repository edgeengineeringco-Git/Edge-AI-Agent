---
name: rock-mineral-id
description: Computer vision and spectral methods for automated rock and mineral identification in REE exploration — core photos, hand specimens, thin sections, and pXRF-assisted identification.
---

# Automated Rock and Mineral Identification

## When to use

- You have core photos or hand specimen photos and want rapid lithology classification.
- You want to identify REE-bearing minerals in thin section images.
- You need to validate pXRF readings against visual mineralogy.
- You want to build a training dataset for ML mineral classification.

## Visual Identification Keys

### Carbonatite vs. Marble (Critical Distinction)
| Feature | Carbonatite | Marble |
|---|---|---|
| Texture | Coarse, inequigranular | Granoblastic, equigranular |
| Minerals | Calcite + apatite + magnetite + pyrochlore | Calcite ± dolomite |
| REE minerals | Bastnäsite, monazite, parisite, synchysite | None |
| Accessory | Magnetite (common), pyrite, barite | Graphite, tremolite |
| Structure | Often brecciated, flow-banded | Bedded, folded |
| Reactivity | Effervesces strongly in HCl | Effervesces strongly |

### Bastnäsite vs. Monazite (Hand Specimen)
| Feature | Bastnäsite-(Ce) | Monazite-(Ce) |
|---|---|---|
| Color | Honey-yellow to brown | Yellow to reddish-brown |
| Crystal form | Tabular, hexagonal | Prismatic, monoclinic |
| Hardness | 4–4.5 | 5–5.5 |
| Luster | Resinous to pearly | Resinous to waxy |
| UV fluorescence | Often weak | Strong yellow-green |
| Specific gravity | 4.9–5.2 | 5.0–5.3 |

### Xenotime vs. Zircon (Heavy Mineral Separation)
| Feature | Xenotime-(Y) | Zircon |
|---|---|---|
| Color | Yellow-brown to reddish | Colorless to pale yellow |
| Crystal form | Prismatic, tetragonal | Prismatic, tetragonal |
| Hardness | 4–5 | 7.5 |
| Luster | Vitreous to resinous | Adamantine |
| Specific gravity | 4.4–5.1 | 4.6–4.7 |
| REE content | High Y, HREE | Low REE, high Zr, Hf |

### Field Indicators of REE Mineralization

1. **Radioactivity:** Hand-held scintillometer or gamma scintillation
2. **UV fluorescence:** Shortwave UV (254 nm) — scheelite (blue), fluorite (various), some apatite
3. **Magnetism:** Magnetite-rich carbonatite will attract magnet
4. **Density:** Heavy mineral concentrates feel distinctly dense
5. **Color:** Yellow-brown staining (iron + REE oxides) in weathered zones

## Computer Vision Pipeline

```python
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB3
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model

def build_mineral_classifier(num_classes=20, img_size=300):
    """
    Build CNN for rock/mineral classification
    """
    base = EfficientNetB3(
        weights='imagenet',
        include_top=False,
        input_shape=(img_size, img_size, 3)
    )
    
    # Freeze base layers initially
    for layer in base.layers:
        layer.trainable = False
    
    x = base.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.3)(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.3)(x)
    predictions = Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs=base.input, outputs=predictions)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

# Training data augmentation for geology images
train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
    rotation_range=360,  # Rocks have no preferred orientation
    width_shift_range=0.1,
    height_shift_range=0.1,
    brightness_range=[0.8, 1.2],
    zoom_range=0.2,
    horizontal_flip=True,
    vertical_flip=True,
    fill_mode='nearest'
)
```

### Thin Section Analysis
```python
import cv2
import numpy as np

def analyze_thin_section(image_path, polarized=False):
    """
    Extract mineralogical features from thin section photomicrographs
    """
    img = cv2.imread(image_path)
    
    if polarized:
        # Under crossed polars: look for birefringence colors
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # High saturation = high birefringence
        saturation = hsv[:,:,1]
        high_biref = saturation > 150
        
        # Bastnäsite: low relief, weak birefringence (gray/white)
        # Monazite: moderate birefringence (yellow/orange)
        # Apatite: low relief, low birefringence
    else:
        # Plane polarized light
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Relief estimation (edge sharpness)
        edges = cv2.Laplacian(gray, cv2.CV_64F)
        relief = np.var(edges)
        
        # Grain size distribution
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        grain_areas = [cv2.contourArea(c) for c in contours if cv2.contourArea(c) > 50]
    
    return {
        'mean_grain_size_px': np.mean(grain_areas) if grain_areas else 0,
        'relief_index': float(relief),
        'n_grains': len(grain_areas)
    }
```

## pXRF + Vision Fusion

```python
def identify_mineral_from_pxrf_and_image(pxrf_reading, image_features):
    """
    Combine pXRF elemental data with visual features for mineral ID
    """
    elements = pxrf_reading  # dict of element ppm
    
    candidates = []
    
    # Rule-based mineral identification
    if elements.get('Ce', 0) > 10000 and elements.get('La', 0) > 5000:
        if elements.get('F', 0) > 5000:
            candidates.append(('bastnäsite', 0.8))
        else:
            candidates.append(('monazite', 0.7))
    
    if elements.get('Y', 0) > 5000 and elements.get('P', 0) > 10000:
        candidates.append(('xenotime', 0.75))
    
    if elements.get('Ca', 0) > 300000 and elements.get('P', 0) > 5000:
        candidates.append(('apatite', 0.6))
    
    if elements.get('Fe', 0) > 500000:
        candidates.append(('magnetite', 0.7))
    
    if elements.get('Ba', 0) > 500000:
        candidates.append(('barite', 0.8))
    
    # Adjust confidence based on visual features
    if image_features.get('magnetic', False):
        # Boost magnetite, reduce others
        candidates = [(name, conf*1.2 if 'magnet' in name else conf*0.9) 
                      for name, conf in candidates]
    
    return sorted(candidates, key=lambda x: x[1], reverse=True)
```

## Best Practices

1. **Standardize photography:** Same lighting, background, scale for all training images.
2. **Multi-view:** Classify from multiple angles — minerals are anisotropic.
3. **Validate with XRD:** Use XRD or SEM-EDS as ground truth for training labels.
4. **Confidence threshold:** Only report identifications > 70% confidence.
5. **Human in the loop:** CV assists, but geologist confirms all critical identifications.
