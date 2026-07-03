---
name: regulatory-compliance
description: Regulatory frameworks for REE and critical mineral exploration — JORC 2012, NI 43-101, SAMREC, CRIRSCO alignment, environmental permits, radiation safety, and indigenous consultation requirements.
---

# Regulatory Compliance for REE Exploration

## When to use

- You need to ensure resource estimates meet reporting standards.
- You are preparing a technical report for investors or regulators.
- You need to understand environmental and radiation permitting requirements.
- You want to know indigenous consultation obligations.

## International Reporting Standards (CRIRSCO-aligned)

| Standard | Jurisdiction | Key Feature |
|---|---|---|
| **JORC 2012** | Australia / Asia / Africa | Most widely used; Competent Person (CP) requirement |
| **NI 43-101** | Canada / TSX | Strictest; Qualified Person (QP) must sign off |
| **SAMREC 2016** | South Africa | Similar to JORC; Social/ESG elements added |
| **PERC 2021** | Europe | Includes sustainability and ESG reporting |
| **SEC S-K 1300** | USA | New mining disclosure rules (2021) |

## JORC 2012 Essentials

### Competent Person (CP)
- Must be a Member or Fellow of a Recognized Professional Organization (RPO)
- Minimum 5 years relevant experience
- Must take responsibility for the specific section they sign
- Cannot be an employee of the company if also acting as independent reviewer (conflict of interest)

### Material Information
Anything that could influence investment decisions:
- Geology and mineralization style
- Exploration results (must not be presented as resource without QP/CP sign-off)
- Sampling methods and QA/QC
- Data verification
- Resource estimation methodology
- Economic studies (if applicable)

### Table 1 Checklist (JORC)
JORC Code requires disclosure against Table 1 categories:
1. **Sampling Techniques** — How samples were collected, cut, split
2. **Drilling Techniques** — Core diameter, recovery, orientation
3. **Sample Prep** — Crushing, splitting, pulverizing, assay lab
4. **Quality of Assay Data** — Standards, blanks, duplicates, lab QA
5. **Verification** — Independent checks, twinned holes
6. **Location** — Survey method, coordinate system, topography
7. **Data Spacing** — Sample spacing, compositing, orientation
8. **Orientation** — Relationship between mineralization and sampling
9. **Audit** — Internal or external audits of data quality
10. **Mineral Resource** — Estimation method, assumptions, classification
11. **Ore Reserve** — Modifying factors, mining method, metallurgy
12. **Exploration Results** — Not resources; must be clearly labeled

## NI 43-101 Key Differences

- **Qualified Person (QP)** — Similar to CP but must be independent for certain reports
- **Technical Report (Form 43-101F1)** — Required for disclosure of mineral resources/reserves
- **Consent** — QP must consent to use of their report
- **Escrow** — Early-stage exploration data can be held in escrow

## Resource Classification Criteria

### Geological Confidence
| Factor | Measured | Indicated | Inferred |
|---|---|---|---|
| **Geological continuity** | Confirmed by detailed mapping | Interpreted with reasonable confidence | Assumed or extrapolated |
| **Data spacing** | Close enough for mine planning | Suitable for mine planning with caution | Too sparse for economic evaluation |
| **Sampling** | Representative, unbiased | Representative with minor gaps | May not be representative |
| **QA/QC** | Rigorous, documented | Adequate | Limited or absent |

### JORC Modifying Factors (for Ore Reserve)
1. Mining method and parameters
2. Metallurgical recovery and process design
3. Infrastructure and logistics
4. Environmental and social impact
5. Legal and permitting
6. Marketing and sales
7. Capital and operating costs
8. Economic analysis (NPV, IRR)

## Environmental Permitting

### REE-Specific Environmental Issues
| Issue | Concern | Mitigation |
|---|---|---|
| **Radioactivity** | Th-232, U-238 in monazite/xenotime | Radiation management plan, waste characterization |
| **Acid drainage** | Sulfide minerals in some REE ores | Acid-base accounting, waste rock covers |
| **Tailings** | Fine-grained, often radioactive | Dry stacking, encapsulation, long-term monitoring |
| **Water use** | High water demand for processing | Recycling, zero-discharge design |
| **Reagents** | H₂SO₄, NaOH, organic solvents | Spill containment, neutralization |

### Typical Permits Required
1. **Exploration License** — Government mineral rights
2. **Environmental Impact Assessment (EIA)** — Required before mining
3. **Water Use Permit** — Abstraction and discharge
4. **Radiation License** — If ore > 200 Bq/g (varies by jurisdiction)
5. **Waste Management Permit** — Tailings and waste rock
6. **Land Use Agreement** — Private or communal land access
7. **Heritage Clearance** — Archaeological and cultural sites
8. **Biodiversity Offset** — If critical habitat affected

## Indigenous Consultation

### Free, Prior, and Informed Consent (FPIC)
- **Free** — No coercion, intimidation, or manipulation
- **Prior** — Consultation begins before exploration, not after discovery
- **Informed** — Full disclosure of impacts, benefits, risks
- **Consent** — Right to say no (in some jurisdictions)

### Best Practice
```python
def consultation_checklist():
    return {
        'initial_contact': False,
        'community_mapping': False,  # Map sacred sites, hunting grounds
        'benefit_sharing_agreement': False,
        'grievance_mechanism': False,
        'cultural_heritage_assessment': False,
        'employment_commitment': False,
        'environmental_monitoring_participation': False,
        'consent_documented': False
    }
```

## Radiation Safety

### Regulatory Thresholds (varies by country)
| Classification | Activity Concentration (Bq/g) | Regulatory Regime |
|---|---|---|
| Exempt | < 0.5–1.0 | None |
| NORM | 1.0–200 | Registration, basic controls |
| Radioactive Material | > 200 | Full licensing, dosimetry, transport rules |

### Radiation Management Plan Requirements
1. **Baseline survey** — Pre-exploration gamma dose rates
2. **Dosimetry** — Personal monitors for all workers
3. **Dose limits** — 20 mSv/year (occupational), 1 mSv/year (public)
4. **Dust control** — Respirable dust containing Th/U is the primary hazard
5. **Waste characterization** — All rock/soil with elevated radioactivity
6. **Transport** — UN classification if > exemption limits
7. **Emergency procedures** — Spill, loss of source, overexposure

## Report Templates

### JORC-compliant Resource Statement
```
The Mineral Resource estimate for the [Project Name] deposit is reported in accordance 
with the JORC Code (2012). The Competent Person is [Name], [Membership], who has 
[XX] years of experience in [relevant field].

The Measured Resource is [XX] Mt at [X.XX]% TREO, containing [XX,XXX] tonnes TREO.
The Indicated Resource is [XX] Mt at [X.XX]% TREO, containing [XX,XXX] tonnes TREO.
The Inferred Resource is [XX] Mt at [X.XX]% TREO, containing [XX,XXX] tonnes TREO.

[Cut-off grade, modifying factors, key assumptions, and QP statement follow.]
```

## Python: Automated Compliance Checker

```python
def check_jorc_compliance(report_text):
    """
    Automated checklist against JORC Table 1
    """
    required_sections = [
        'sampling techniques', 'drilling techniques', 'sample preparation',
        'quality of assay data', 'verification', 'location of data points',
        'data spacing', 'orientation', 'sample security', 'audits',
        'mineral resource estimation', 'classification'
    ]
    
    report_lower = report_text.lower()
    missing = []
    
    for section in required_sections:
        if section not in report_lower:
            missing.append(section)
    
    # Check for CP statement
    if 'competent person' not in report_lower:
        missing.append('Competent Person statement')
    
    # Check for materiality
    if 'material' not in report_lower or 'modifying factors' not in report_lower:
        missing.append('Materiality / Modifying factors')
    
    return {
        'compliant': len(missing) == 0,
        'missing_sections': missing,
        'score': (len(required_sections) - len(missing)) / len(required_sections) * 100
    }
```

## Best Practices

1. **Document everything:** If it's not documented, it didn't happen for regulatory purposes.
2. **Chain of custody:** Sample tracking from field to lab to database.
3. **Independent review:** Have a second CP/QP review all estimates.
4. **Conservative classification:** When in doubt, downgrade (Measured → Indicated → Inferred).
5. **Regular updates:** JORC requires annual review if new data changes the estimate.
6. **ESG integration:** Modern standards (PERC, SAMREC) require sustainability reporting.
