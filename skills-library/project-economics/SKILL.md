---
name: project-economics
description: Economic evaluation of REE and critical mineral projects — NPV modeling, capex/opex estimation, basket pricing, sensitivity analysis, and feasibility study frameworks.
---

# Project Economics for REE and Critical Mineral Projects

## When to use

- You need to assess whether a discovered deposit is economically viable.
- You want to optimize cut-off grade based on prices and costs.
- You need to build a financial model for investors or JV partners.
- You want to run sensitivity analysis on key variables (price, recovery, capex).

## Key Economic Parameters

### Capital Expenditure (CAPEX)
| Item | % of Total | Notes |
|---|---|---|
| **Mining plant & equipment** | 25–35% | Lower for open pit, higher for underground |
| **Processing plant** | 30–45% | REE separation is CAPEX-intensive |
| **Infrastructure** | 10–20% | Roads, power, water, camp, port |
| **EPCM & Owner's costs** | 10–15% | Engineering, procurement, construction management |
| **Contingency** | 10–15% | Essential for REE (first-of-kind risk) |
| **Working capital** | 5–10% | Initial reagents, spare parts |

**Typical CAPEX ranges:**
- Small REE project (1–5 Mtpa): $200–500M
- Medium REE project (5–10 Mtpa): $500M–1.5B
- Large integrated REE mine-to-magnet: $1.5B–5B

### Operating Expenditure (OPEX)
| Cost Component | $/t ROM | $/kg REO | Notes |
|---|---|---|---|
| **Mining** | 8–25 | 2–8 | Open pit cheaper than underground |
| **Processing** | 30–80 | 10–40 | Leaching + SX expensive |
| **Reagents** | 10–30 | 3–15 | Acid, solvent, precipitants |
| **Energy** | 5–15 | 2–6 | Power-intensive separation |
| **Labor** | 5–15 | 2–5 | Skilled metallurgists needed |
| **Waste/tailings** | 3–8 | 1–3 | Radioactive waste = higher cost |
| **G&A** | 3–8 | 1–3 | Administration, royalties |
| **TOTAL OPEX** | 60–180 | 20–80 | Highly variable |

### REE Basket Price Calculation

```python
def calculate_basket_price(grades_dict, prices_dict):
    """
    Calculate weighted basket price based on deposit grade and market prices
    grades_dict: {element: grade_fraction}
    prices_dict: {element: price_per_kg}
    """
    total_revenue_per_tonne = 0
    breakdown = {}
    
    for element, grade_frac in grades_dict.items():
        if element in prices_dict:
            revenue = grade_frac * prices_dict[element] * 1000  # kg per tonne
            total_revenue_per_tonne += revenue
            breakdown[element] = revenue
    
    # Basket price = revenue per tonne / total REO kg per tonne
    total_reo_kg = sum(grades_dict.values()) * 1000
    basket_price = total_revenue_per_tonne / total_reo_kg if total_reo_kg > 0 else 0
    
    return {
        'basket_price_per_kg_reo': basket_price,
        'revenue_per_tonne_rom': total_revenue_per_tonne,
        'breakdown': breakdown
    }

# Example: Mountain Pass style (LREE dominant)
grades = {
    'La': 0.035, 'Ce': 0.055, 'Pr': 0.006, 'Nd': 0.022,
    'Sm': 0.003, 'Eu': 0.0006, 'Gd': 0.002, 'Tb': 0.0003,
    'Dy': 0.001, 'Ho': 0.0002, 'Er': 0.0005, 'Tm': 0.00008,
    'Yb': 0.0004, 'Lu': 0.00006, 'Y': 0.008
}

prices = {
    'La': 10, 'Ce': 12, 'Pr': 80, 'Nd': 85,
    'Sm': 25, 'Eu': 350, 'Gd': 120, 'Tb': 850,
    'Dy': 300, 'Ho': 200, 'Er': 50, 'Tm': 450,
    'Yb': 80, 'Lu': 550, 'Y': 60
}

result = calculate_basket_price(grades, prices)
print(f"Basket price: ${result['basket_price_per_kg_reo']:.2f}/kg REO")
```

## NPV Model

```python
import numpy as np
import pandas as pd

def ree_npv_model(
    mine_life_years,
    annual_production_mt,
    treo_grade_pct,
    metallurgical_recovery_pct,
    basket_price_per_kg,
    capex_millions,
    opex_per_tonne,
    discount_rate=0.10,
    inflation=0.025,
    royalty_rate=0.05,
    tax_rate=0.30,
    closure_cost_millions=50
):
    """
    Full NPV model for REE project
    """
    years = np.arange(0, mine_life_years + 1)
    
    # Production profile (ramp up then steady)
    production = np.ones(mine_life_years) * annual_production_mt
    production[0] *= 0.5  # Ramp-up year 1
    production[1] *= 0.75  # Ramp-up year 2
    
    # Revenue
    reo_kg_per_tonne = treo_grade_pct / 100 * 1000 * (metallurgical_recovery_pct / 100)
    revenue_per_tonne = reo_kg_per_tonne * basket_price_per_kg
    
    revenue = production * revenue_per_tonne * 1e6  # Convert to $
    
    # Costs
    opex = production * opex_per_tonne * 1e6
    royalty = revenue * royalty_rate
    
    # CAPEX schedule (front-loaded)
    capex_schedule = np.zeros(mine_life_years)
    capex_schedule[0] = capex_millions * 0.4 * 1e6
    capex_schedule[1] = capex_millions * 0.4 * 1e6
    capex_schedule[2] = capex_millions * 0.2 * 1e6
    
    # Closure cost (end of life)
    closure = np.zeros(mine_life_years)
    closure[-1] = closure_cost_millions * 1e6
    
    # Pre-tax cash flow
    ebitda = revenue - opex - royalty
    depreciation = (capex_millions * 1e6) / mine_life_years
    ebit = ebitda - depreciation
    tax = np.maximum(0, ebit * tax_rate)
    
    # After-tax cash flow
    cash_flow = ebitda - capex_schedule - tax - closure
    
    # NPV
    npv = np.sum(cash_flow / (1 + discount_rate) ** np.arange(1, mine_life_years + 1))
    npv -= capex_schedule[0]  # Year 0 CAPEX
    
    # IRR
    full_cf = np.concatenate([[-capex_schedule[0]], cash_flow[1:]])
    irr = np.irr(full_cf) if hasattr(np, 'irr') else None
    
    return {
        'npv_millions': npv / 1e6,
        'irr_pct': irr * 100 if irr else None,
        'payback_years': np.argmax(np.cumsum(cash_flow) > 0) + 1,
        'annual_cash_flows': cash_flow / 1e6,
        'revenue_profile': revenue / 1e6,
        'opex_profile': opex / 1e6
    }

# Example
result = ree_npv_model(
    mine_life_years=20,
    annual_production_mt=2.0,
    treo_grade_pct=3.5,
    metallurgical_recovery_pct=65,
    basket_price_per_kg=25,
    capex_millions=800,
    opex_per_tonne=80,
    discount_rate=0.10
)
print(f"NPV: ${result['npv_millions']:.1f}M")
print(f"IRR: {result['irr_pct']:.1f}%")
```

## Sensitivity Analysis

```python
def tornado_sensitivity(base_case, variables):
    """
    Tornado diagram sensitivity analysis
    variables: dict of {name: (low_value, high_value)}
    """
    sensitivities = []
    
    for var_name, (low, high) in variables.items():
        # Low case NPV
        low_params = base_case.copy()
        low_params[var_name] = low
        low_npv = ree_npv_model(**low_params)['npv_millions']
        
        # High case NPV
        high_params = base_case.copy()
        high_params[var_name] = high
        high_npv = ree_npv_model(**high_params)['npv_millions']
        
        sensitivities.append({
            'variable': var_name,
            'low_npv': low_npv,
            'high_npv': high_npv,
            'swing': abs(high_npv - low_npv)
        })
    
    # Sort by swing magnitude
    sensitivities.sort(key=lambda x: x['swing'], reverse=True)
    return sensitivities

# Run sensitivity
variables = {
    'basket_price_per_kg': (15, 40),
    'treo_grade_pct': (2.0, 5.0),
    'metallurgical_recovery_pct': (50, 80),
    'capex_millions': (600, 1200),
    'opex_per_tonne': (60, 120),
    'discount_rate': (0.08, 0.15)
}

base = {
    'mine_life_years': 20,
    'annual_production_mt': 2.0,
    'treo_grade_pct': 3.5,
    'metallurgical_recovery_pct': 65,
    'basket_price_per_kg': 25,
    'capex_millions': 800,
    'opex_per_tonne': 80
}

tornado = tornado_sensitivity(base, variables)
for s in tornado:
    print(f"{s['variable']}: ${s['low_npv']:.0f}M to ${s['high_npv']:.0f}M (swing: ${s['swing']:.0f}M)")
```

## Cut-off Grade Optimization

```python
def optimize_cutoff_grade(grade_tonnage_curve, opex_per_tonne, basket_price, recovery, discount_rate=0.10):
    """
    Find the cut-off grade that maximizes NPV
    grade_tonnage_curve: list of (grade, cumulative_tonnage) tuples
    """
    best_npv = -np.inf
    best_cutoff = 0
    
    for grade, tonnes in grade_tonnage_curve:
        if grade < 0.1:
            continue
        
        revenue_per_tonne = grade / 100 * 1000 * recovery / 100 * basket_price
        margin = revenue_per_tonne - opex_per_tonne
        
        if margin <= 0:
            continue
        
        # Simple NPV approximation
        annual_tonnage = min(tonnes / 15, 3e6)  # Assume 15-year mine, max 3 Mtpa
        mine_life = tonnes / annual_tonnage
        annual_cf = annual_tonnage * margin
        npv = annual_cf * ((1 - (1 + discount_rate)**(-mine_life)) / discount_rate)
        
        if npv > best_npv:
            best_npv = npv
            best_cutoff = grade
    
    return best_cutoff, best_npv
```

## Best Practices

1. **Basket price conservatism:** Use 3-year trailing average, not spot prices.
2. **Recovery penalties:** REE metallurgy is hard — use pilot plant data, not lab-scale.
3. **Contingency:** REE projects have high technical risk. Use 15–20% contingency, not 10%.
4. **Currency risk:** Most REE priced in USD; costs may be local currency.
5. **Royalty structures:** Some jurisdictions have sliding-scale royalties based on grade or price.
6. **Tax holidays:** Many countries offer tax incentives for critical minerals — model them.
7. **Offtake agreements:** Secure offtake before final investment decision (FID).
