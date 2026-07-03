---
name: hydro-geochem
description: Hydrogeochemistry and water sampling for REE exploration — water chemistry analysis, pathfinder detection in water, isotope geochemistry, and environmental baseline studies.
---

# Hydrogeochemistry for REE Exploration

## When to use

- You want to detect REE pathfinders in surface water or groundwater.
- You need to establish environmental baseline chemistry before exploration.
- You want to use isotopes (O, H, Sr, Nd) to trace fluid sources.
- You're assessing acid mine drainage or leaching potential.

## Water Sampling Protocol

### Field Parameters (In-Situ)
| Parameter | Instrument | Notes |
|---|---|---|
| pH | Portable pH meter | Calibrate daily |
| EC (electrical conductivity) | EC meter | μS/cm, correlates with TDS |
| Temperature | Thermometer | °C, affects solubility |
| Eh / ORP | ORP meter | Redox conditions |
| Dissolved O₂ | DO meter | Critical for redox-sensitive REE |
| Turbidity | Turbidimeter | Filter if > 5 NTU |

### Sample Collection
1. **Rinse bottle 3×** with sample water before filling
2. **0.45 μm filter** on-site for dissolved metals
3. **Acidify to pH < 2** with HNO₃ (ultra-pure) for metal analysis
4. **Refrigerate** at 4°C, analyze within 6 months
5. **Duplicate** 1 in 20 samples
6. **Field blank** 1 per batch (deionized water)

## REE in Natural Waters

### Concentration Ranges
| Water Type | TREO (ppb) | Key Features |
|---|---|---|
| Seawater | 1–5 | Strong LREE enrichment, negative Ce anomaly |
| River water | 0.1–50 | Variable, reflects catchment lithology |
| Groundwater | 0.01–1000 | Can be very high in REE-rich aquifers |
| Acid mine drainage | 100–10,000 | Extremely high, LREE >> HREE |
| Carbonatite springs | 10–500 | Anomalous Nb, Sr, Ba, F, P |

### Normalized Patterns
```python
def plot_water_ree_pattern(water_data, normalization='chondrite'):
    """
    Plot REE pattern for water sample
    """
    import matplotlib.pyplot as plt
    
    ree_elements = ['La', 'Ce', 'Pr', 'Nd', 'Sm', 'Eu', 'Gd', 
                    'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu']
    
    chondrite = [0.237, 0.612, 0.095, 0.467, 0.153, 0.058, 0.205,
                 0.037, 0.254, 0.057, 0.166, 0.026, 0.165, 0.025]
    
    water_values = [water_data.get(e, np.nan) for e in ree_elements]
    normalized = np.array(water_values) / np.array(chondrite)
    
    plt.figure(figsize=(10, 6))
    plt.plot(ree_elements, normalized, 'o-', linewidth=2)
    plt.axhline(y=1, color='gray', linestyle='--')
    plt.ylabel(f'{normalization}-normalized REE')
    plt.yscale('log')
    plt.title('Water REE Pattern')
    plt.grid(True, alpha=0.3)
    return plt.gcf()
```

## Pathfinder Elements in Water

| Target | Primary Pathfinders | Secondary | Notes |
|---|---|---|---|
| Carbonatite | F⁻, Sr²⁺, Ba²⁺, Nb, P | REE, Th | High pH (8–10), high HCO₃⁻ |
| IAC clay | Al³⁺, SO₄²⁻, pH 4–6 | Fe, Mn | Acidic groundwater from weathering |
| Hydrothermal HREE | F⁻, As, Sb, W | Sn, Li, Cs | Near-neutral pH, high F |
| LCT pegmatite | Li, Cs, Rb, B | Be, Nb, Ta | Often in thermal springs |
| U-REE | U, Ra, Rn | Mo, Se | Redox front control |

## Isotope Geochemistry

### Strontium Isotopes (⁸⁷Sr/⁸⁶Sr)
- **Carbonatite:** 0.703–0.706 (mantle-derived)
- **Granite:** 0.707–0.720 (crustal)
- **Seawater:** 0.709 (modern)
- **Application:** Distinguish carbonatite-derived fluids from crustal groundwater

### Neodymium Isotopes (εNd)
- **Carbonatite:** εNd = 0 to +5 (depleted mantle signature)
- **Crustal rocks:** εNd = -5 to -20
- **Application:** Provenance of REE in sediments/placers

### Oxygen-Hydrogen Isotopes (δ¹⁸O, δD)
- **Meteoric water line:** δD = 8 × δ¹⁸O + 10
- **Magmatic water:** δ¹⁸O = +6 to +10, δD = -40 to -80
- **Application:** Distinguish magmatic vs. meteoric fluid sources

## Environmental Baseline

```python
def calculate_baselines(water_chemistry_df, elements):
    """
    Calculate background and anomaly thresholds for water chemistry
    """
    results = {}
    
    for elem in elements:
        data = water_chemistry_df[elem].dropna()
        
        # Background: median + 2MAD
        median = data.median()
        mad = np.median(np.abs(data - median))
        threshold = median + 2 * 1.4826 * mad  # Consistent MAD estimator
        
        results[elem] = {
            'n_samples': len(data),
            'mean': data.mean(),
            'median': median,
            'std': data.std(),
            'min': data.min(),
            'max': data.max(),
            'threshold': threshold,
            'anomaly_count': int(np.sum(data > threshold))
        }
    
    return pd.DataFrame(results).T
```

## AMD Potential Assessment

```python
def calculate_np_ap(sulfide_pct, carbonate_pct, silicate_pct):
    """
    Acid Base Accounting for REE deposits
    NP = Neutralization Potential (from carbonates)
    AP = Acid Potential (from sulfides)
    """
    # Simplified: assume all S is pyrite
    ap = sulfide_pct * 31.25  # kg H2SO4/t
    
    # NP from calcite/dolomite
    np = carbonate_pct * 10  # Rough approximation
    
    npr = np / ap if ap > 0 else float('inf')
    
    if npr > 3:
        risk = "Low"
    elif npr > 1:
        risk = "Moderate"
    elif npr > 0:
        risk = "High"
    else:
        risk = "Very High"
    
    return {'NP': np, 'AP': ap, 'NPR': npr, 'risk': risk}
```

## Best Practices

1. **Sample before drilling:** Establish true baseline before any disturbance.
2. **Seasonal sampling:** Wet season vs. dry season can show 10× concentration differences.
3. **Filter immediately:** REE can precipitate on suspended particles.
4. **Record everything:** Weather, flow rate, upstream geology, nearby land use.
5. **Chain of custody:** Track samples from field to lab with signed forms.
