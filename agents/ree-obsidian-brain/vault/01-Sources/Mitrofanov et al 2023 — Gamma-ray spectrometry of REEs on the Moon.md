---
title: "On gamma-ray spectrometry of rare earth elements on the moon: Reference data from proton accelerator experiment"
date_created: 2026-07-30
date_modified: 2026-07-30
tags: [source, paper, gamma-ray, REE, moon, lunar, spectrometry, GCR, HPGe, JINR]
doi: "10.1016/j.actaastro.2023.04.018"
authors: ["Mitrofanov, I.", "Golovin, D.", "Litvak, M.", "Nikiforov, S.", "Sanin, A.", "Anikin, A.", "Kozyrev, A.", "Mokrousov, M.", "Shvetsov, V.", "Timoshenko, G.", "Pavlik, E."]
journal: "Acta Astronautica"
volume: 209
pages: "21-30"
year: 2023
status: growing
attachment: "attachments/Ru-gamma-moon.pdf"
---

# On gamma-ray spectrometry of rare earth elements on the moon: Reference data from proton accelerator experiment

## Metadata
- **Authors**: Mitrofanov, I., Golovin, D., Litvak, M., Nikiforov, S., Sanin, A., Anikin, A., Kozyrev, A., Mokrousov, M., Shvetsov, V., Timoshenko, G., Pavlik, E.
- **Journal**: Acta Astronautica 209 (2023) 21–30
- **Year**: 2023
- **DOI**: [10.1016/j.actaastro.2023.04.018](https://doi.org/10.1016/j.actaastro.2023.04.018)
- **PDF**: [[Ru-gamma-moon.pdf]] (in `attachments/`)

## Abstract

Laboratory experiment at the Joint Institute for Nuclear Research (JINR) using a prototype planetary gamma-ray spectrometer (GRS) with a High Purity Germanium (HPGe) detector and a proton detector (PD) in coincidence mode. 11 REE samples were irradiated with 170 MeV protons to identify characteristic gamma-ray lines for lunar surface REE detection via Galactic Cosmic Ray (GCR) bombardment.

## Key Findings

> [!important] 45 significant gamma-ray lines were found for 11 tested REE samples

| Metric | Value |
|--------|-------|
| Total gamma-ray lines found | 45 |
| Lines already in existing catalog | 7 |
| **Unique lines** (single REE only) | **18** |
| Shared lines (multiple REEs) | 27 |
| Joint groups formed | 10 |
| Prompt fraction range | 10–50% |

- **18 unique gamma-ray lines** detected for individual REEs only — these are the most valuable for unambiguous identification
- **27 shared lines** combined into **10 joint groups** (some groups span 4 REEs)
- Some gamma-ray lines have prompt fraction approaching **50%**, others as low as **10–15%**
- Cerium gamma-ray line at **553 keV** detectable after **1.6 hours** of signal accumulation on lunar surface (with 10× effective area)

## Methodology

- **Facility**: Joint Institute for Nuclear Research (JINR), Dubna, Russia
- **Proton beam energy**: 171.5 ± 8.6 MeV
- **Detector**: HPGe (ORTEC GEM30185, 30% efficiency at 1333 keV)
- **Method**: Cosmic Gamma-Ray Spectrometry with Tagged Charged Particles (CGS-TCP)
  - Integrated spectra (all detected photons)
  - Tagged spectra (photons synchronized with proton detection)
  - Coincidence time window: ~tens of nanoseconds
- **Irradiation time**: ~2 hours per sample

## Tested REEs

11 of 17 REEs were tested:

| Element | Oxide Used | Mass (g) | Supply Risk | Tested? |
|---------|-----------|----------|-------------|---------|
| La | La₂O₃ | 236.0 | High | ✅ |
| Ce | CeO | 259.1 | High | ✅ |
| Pr | Pr₆O₁₁ | 177.6 | High | ✅ |
| Nd | Nd₂O₃ | 151.2 | High | ✅ |
| Pm | — | — | — | ❌ (no stable isotopes) |
| Sm | — | — | Low | ❌ (low supply risk) |
| Eu | Eu₂O₃ | 134.7 | Very high | ✅ |
| Gd | Gd₂O₃ | 252.0 | Low | ✅ |
| Tb | — | — | High | ❌ (too expensive) |
| Dy | Dy₂O₃ | 309.1 | High | ✅ |
| Ho | — | — | — | ❌ (not available) |
| Er | Er₂O₃ | 378.2 | Medium | ✅ |
| Tm | Tm₂O₃ | 327.1 | Medium | ✅ |
| Yb | Yb₂O₃ | 292.8 | Medium | ✅ |
| Lu | — | — | — | ❌ (too expensive) |
| Y | Y₂O₃ | 181.8 | Very high | ✅ |
| Sc | — | — | — | ❌ (too expensive) |

## Lunar Context

- Moon has two terrain types: **highlands** (Ca-Al rich, feldspar) and **maria** (Fe-Ti rich, pyroxene)
- Three geological provinces: **PKT** (Procellarum KREEP Terrane), **FHT** (Feldspathic Highlands Terrane), **SPAT** (South Pole-Aitken Terrane)
- **KREEP** regions: rich in **K** (Potassium), **REE** (Rare Earth Elements), and **P** (Phosphorus)
- Lunar surface covered by regolith — only gamma-ray sensing can detect shallow subsurface REEs
- Orbital gamma-ray (Lunar Prospector) has poor spatial resolution (~100s of km)
- Surface-level mobile platform GRS needed for local REE spot detection

## Relevance to EDGE Exploration

This paper is directly relevant to the [[edge-kuth-portal|K/U/Th Portal]] pipeline:
- Same physics: gamma-ray spectrometry for element identification
- Same approach: K, U, Th as pathfinders for REE-enriched zones
- The CGS-TCP method could improve signal-to-noise in field surveys
- Reference data for 11 REEs provides calibration lines for spectral interpretation

## Atomic Notes Extracted

- [[Gamma-Ray Spectrometry of REEs]]
- [[CGS-TCP Method]]
- [[KREEP Terrane]]
- [[Lunar REE Resources]]
- [[Cerium]] — 553 keV gamma-ray line for Ce detection
- [[Lanthanum]] — tested, La₂O₃ sample
- [[Europium]] — tested, very high supply risk
- [[Yttrium]] — tested, very high supply risk

## Related

- [[MOC — REE Master Index]]
- [[MOC — Sources Index]]
- [[03-Deposits/Carbonatite Deposits]]
- [[08-Concepts/Bastnäsite]]
- [[08-Concepts/Monazite]]
- [[08-Concepts/Xenotime]]

## Notes

This is a foundational reference for lunar REE gamma-ray spectrometry. The 45 identified gamma-ray lines and the CGS-TCP coincidence method provide both reference data and a potential improvement to terrestrial REE exploration using GCR-induced gamma rays. The paper bridges space science and resource exploration — directly relevant to EDGE's K/U/Th portal and gamma-ray survey capabilities.
