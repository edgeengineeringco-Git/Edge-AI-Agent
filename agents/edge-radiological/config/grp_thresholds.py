"""
GEOGENIC RADON POTENTIAL (GRP) THRESHOLDS & WEIGHTS
===================================================
Section 4.2 / Rule 6 compliance:

  - The PRIMARY output of the GRP model is an ORDINAL category: Low / Medium / High.
  - The category is derived from a transparent SOURCE-term + TRANSPORT-term
    combination, NOT from any single country/terrain-specific regression.
  - All thresholds and weights live HERE (adjustable), never buried in the
    calculation logic.
  - The internal numeric "score" is a documented weighted combination of named
    sub-scores; it is NOT presented as an independently validated GRP index.

Method rationale
----------------
Source term  = normalised Ra-226 activity (radon generation potential).
Transport term = soil permeability + fault proximity (how readily generated
                 radon migrates toward the surface / a future building).
Both terms are on a 0..1 scale; the combined score is a named weighted sum.

References for the qualitative structure (source x transport controls radon
potential): Nazaroff (1992) Reviews of Geophysics; Neznal et al. (2004)
"The new method for assessing the radon risk of building sites"; IAEA (2013)
Technical Reports Series 474. Thresholds below are project decision boundaries
(operational, adjustable) — NOT fabricated physical measurements.
"""

from __future__ import annotations

# ── Named weights for the source + transport combination (must sum to 1.0) ──
# Radon generation is meaningless without a transport path, and vice-versa,
# so both are weighted; source is weighted slightly higher because without
# radium there is no radon regardless of permeability.
WEIGHTS = {
    "source": 0.55,      # normalised Ra-226 activity
    "transport": 0.45,   # permeability + fault proximity
}

# ── Source-term normalisation ──
# Ra-226 activity (Bq/kg) mapped to 0..1. Anchored to UNSCEAR world-average
# soil Ra-226 (~32 Bq/kg) as the midpoint reference; values well above the
# world average approach 1.0. This is a normalisation choice, documented and
# adjustable — not a physical constant.
SOURCE_REF_LOW_BQKG = 15.0     # at/below this, source sub-score ~ 0.1
SOURCE_REF_HIGH_BQKG = 90.0    # at/above this, source sub-score ~ 1.0

# ── Transport sub-weights (permeability vs fault proximity) ──
TRANSPORT_WEIGHTS = {
    "permeability": 0.70,
    "fault_proximity": 0.30,
}

# ── GSI subsoil permeability rank -> transport sub-score (0..1) ──
# GSI Subsoil Permeability layer reports ordinal classes (Low/Moderate/High).
# We map those ordinal classes to a 0..1 transport contribution. If the layer
# returns no class at the point, transport is marked UNAVAILABLE (never
# defaulted to "moderate" — Section 4.2 explicit rule).
PERMEABILITY_RANK_SCORE = {
    "H": 1.0,    # High permeability -> strong radon transport
    "M": 0.6,    # Moderate
    "L": 0.25,   # Low permeability -> weak transport
    "X": 0.6,    # "Mixed/variable" GSI class -> treat as moderate-high
}

# ── Fault-proximity sub-score ──
# Faults act as preferential migration pathways. Closer -> higher sub-score.
# Exponential decay with distance; decay length is an adjustable operational
# parameter, not a fabricated measurement.
FAULT_DECAY_LENGTH_M = 3000.0   # e-folding distance for fault influence (m)
FAULT_MAX_CONSIDERED_M = 15000.0

# ── Category cut points on the combined 0..1 score ──
# Ordinal boundaries (adjustable). These define the Low/Medium/High output.
CATEGORY_CUTS = {
    "low_max": 0.33,     # score <= 0.33 -> Low
    "medium_max": 0.66,  # 0.33 < score <= 0.66 -> Medium; > 0.66 -> High
}


def category_from_score(score: float) -> str:
    """Map a 0..1 combined score to the ordinal GRP category."""
    if score <= CATEGORY_CUTS["low_max"]:
        return "Low"
    if score <= CATEGORY_CUTS["medium_max"]:
        return "Medium"
    return "High"
