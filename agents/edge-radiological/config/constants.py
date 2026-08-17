"""
CITED PHYSICAL CONSTANTS — Edge Radiological Assessment Platform
================================================================
RULE 1 compliance: every literal number here is a published physical constant
with an explicit source citation. NOTHING in this file is fabricated,
calibrated to a single narrow study, or a plausible-looking guess.

If a value cannot be cited, it does not belong in this file.
"""

from __future__ import annotations

# ──────────────────────────────────────────────────────────────────────────
# ACTIVITY-CONCENTRATION CONVERSIONS
# Convert measured elemental concentrations (Tellus soil geochemistry) to
# specific activity in Bq/kg, assuming secular equilibrium in the decay series.
# Source: IAEA TECDOC-1363, "Guidelines for radioelement mapping using gamma
# ray spectrometry data" (2003), Table conversion factors.
# ──────────────────────────────────────────────────────────────────────────
BQKG_PER_PPM_EU = 12.35      # 1 ppm eU  -> 12.35 Bq/kg Ra-226  [IAEA TECDOC-1363]
BQKG_PER_PPM_ETH = 4.06      # 1 ppm eTh -> 4.06  Bq/kg Th-232  [IAEA TECDOC-1363]
BQKG_PER_PCT_K = 313.0       # 1 % K     -> 313   Bq/kg K-40    [IAEA TECDOC-1363]

# Elemental potassium fraction of potassium oxide (K2O), by mass.
# Tellus XRFS reports K as K2O_PCT; convert to elemental K% before the K-40 step.
# K = K2O x (2 * M_K) / (2 * M_K + M_O)
# M_K = 39.0983 g/mol, M_O = 15.999 g/mol  [IUPAC 2021 standard atomic weights]
# => 2*39.0983 / (2*39.0983 + 15.999) = 0.8302
K2O_TO_K_MASS_FRACTION = 0.8302   # [IUPAC 2021 standard atomic weights]

# ──────────────────────────────────────────────────────────────────────────
# EXTERNAL GAMMA DOSE-RATE COEFFICIENTS  (nGy/h per Bq/kg)
# Absorbed dose rate in air 1 m above ground for uniformly distributed activity.
# Source: UNSCEAR 2008 Report, Annex B, Table 3 (dose coefficients originally
# from Saito & Jacob 1995 / UNSCEAR 2000 Annex B).
# ──────────────────────────────────────────────────────────────────────────
GAMMA_COEFF_RA226 = 0.462    # nGy/h per Bq/kg Ra-226  [UNSCEAR 2008, Annex B, Table 3]
GAMMA_COEFF_TH232 = 0.604    # nGy/h per Bq/kg Th-232  [UNSCEAR 2008, Annex B, Table 3]
GAMMA_COEFF_K40 = 0.0417     # nGy/h per Bq/kg K-40    [UNSCEAR 2008, Annex B, Table 3]

# ──────────────────────────────────────────────────────────────────────────
# ANNUAL EFFECTIVE DOSE FROM EXTERNAL GAMMA
# E (mSv/yr) = D(nGy/h) x hours/yr x occupancy x conversion(Sv/Gy) x 1e-6
# Source: UNSCEAR 2008 Report, Annex B.
# ──────────────────────────────────────────────────────────────────────────
HOURS_PER_YEAR = 8760.0                 # 365 x 24  [definition]
SV_PER_GY_GAMMA = 0.7                    # effective/absorbed dose conversion, adults
#                                          [UNSCEAR 2008, Annex B]
NGY_TO_MSV = 1.0e-6                      # 1 nGy = 1e-6 mGy; 1 mGy air ~ conversion [SI]
# UNSCEAR default indoor occupancy fraction (people spend ~80% of time indoors).
INDOOR_OCCUPANCY_FRACTION = 0.8          # [UNSCEAR 2008, Annex B]
OUTDOOR_OCCUPANCY_FRACTION = 0.2         # [UNSCEAR 2008, Annex B]

# ──────────────────────────────────────────────────────────────────────────
# SOIL GAS RADON — PORE-SPACE CONCENTRATION MODEL
# C_pore (Bq/m3) = A_Ra226 (Bq/kg) x rho_grain (kg/m3) x epsilon x (1-n)/n
# where epsilon = radon emanation coefficient, n = porosity.
# Source of formula: Nazaroff (1992) "Radon transport from soil to air",
# Reviews of Geophysics 30(2), 137-160; also IAEA (2013) "Measurement and
# Calculation of Radon Releases from NORM Residues", Technical Reports Series 474.
# ──────────────────────────────────────────────────────────────────────────
GRAIN_DENSITY_KG_M3 = 2650.0            # quartz/typical mineral grain density
#                                          [Nazaroff 1992; standard soil physics]
# Emanation coefficient range for soils (fraction of radon escaping grains).
EMANATION_COEFF_MIN = 0.10              # [UNSCEAR 2000, Annex B; Nazaroff 1992]
EMANATION_COEFF_MAX = 0.30              # [UNSCEAR 2000, Annex B; Nazaroff 1992]
# Total porosity range for typical soils (dimensionless void fraction).
POROSITY_MIN = 0.25                    # [Nazaroff 1992; soil physics texts]
POROSITY_MAX = 0.45                    # [Nazaroff 1992; soil physics texts]

# ──────────────────────────────────────────────────────────────────────────
# IRELAND PUBLISHED REGULATORY REFERENCE LEVELS (public facts, not EPA map data)
# Source: S.I. No. 30 of 2019, Radiological Protection Act 1991 (Ionising
# Radiation) Regulations 2019.
# ──────────────────────────────────────────────────────────────────────────
REFERENCE_LEVEL_HOME_BQ_M3 = 200        # National Reference Level, homes   [S.I. 30/2019]
REFERENCE_LEVEL_WORKPLACE_BQ_M3 = 300   # Reference Level, workplaces       [S.I. 30/2019]
HIGH_RADON_AREA_THRESHOLD_PCT = 10      # >10% of homes predicted > 200 Bq/m3
#                                          defines a High Radon Area          [S.I. 30/2019]

# ──────────────────────────────────────────────────────────────────────────
# THORON / CRUSTAL GEOCHEMISTRY REFERENCE
# ──────────────────────────────────────────────────────────────────────────
CRUSTAL_TH_U_RATIO = 3.8                # average continental crust Th/U mass ratio
#                                          [Taylor & McLennan 1985, "The Continental
#                                           Crust: its Composition and Evolution"]

# ──────────────────────────────────────────────────────────────────────────
# UNSCEAR WORLD-AVERAGE SOIL ACTIVITIES (for contextual comparison only,
# never substituted into a user's result).
# Source: UNSCEAR 2000 Report, Annex B, Table 1 (population-weighted world means).
# ──────────────────────────────────────────────────────────────────────────
WORLD_AVG_RA226_BQKG = 32.0             # [UNSCEAR 2000, Annex B, Table 1]
WORLD_AVG_TH232_BQKG = 45.0             # [UNSCEAR 2000, Annex B, Table 1]
WORLD_AVG_K40_BQKG = 420.0              # [UNSCEAR 2000, Annex B, Table 1]
WORLD_AVG_OUTDOOR_GAMMA_NGY_H = 59.0    # world-average outdoor absorbed dose rate
#                                          [UNSCEAR 2000, Annex B]

# External outbound reference (never embeds EPA data — Rule 8 / Section 7.7).
EPA_RADON_MAP_URL = "https://www.epa.ie/environment-and-you/radon/radon-map/"

# Data attribution strings (Section 3 — CC-BY-4.0 requires attribution).
ATTRIBUTION = {
    "tellus": "Geological Survey Ireland & Geological Survey of Northern Ireland "
              "(Tellus airborne/geochemical survey), CC-BY-4.0",
    "gsi_permeability": "Geological Survey Ireland, Subsoil Permeability, CC-BY-4.0",
    "gsi_faults": "Geological Survey Ireland, Bedrock Geology 1:100k geological "
                  "lines (faults), CC-BY-4.0",
    "basemap": "Esri World Imagery (map display only, not a scientific input)",
}
