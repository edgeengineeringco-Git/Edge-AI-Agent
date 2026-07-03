---
name: rock-mineral-id
description: Computer vision and spectral methods for automated rock and mineral identification in exploration — core photos, hand specimens, thin sections, and pXRF-assisted mineralogy.
---

# Rock and Mineral Identification

## When to use

- You have drill core photos or hand specimen photos and want automated identification.
- You need to identify minerals in the field using simple tests.
- You want to link pXRF elemental data to likely mineralogy.
- You have thin section images and want modal mineralogy.

## Field Identification Key for REE Host Rocks

### Carbonatite Identification
| Test | Result |
|---|---|
| **Acid (HCl)** | Strong effervescence |
| **Color** | Cream, white, buff, brown; sometimes banded |
| **Texture** | Coarse-grained, equigranular; fenite contact zone |
| **Heavy minerals** | Magnetite, pyrochlore, apatite, phlogopite |
| **Associated rocks** | Syenite, nephelinite, ijolite within 1–2 km |
| **Magnetism** | Variable — can be strongly magnetic |

### Ion-Adsorption Clay (IAC)
| Test | Result |
|---|---|
| **Texture** | Earthy, crumbly, sticky when wet |
| **Color** | White, pink, red, yellow (lateritic) |
| **Context** | Over granite, deeply weathered (>10 m) |
| **pXRF** | Elevated REE, low Th/U in barren zones, high Th in mineralized |
| **XRD** | Kaolinite, halloysite, illite dominant |

### LCT Pegmatite
| Test | Result |
|---|---|
| **Texture** | Very coarse-grained (>5 cm crystals), zoned |
| **Key minerals** | Spodumene (white/pink blade), lepidolite (purple mica), petalite |
| **pXRF** | High Li (proxy: Rb, Cs, Ta), Nb, Be |
| **Associated** | Tourmaline (black, elbaite), beryl, cassiterite |

### Laterite (Ni-Co)
| Test | Result |
|---|---|
| **Profile** | Ferricrete (cap) → limonite → saprolite → bedrock |
| **Color** | Red-brown (limonite), green (garnierite in saprolite) |
| **pXRF** | Ni, Co, Mn, Fe; Cr in bedrock |
| **Hardness** | Ferricrete = very hard; saprolite = can dig with shovel |

## Automated Photo Identification

```python
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model

# Rock type classifier
def build_rock_classifier(num_classes=10, input_shape=(224, 224, 3)):
    base = EfficientNetB0(
        weights='imagenet',
        include_top=False,
        input_shape=input_shape
    )
    
    x = base.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(256, activation='relu')(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    predictions = Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs=base.input, outputs=predictions)
    
    # Fine-tune last 20 layers
    for layer in base.layers[:-20]:
        layer.trainable = False
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

# Classes for REE exploration
ROCK_CLASSES = [
    'carbonatite',
    'fenite',
    'syenite',
    'granite',
    'pegmatite',
    'laterite_saprolite',
    'shale',
    'breccia',
    'gossan',
    'barren_host'
]
```

## Mineral Identification from pXRF Chemistry

```python
def infer_mineralogy_from_pxrf(elements):
    """
    Infer likely mineralogy from pXRF elemental signature
    """
    minerals = []
    
    # REE-bearing minerals
    if elements['Ce_ppm'] > 10000 and elements['La_ppm'] > 5000:
        if elements['F_ppm'] > 5000:
            minerals.append(('bastnäsite', 0.8))
        else:
            minerals.append(('monazite', 0.7))
    
    if elements['Y_ppm'] > 5000 and elements['Dy_ppm'] > 500:
        minerals.append(('xenotime', 0.75))
    
    if elements['P_ppm'] > 50000 and elements['Ce_ppm'] > 2000:
        minerals.append(('apatite', 0.7))
    
    # Pathfinder mineralogy
    if elements['Fe_pct'] > 15 and elements['Ti_ppm'] > 5000:
        minerals.append(('magnetite', 0.6))
    
    if elements['Nb_ppm'] > 1000 and elements['Ta_ppm'] > 50:
        minerals.append(('pyrochlore', 0.65))
    
    if elements['Ba_ppm'] > 10000:
        minerals.append(('barite', 0.6))
    
    if elements['F_ppm'] > 10000 and elements['Ca_pct'] > 5:
        minerals.append(('fluorite', 0.7))
    
    # Lithium minerals
    if elements['Rb_ppm'] > 200 and elements['Cs_ppm'] > 5:
        if elements['Sn_ppm'] > 50:
            minerals.append(('lepidolite', 0.6))
        if elements['Al_pct'] > 10:
            minerals.append(('spodumene', 0.55))
    
    return sorted(minerals, key=lambda x: x[1], reverse=True)
```

## Thin Section Modal Analysis

```python
def analyze_thin_section(image_path, minerals_reference):
    """
    Semi-automated modal mineralogy from thin section photo
    """
    from sklearn.cluster import KMeans
    
    img = cv2.imread(image_path)
    img_lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    
    # Segment grains by color/texture
    pixels = img_lab.reshape(-1, 3)
    kmeans = KMeans(n_clusters=8, random_state=42, n_init=10)
    labels = kmeans.fit_predict(pixels)
    
    # Match clusters to mineral reference colors
    modal = {}
    for i, center in enumerate(kmeans.cluster_centers_):
        pct = np.sum(labels == i) / len(labels)
        best_match = match_to_reference(center, minerals_reference)
        modal[best_match] = modal.get(best_match, 0) + pct
    
    return {k: round(v * 100, 1) for k, v in modal.items()}
```

## Best Practices

1. **Photo standards:** Consistent lighting, scale bar, neutral background.
2. **Multiple angles:** Some minerals show different colors/cleavage on different faces.
3. **Hardness test:** Mohs scale — fingernail (2.5), copper penny (3.5), knife (5.5), glass (6), quartz (7).
4. **Streak test:** More reliable than surface color (hematite = red-brown streak).
5. **Magnet test:** Strong = magnetite, weak = pyrrhotite, none = most other minerals.
6. **UV fluorescence:** Scheelite (blue-white), fluorite (violet), autunite (green-yellow).
