# tests/test_dose_core.py
from dose_core.dose_calculation_core import polygon_dose_fingerprint as fp, radon_inhalation_dose

def test_world_average_soil():
    r = fp(lithology="world_average_soil")
    assert abs(r["arms_mSv_yr"]["thoron"] - 0.10) < 0.02
    assert 45 < r["gamma_rate_nGy_h"] < 60
    assert r["risk"]["tier"] == "GREEN"

def test_granite_amber():
    r = fp(lithology="Pa", dist_fault_m=200, lineament_density=1.0)
    assert r["arms_mSv_yr"]["radon"] > r["arms_mSv_yr"]["thoron"]
    assert r["risk"]["tier"] == "AMBER"

def test_carbonate_green():
    r = fp(lithology="Sc")
    assert r["total_terrestrial_mSv_yr"] < 1.0
    assert r["risk"]["tier"] == "GREEN"

def test_monazite_red():
    r = fp(lithology="monazite_bearing")
    assert r["arms_mSv_yr"]["thoron"] > 1.0
    assert r["risk"]["tier"] == "RED"

def test_measurement_override():
    r = fp(lithology="Pa", eU_ppm=10.0)
    assert abs(r["activities_Bq_kg"]["A_Ra226"] - 122.2) < 0.1
    assert any("measured" in p for p in r["provenance"])

def test_radon_action_level():
    assert abs(radon_inhalation_dose(300.0) - 10.0) < 0.01
