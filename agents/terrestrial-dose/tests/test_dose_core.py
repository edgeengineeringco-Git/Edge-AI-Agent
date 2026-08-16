"""
Test suite for dose_calculation_core.py
All assertions must pass before proceeding.
Includes Ireland-specific tests for 200 Bq/m³ action level.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dose_core.dose_calculation_core import (
    polygon_dose_fingerprint,
    radon_inhalation_dose,
    risk_class,
    radon_inhalation_dose_irish,
    risk_class_irish,
    RADON_IRISH_FACTOR,
    IRISH_RN_ACTION,
)


def test_world_average_soil():
    """World-average soil → matches UNSCEAR, GREEN."""
    fp = polygon_dose_fingerprint(lithology="world_average_soil")
    assert abs(fp["arms_mSv_yr"]["thoron"] - 0.10) < 0.02, \
        f"thoron {fp['arms_mSv_yr']['thoron']} != 0.10"
    assert 45 < fp["gamma_rate_nGy_h"] < 60, \
        f"gamma_rate {fp['gamma_rate_nGy_h']} not in 45–60"
    assert fp["risk"]["tier"] == "GREEN"


def test_granite_radon_dominated_amber():
    """GLiM acid plutonic (Pa = granite) → radon-dominated, AMBER."""
    fp = polygon_dose_fingerprint(lithology="Pa", dist_fault_m=200, lineament_density=1.0)
    assert fp["arms_mSv_yr"]["radon"] > fp["arms_mSv_yr"]["thoron"]
    assert fp["arms_mSv_yr"]["radon"] > fp["arms_mSv_yr"]["gamma"]
    assert fp["risk"]["tier"] == "AMBER"


def test_carbonate_green():
    """GLiM carbonate (Sc = limestone) → low dose, GREEN."""
    fp = polygon_dose_fingerprint(lithology="Sc")
    assert fp["total_terrestrial_mSv_yr"] < 1.0, \
        f"total {fp['total_terrestrial_mSv_yr']} >= 1.0"
    assert fp["risk"]["tier"] == "GREEN"


def test_monazite_thoron_red():
    """Monazite/REE → thoron dominant, RED."""
    fp = polygon_dose_fingerprint(lithology="monazite_bearing")
    assert fp["arms_mSv_yr"]["thoron"] > 1.0, \
        f"thoron {fp['arms_mSv_yr']['thoron']} <= 1.0"
    assert fp["risk"]["tier"] == "RED"


def test_measurement_override():
    """Measurement override works — eU=10 ppm → A_Ra226 ≈ 122.2."""
    fp = polygon_dose_fingerprint(lithology="Pa", eU_ppm=10.0)
    assert abs(fp["activities_Bq_kg"]["A_Ra226"] - 122.2) < 0.1, \
        f"A_Ra226 {fp['activities_Bq_kg']['A_Ra226']} != 122.2"
    assert any("measured" in p for p in fp["provenance"]), \
        "No 'measured' tag in provenance"


def test_radon_action_level():
    """Radon action level → 300 Bq/m³ = 10 mSv/yr, RED."""
    assert abs(radon_inhalation_dose(300.0) - 10.0) < 0.01, \
        f"radon_inhalation_dose(300) = {radon_inhalation_dose(300.0)}"
    assert risk_class(10.0, C_Rn=300.0)["tier"] == "RED"


# ══════════════════════════════════════════════════════════════════════════════
# IRELAND-SPECIFIC TESTS
# ══════════════════════════════════════════════════════════════════════════════

def test_irish_radon_factor():
    """Irish 200 Bq/m³ → ~6.7 mSv/yr."""
    assert abs(RADON_IRISH_FACTOR - (6.7 / 200.0)) < 1e-9
    assert abs(radon_inhalation_dose_irish(200.0) - 6.7) < 0.01


def test_irish_radon_at_100():
    """Irish factor at 100 Bq/m³ → ~3.35 mSv/yr."""
    dose = radon_inhalation_dose_irish(100.0)
    assert abs(dose - 3.35) < 0.01, f"dose={dose}"


def test_risk_class_irish_green():
    """Low dose, low radon → GREEN."""
    risk = risk_class_irish(1.5, C_Rn=50)
    assert risk["tier"] == "GREEN"


def test_risk_class_irish_radon_amber():
    """Radon 150 Bq/m³ (between WHO 100 and Irish 200) → AMBER."""
    risk = risk_class_irish(1.5, C_Rn=150)
    assert risk["tier"] == "AMBER"
    assert any("RADON_ELEVATED" in f for f in risk["flags"])


def test_risk_class_irish_radon_red():
    """Radon 200 Bq/m³ (Irish action) → RED regardless of dose."""
    risk = risk_class_irish(1.0, C_Rn=200)
    assert risk["tier"] == "RED"
    assert any("RADON_ACTION" in f for f in risk["flags"])


def test_risk_class_irish_high_dose_red():
    """Dose > 6.6 → RED."""
    risk = risk_class_irish(7.0, C_Rn=50)
    assert risk["tier"] == "RED"


def test_risk_class_irish_raeq_red():
    """Ra-eq ≥ 370 → RED."""
    risk = risk_class_irish(1.5, C_Rn=50, raeq=400)
    assert risk["tier"] == "RED"
    assert any("RAEQ_HIGH" in f for f in risk["flags"])


def test_risk_class_irish_gamma_red():
    """Gamma rate ≥ 1000 nGy/h → RED."""
    risk = risk_class_irish(1.5, C_Rn=50, gamma_rate=1200)
    assert risk["tier"] == "RED"
    assert any("GAMMA_HIGH" in f for f in risk["flags"])
