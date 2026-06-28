#!/usr/bin/env python3
"""
Aerial survey flight planner for REE and critical minerals exploration.

Usage:
    python3 plan_flight.py --area-km2 <n> --platform <p> --sensor <s> --target-type <t> [--output <path>]

Produces a JSON survey plan with line spacing, altitude, endurance, coverage, and cost estimate.
"""

import argparse
import json
import sys
from pathlib import Path


# --- Defaults by target type ---
# line_spacing_m (primary), altitude_m_agl by sensor
TARGET_DEFAULTS = {
    "carbonatite":   {"line_spacing_m": 100, "gamma_alt": 150, "pxrf_alt": 30,  "detail_spacing_m": 50},
    "iac_clay":      {"line_spacing_m": 200, "gamma_alt": 200, "pxrf_alt": 40,  "detail_spacing_m": 100},
    "ree_vein":      {"line_spacing_m": 50,  "gamma_alt": 150, "pxrf_alt": 22,  "detail_spacing_m": 20},
    "pegmatite":     {"line_spacing_m": 50,  "gamma_alt": 150, "pxrf_alt": 20,  "detail_spacing_m": 25},
    "porphyry":      {"line_spacing_m": 400, "gamma_alt": 200, "pxrf_alt": 50,  "detail_spacing_m": 100},
}

# Platform specs: flight_time_min (with payload), speed_m_s, cost_per_day_usd
PLATFORM_SPECS = {
    "multirotor":   {"flight_time_min": 25, "speed_m_s": 4,  "cost_per_day_usd": 1200},
    "fixed_wing":   {"flight_time_min": 90, "speed_m_s": 15, "cost_per_day_usd": 1250},
    "hybrid_vtol":  {"flight_time_min": 135,"speed_m_s": 18, "cost_per_day_usd": 1350},
}

# Sensor -> altitude key in TARGET_DEFAULTS
SENSOR_ALT_KEY = {"gamma": "gamma_alt", "pxrf": "pxrf_alt", "hyperspectral": "pxrf_alt", "lidar": "gamma_alt"}

# Weather constraints by sensor
WEATHER = {
    "gamma":        "Any weather except icing (even rain is OK)",
    "pxrf":         "Clear sky, low moisture (early morning or post-rain-washed air)",
    "hyperspectral": "Clear sky only, solar elevation > 20 deg",
    "lidar":        "Any weather except icing",
}


def plan(area_km2, platform, sensor, target_type):
    if target_type not in TARGET_DEFAULTS:
        raise ValueError(f"Unknown target_type '{target_type}'. Choose from: {list(TARGET_DEFAULTS)}")
    if platform not in PLATFORM_SPECS:
        raise ValueError(f"Unknown platform '{platform}'. Choose from: {list(PLATFORM_SPECS)}")
    if sensor not in SENSOR_ALT_KEY:
        raise ValueError(f"Unknown sensor '{sensor}'. Choose from: {list(SENSOR_ALT_KEY)}")

    tgt = TARGET_DEFAULTS[target_type]
    plat = PLATFORM_SPECS[platform]

    line_spacing = tgt["line_spacing_m"]
    altitude = tgt[SENSOR_ALT_KEY[sensor]]
    speed = plat["speed_m_s"]
    flight_time = plat["flight_time_min"]

    # Coverage per flight: swath = 2 × line_spacing (one line each side), distance = speed × time
    swath_m = 2 * line_spacing
    distance_m = speed * flight_time * 60
    coverage_per_flight_km2 = (distance_m * swath_m) / 1e6

    # Battery swaps: assume 2 flights per battery set for multirotor, 1 for fixed-wing
    if platform == "multirotor":
        battery_swaps = max(1, int(area_km2 / coverage_per_flight_km2))
        daily_coverage = coverage_per_flight_km2 * 4  # 4 flights/day with swaps
    else:
        battery_swaps = max(1, int(area_km2 / coverage_per_flight_km2))
        daily_coverage = coverage_per_flight_km2 * 2

    survey_days = max(1, int(area_km2 / daily_coverage) + (1 if area_km2 % daily_coverage else 0))

    # Cost: scale by area tier
    if area_km2 < 50:
        cost_per_km2 = 80.0
    elif area_km2 < 500:
        cost_per_km2 = 45.0
    else:
        cost_per_km2 = 20.0
    total_cost = area_km2 * cost_per_km2

    return {
        "platform": platform,
        "sensor": sensor,
        "target_type": target_type,
        "area_km2": area_km2,
        "line_spacing_m": line_spacing,
        "detail_line_spacing_m": tgt["detail_spacing_m"],
        "altitude_m_agl": altitude,
        "speed_m_s": speed,
        "flight_time_min": flight_time,
        "battery_swaps": battery_swaps,
        "coverage_per_flight_km2": round(coverage_per_flight_km2, 2),
        "daily_coverage_km2": round(daily_coverage, 2),
        "survey_days": survey_days,
        "weather_constraints": WEATHER[sensor],
        "estimated_cost_usd": int(total_cost),
        "cost_per_km2": cost_per_km2,
    }


def main():
    parser = argparse.ArgumentParser(description="Plan an aerial geochemical survey.")
    parser.add_argument("--area-km2", type=float, required=True, help="Survey area in km^2")
    parser.add_argument(
        "--platform",
        required=True,
        choices=list(PLATFORM_SPECS),
        help="Drone platform class",
    )
    parser.add_argument(
        "--sensor",
        required=True,
        choices=list(SENSOR_ALT_KEY),
        help="Primary sensor",
    )
    parser.add_argument(
        "--target-type",
        required=True,
        choices=list(TARGET_DEFAULTS),
        help="Deposit type being targeted",
    )
    parser.add_argument("--output", default=None, help="Optional output JSON path")
    args = parser.parse_args()

    plan_dict = plan(args.area_km2, args.platform, args.sensor, args.target_type)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(plan_dict, f, indent=2)
        print(f"Wrote survey plan to {out_path}")
    else:
        print(json.dumps(plan_dict, indent=2))


if __name__ == "__main__":
    main()
