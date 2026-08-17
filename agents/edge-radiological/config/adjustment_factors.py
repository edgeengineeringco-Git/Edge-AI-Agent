"""
ANTHROPOGENIC & MATERIAL ADJUSTMENT FACTORS
===========================================
Section 4.3 / 4.4 compliance.

Two distinct tables live here:

1. RADON MULTIPLIER RANGES (Section 4.4) — how a building's construction and
   ventilation modify the indoor radon a given ground would produce, relative
   to a reference floor/ventilation case. Each multiplier is a RANGE, each cites
   its justification. "Unknown" answers WIDEN the range (Rule 7), never default
   to a single assumed value.

2. BUILDING-MATERIAL ACTIVITY CONCENTRATIONS (Section 4.3) — published typical
   Ra-226 / Th-232 / K-40 activity for common construction/finish materials,
   used ONLY to flag an additional indoor gamma/thoron contribution when the
   questionnaire reports granite/stone. If no citable source exists for a
   material, the code returns "no published reference available" rather than a
   guess.

All ranges are (low_multiplier, high_multiplier) tuples applied to the geogenic
soil-gas-derived indoor radon estimate. They are operational adjustment factors
grounded in the cited literature's qualitative direction and magnitude, and are
adjustable here rather than buried in logic.

Primary literature basis for the DIRECTION and approximate MAGNITUDE of these
building factors:
  - UNSCEAR 2000 Report, Annex B (indoor/outdoor radon, floor & ventilation
    influence).
  - WHO Handbook on Indoor Radon (2009), Ch. 3 (building factors, remediation
    effectiveness of sub-slab depressurisation & membranes).
  - Ireland EPA / ICRP guidance on remediation effectiveness.
  - EU BSS 2013/59/Euratom (RP-112) for building-material activity indices.
Material activity concentrations: European Commission Radiation Protection 112
"Radiological Protection Principles concerning the Natural Radioactivity of
Building Materials" (1999), Table with typical & maximum activity concentrations.
"""

from __future__ import annotations
from typing import Dict, Optional, Tuple

# ══════════════════════════════════════════════════════════════════════════
# 1. RADON MULTIPLIER RANGES  (low, high) applied to geogenic indoor estimate
# ══════════════════════════════════════════════════════════════════════════
# Reference case (multiplier 1.0) = solid ground-bearing slab WITH radon
# membrane, standard natural ventilation, no remediation.

FLOOR_CONSTRUCTION: Dict[str, Tuple[float, float]] = {
    # Suspended timber floors have a ventilated void that can draw soil gas;
    # generally higher ingress than a sealed slab. [UNSCEAR 2000; WHO 2009]
    "suspended_timber":            (1.2, 2.2),
    # Suspended concrete with a void — intermediate. [WHO 2009]
    "suspended_concrete":          (1.0, 1.8),
    # Solid slab WITHOUT a membrane — direct contact, no gas barrier. [WHO 2009]
    "solid_slab_no_membrane":      (1.0, 1.9),
    # Solid slab WITH an intact membrane — the reference protective case. [WHO 2009]
    "solid_slab_with_membrane":    (0.4, 1.0),
    # Unknown floor construction -> widen across the full plausible span (Rule 7).
    "unknown":                     (0.4, 2.2),
}

VENTILATION: Dict[str, Tuple[float, float]] = {
    # Mechanical ventilation with heat recovery dilutes indoor radon. [WHO 2009]
    "mvhr":                        (0.5, 0.9),
    # Positive-input / mechanical extract ventilation. [WHO 2009]
    "mechanical_extract":          (0.6, 1.0),
    # Natural background ventilation (trickle vents, occasional opening).
    "natural":                     (0.9, 1.3),
    # Tightly sealed / draught-proofed with little ventilation raises radon.
    "sealed_minimal":              (1.1, 1.8),
    "unknown":                     (0.5, 1.8),
}

REMEDIATION: Dict[str, Tuple[float, float]] = {
    # Active sub-slab depressurisation (radon sump + fan) is highly effective.
    # WHO 2009 reports typical reductions of 50-90% -> multiplier 0.1-0.5.
    "active_sump":                 (0.1, 0.5),
    # Passive membrane/sump installed but not activated. [WHO 2009]
    "passive_measures":            (0.5, 0.9),
    # No remediation in place — reference.
    "none":                        (1.0, 1.0),
    "unknown":                     (0.1, 1.0),
}

HEATING_CLOSURE: Dict[str, Tuple[float, float]] = {
    # Long closed-up heated periods (winter, low air change) concentrate radon.
    "long_closed_heated":          (1.1, 1.5),
    # Balanced / typical pattern.
    "typical":                     (0.9, 1.1),
    # Frequently open / cross-ventilated.
    "often_open":                  (0.7, 1.0),
    "unknown":                     (0.7, 1.5),
}


def floor_multiplier(key: Optional[str]) -> Tuple[float, float]:
    return FLOOR_CONSTRUCTION.get(key or "unknown", FLOOR_CONSTRUCTION["unknown"])


def ventilation_multiplier(key: Optional[str]) -> Tuple[float, float]:
    return VENTILATION.get(key or "unknown", VENTILATION["unknown"])


def remediation_multiplier(key: Optional[str]) -> Tuple[float, float]:
    return REMEDIATION.get(key or "unknown", REMEDIATION["unknown"])


def heating_multiplier(key: Optional[str]) -> Tuple[float, float]:
    return HEATING_CLOSURE.get(key or "unknown", HEATING_CLOSURE["unknown"])


# ══════════════════════════════════════════════════════════════════════════
# 2. BUILDING-MATERIAL ACTIVITY CONCENTRATIONS  (Bq/kg)
# Source: European Commission Radiation Protection 112 (1999),
# "Radiological Protection Principles concerning the Natural Radioactivity of
# Building Materials", typical activity concentration table.
# Only materials with a citable published value appear here. Anything not
# listed returns "no published reference available".
# ══════════════════════════════════════════════════════════════════════════
MATERIAL_ACTIVITIES_BQKG: Dict[str, Dict[str, float]] = {
    # material_key: {Ra226, Th232, K40, label, source}
    "granite": {
        "A_Ra226": 100.0, "A_Th232": 80.0, "A_K40": 1000.0,
        "label": "Granite (worktop / cladding / structural stone)",
        "source": "EC Radiation Protection 112 (1999), typical granite",
    },
    "natural_stone_general": {
        "A_Ra226": 60.0, "A_Th232": 60.0, "A_K40": 640.0,
        "label": "Natural stone (general)",
        "source": "EC Radiation Protection 112 (1999)",
    },
    "concrete": {
        "A_Ra226": 40.0, "A_Th232": 30.0, "A_K40": 400.0,
        "label": "Concrete",
        "source": "EC Radiation Protection 112 (1999), typical concrete",
    },
    "granite_tuff": {
        "A_Ra226": 100.0, "A_Th232": 100.0, "A_K40": 1000.0,
        "label": "Granitic tuff / volcanic stone",
        "source": "EC Radiation Protection 112 (1999)",
    },
}


def material_activities(material_key: Optional[str]) -> Optional[Dict[str, float]]:
    """Return published material activities, or None if no citable source."""
    if not material_key:
        return None
    return MATERIAL_ACTIVITIES_BQKG.get(material_key)
