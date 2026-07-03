---
name: hydro-geochem
description: Hydrogeochemistry for REE and critical mineral exploration — water sampling, pathfinder elements in groundwater, isotope geochemistry, and environmental baseline studies.
---

# Hydrogeochemistry for REE Exploration

## When to use

- You need to sample groundwater, streams, or springs for geochemical pathfinders.
- You want to understand REE mobility in the weathering environment.
- You need environmental baseline data before exploration begins.
- You want to use isotopes (O, H, Sr, Nd) to trace fluid sources.

## Water Sampling for Exploration

### Parameters to Measure
| Parameter | Field Method | Lab Method | Exploration Significance |
|---|---|---|---|
| **pH** | pH meter | — | Controls REE mobility (low pH = mobile) |
| **EC/TDS** | Conductivity meter | — | Total dissolved solids proxy |
| **Eh** | ORP meter | — | Redox state (affects Ce) |
| **Alkalinity** | Titrate HCl | — | Carbonate system |
| **Major ions** | — | IC, ICP-OES | Water type classification |
| **REE + trace** | — | ICP-MS | Direct pathfinder detection |
| **U, Th** | — | ICP-MS | Radioactive pathfinders |
| **Stable isotopes** | — | IRMS | Fluid source tracing |

### REE Mobility in Water
- **Acidic waters (pH < 5):** All REE mobile, LREE > HREE
- **Neutral waters (pH 6–7):** REE immobile, adsorbed to Fe-Mn oxyhydroxides
- **Carbonate-rich waters:** Ce anomaly develops (Ce⁴⁺ insoluble)
- **Saline waters:** REE complexed with Cl⁻, SO₄²⁻

### Sampling Protocol
```python
WATER_SAMPLING_PROTOCOL = {
    'preparation': [
        'Rinse bottle 3x with sample water before filling',
        'Wear nitrile gloves — skin oils contaminate REE analysis',
        'Record GPS, time, weather, flow rate, color, odor'
    ],
    'filtration': {
        'unfiltered': 'Acidify with HNO₃ to pH < 2 for total metals (ICP-MS)',
        '0.45_um': 'Filter for dissolved metals',
        '0.22_um': 'Filter for truly dissolved (colloids removed)'
    },
    'acidification': {
        'total_ree': 'HNO₃ to pH < 2 immediately after collection',
        'cations': 'HNO₃ to pH < 2',
        'anions': 'No acidification — analyze within 48 hours',
        'isotopes': 'No acidification — fill completely, no headspace'
    },
    'preservation': {
        'temperature': 'Cool to 4°C immediately',
        'dark': 'Store in dark to prevent algal growth',
        'time_to_lab': '< 6 months for total metals, < 48 hours for anions'
    }
}
```

## Stream Sediment vs. Water Geochemistry

| Method | Best For | Detection Range | Seasonal Variation |
|---|---|---|---|
| **Stream sediment** | REE pathfinders in heavy minerals | ppm–% | Low |
| **Stream water (total)** | Mobile REE, major ions | ppb–ppm | High (flow-dependent) |
| **Stream water (filtered)** | Truly dissolved REE | ppb | Very high |
| **Groundwater** | Deep-seated signatures | ppb–ppm | Low |

## Isotope Geochemistry

### Strontium-Neodymium Isotopes
```
⁸⁷Sr/⁸⁶Sr and εNd can fingerprint:
- Carbonatite fluids (low ⁸⁷Sr/⁸⁶Sr, positive εNd)
- Crustal fluids (high ⁸⁷Sr/⁸⁶Sr, negative εNd)
- Seawater (⁸⁷Sr/⁸⁶Sr ~ 0.709, time-dependent)
```

### Oxygen-Hydrogen Isotopes
```
δ¹⁸O vs. δD plot:
- Meteoric water line (MWL): δD = 8 × δ¹⁸O + 10
- Magmatic fluids: δ¹⁸O = 6–10‰, δD = -40 to -80‰
- Metamorphic fluids: δ¹⁸O = 8–15‰
- Evolved meteoric: Shifted right of MWL
```

## Python: Water Chemistry Analysis

```python
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

def analyze_water_chemistry(water_df):
    """
    Analyze water geochemistry for exploration signals
    """
    results = {}
    
    # 1. Water type (Piper diagram data)
    water_df['Ca_meq'] = water_df['Ca_mgL'] / 20.04
    water_df['Mg_meq'] = water_df['Mg_mgL'] / 12.15
    water_df['Na_meq'] = water_df['Na_mgL'] / 22.99
    water_df['K_meq'] = water_df['K_mgL'] / 39.10
    water_df['HCO3_meq'] = water_df['HCO3_mgL'] / 61.02
    water_df['SO4_meq'] = water_df['SO4_mgL'] / 48.03
    water_df['Cl_meq'] = water_df['Cl_mgL'] / 35.45
    
    cation_sum = water_df['Ca_meq'] + water_df['Mg_meq'] + water_df['Na_meq'] + water_df['K_meq']
    anion_sum = water_df['HCO3_meq'] + water_df['SO4_meq'] + water_df['Cl_meq']
    
    water_df['Ca_pct'] = water_df['Ca_meq'] / cation_sum * 100
    water_df['Mg_pct'] = water_df['Mg_meq'] / cation_sum * 100
    water_df['NaK_pct'] = (water_df['Na_meq'] + water_df['K_meq']) / cation_sum * 100
    
    # 2. REE patterns in water
    ree_elements = ['La', 'Ce', 'Pr', 'Nd', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu']
    
    # Shale-normalized (PAAS)
    paas = {'La': 38.2, 'Ce': 79.6, 'Pr': 8.83, 'Nd': 33.9, 'Sm': 5.55, 
            'Eu': 1.08, 'Gd': 4.66, 'Tb': 0.774, 'Dy': 4.68, 'Ho': 0.991,
            'Er': 2.85, 'Tm': 0.405, 'Yb': 2.82, 'Lu': 0.433}
    
    for elem in ree_elements:
        water_df[f'{elem}_sn'] = water_df[f'{elem}_ugL'] / paas[elem]
    
    # 3. Anomaly detection
    water_df['has_ree_anomaly'] = water_df[['La_ugL', 'Ce_ugL', 'Nd_ugL']].max(axis=1) > 1.0
    
    # 4. Correlation with known mineralization
    # (Requires training data)
    
    return water_df

def plot_water_ree_pattern(sample, title="Water REE Pattern"):
    """Plot shale-normalized REE pattern for water sample"""
    ree_elements = ['La', 'Ce', 'Pr', 'Nd', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu']
    values = [sample[f'{e}_sn'] for e in ree_elements]
    
    plt.figure(figsize=(10, 6))
    plt.plot(range(len(ree_elements)), values, 'o-', linewidth=2)
    plt.xticks(range(len(ree_elements)), ree_elements)
    plt.ylabel('PAAS-normalized')
    plt.title(title)
    plt.yscale('log')
    plt.grid(True, alpha=0.3)
    plt.axhline(y=1, color='r', linestyle='--', alpha=0.5)
    plt.show()
```

## Environmental Baseline

```python
ENVIRONMENTAL_BASELINE = {
    'water_quality': {
        'sampling_frequency': 'quarterly',
        'parameters': ['pH', 'EC', 'TDS', 'major_ions', 'trace_metals', 'REE'],
        'reference_sites': 'upgradient of any disturbance',
        'seasonal_coverage': 'wet and dry season'
    },
    'radiation': {
        'gamma_dose_rate': 'continuous monitoring or quarterly surveys',
        'radon': 'indoor and outdoor air',
        'water': 'gross_alpha, gross_beta, U, Th'
    },
    'biology': {
        'aquatic': 'macroinvertebrate community (sensitive to metals)',
        'vegetation': 'species composition, heavy metal uptake'
    },
    'socioeconomic': {
        'land_use': 'current farming, grazing, fishing',
        'water_use': 'domestic, irrigation, livestock'
    }
}
```

## Best Practices

1. **Sample upstream first:** Always collect baseline samples before any ground disturbance.
2. **Duplicate everything:** 10% field duplicates, 10% lab duplicates for water.
3. **Blank control:** Equipment blanks to check for contamination.
4. **Flow measurement:** Stream flow affects concentration — always measure.
5. **Seasonal monitoring:** Water chemistry varies dramatically between wet and dry seasons.
6. **Colloids matter:** A significant fraction of "dissolved" REE may be colloidal. Filter carefully.
