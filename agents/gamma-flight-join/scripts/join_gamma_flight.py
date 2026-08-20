#!/usr/bin/env python3
"""
Join gamma spectrogram (FORMAT 3) with an Airdata drone flight log.

Professional airborne gamma survey workflow. This tool:
  - Parses a gamma spectrogram text file in FORMAT 3 (GammaSpectacular / ImpulseQt export).
  - Parses an Airdata drone flight log CSV.
  - Converts spectrogram timestamps (Unix ms) and flight-log timestamps (UTC) to a common UTC timebase.
  - Performs a nearest-time join so each gamma spectrum record gets precise drone position
    and kinematic parameters (in SI units).
  - Writes a joined CSV with one row per spectrum plus all channels.
  - Writes a separate calibration metadata text file containing TWO calibration sets per project:
      (1) Factory / Cs-check calibration from ImpulseQt (screen values),
      (2) Best-fit survey calibration derived from all spectra in the project.

The calibration coefficients inside the spectrogram text file are intentionally ignored;
only the factory calibration (passed via CLI) and the best-fit calibration are used.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import math
import textwrap
from pathlib import Path
from typing import List, Tuple

import warnings

import numpy as np
import pandas as pd
from scipy.optimize import OptimizeWarning, curve_fit
from scipy.signal import find_peaks

# curve_fit emits harmless covariance warnings when the reference points are
# nearly collinear (common with sparse peak sets). Suppress the noise; the fit
# result itself is still used and scored.
warnings.simplefilter("ignore", OptimizeWarning)

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class SpectrogramHeader:
    """Metadata parsed from the spectrogram header (FORMAT 3)."""

    format_version: int
    start_local_dt: dt.datetime
    counts_total: int
    cps: float
    integration_time_s: float
    coord_str: str
    gps_start_ms: int
    gps_end_ms: int
    phone_lat: float
    phone_lon: float
    description: str
    device: str
    base_duration_s: float
    n_channels: int
    n_calibration_coefficients: int
    calibration_coefficients: List[float]
    base_channels: np.ndarray


@dataclasses.dataclass
class GammaRecord:
    """One delta-spectrum record: timestamp, phone location and channel counts."""

    spectrum_id: int
    timestamp_ms: int
    datetime_utc: dt.datetime
    latitude_phone: float
    longitude_phone: float
    duration_s: float
    altitude_phone: float = math.nan
    channels: np.ndarray = dataclasses.field(default_factory=lambda: np.array([], dtype=np.int32))
    record_type: str = "Delta"


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def parse_header_line(line: str) -> Tuple[dt.datetime, int, float, float, str]:
    """Parse the human-readable header line with counts and CPS.

    Example:
      "2026.08.03 11:10:45 +0100 Counts: 169308, ~cps: 455.496, Time: 371.70 s, Coord: ..."
    """

    parts = line.strip().split(" Counts:")
    if len(parts) < 2:
        raise ValueError(f"Unexpected header line format: {line}")

    dt_part = parts[0]
    rest = " Counts:" + parts[1]

    # Local datetime with offset (e.g. +0100 for Irish summer time)
    start_dt = dt.datetime.strptime(dt_part, "%Y.%m.%d %H:%M:%S %z")

    counts = 0
    cps = math.nan
    time_s = math.nan
    coord_str = ""

    idx = rest.find("Counts:")
    if idx != -1:
        after = rest[idx + len("Counts:"):]
        counts = int(after.split(",", 1)[0].strip())

    idx = rest.find("~cps:")
    if idx != -1:
        after = rest[idx + len("~cps:"):]
        cps = float(after.split(",", 1)[0].strip())

    idx = rest.find("Time:")
    if idx != -1:
        after = rest[idx + len("Time:"):]
        time_s = float(after.split(" s", 1)[0].strip())

    idx = rest.find("Coord:")
    if idx != -1:
        coord_str = rest[idx + len("Coord:"):].strip()

    return start_dt, counts, cps, time_s, coord_str


def parse_spectrogram(path: Path) -> Tuple[SpectrogramHeader, List[GammaRecord]]:
    """Parse a FORMAT 3 spectrogram file into header + list of GammaRecord.

    Assumed structure (confirmed on sample files):
      1: "FORMAT: 3"
      2: human-readable header line
      3: GPS start time (Unix ms)
      4: GPS end time (Unix ms)
      5: phone latitude (decimal degrees)
      6: phone longitude (decimal degrees)
      7: description string
      8: device string
      9: base spectrum duration (seconds)
     10: number of channels (e.g. 8192)
     11+: base spectrum channel counts (one integer per line, length = n_channels)
     After base spectrum: repeated delta-spectra blocks:
        timestamp_ms
        latitude_phone
        longitude_phone
        duration_s
        ch_0 ch_1 ... ch_(n_channels-1)
    """

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    if not lines:
        raise ValueError(f"Spectrogram file '{path}' is empty")

    first = lines[0].strip()
    if not first.startswith("FORMAT:"):
        raise ValueError(f"Unexpected first line: {first}")
    format_version = int(first.split(":", 1)[1].strip())

    header_line = lines[1].strip()
    start_dt, counts_total, cps, time_s, coord_str = parse_header_line(header_line)

    gps_start_ms = int(lines[2].strip())
    gps_end_ms = int(lines[3].strip())
    phone_lat = float(lines[4].strip())
    phone_lon = float(lines[5].strip())
    description = lines[6].strip()
    device = lines[7].strip()
    base_duration_s = float(lines[8].strip())
    # FORMAT 3 exports may serialise integer fields as e.g. ``8192.0``.
    n_channels = int(float(lines[9].strip()))
    n_cal = int(float(lines[10].strip()))
    cal_start = 11
    cal_end = cal_start + n_cal
    calibration_coefficients = [float(lines[i].strip()) for i in range(cal_start, cal_end)]

    base_start = cal_end
    base_end = base_start + n_channels
    if base_end > len(lines):
        raise ValueError("Spectrogram file truncated: not enough lines for base spectrum")

    base_spectrum = np.fromiter(
        (int(float(lines[i].strip())) for i in range(base_start, base_end)),
        dtype=np.int32,
        count=n_channels,
    )

    header = SpectrogramHeader(
        format_version=format_version,
        start_local_dt=start_dt,
        counts_total=counts_total,
        cps=cps,
        integration_time_s=time_s,
        coord_str=coord_str,
        gps_start_ms=gps_start_ms,
        gps_end_ms=gps_end_ms,
        phone_lat=phone_lat,
        phone_lon=phone_lon,
        description=description,
        device=device,
        base_duration_s=base_duration_s,
        n_channels=n_channels,
        n_calibration_coefficients=n_cal,
        calibration_coefficients=calibration_coefficients,
        base_channels=base_spectrum,
    )

    # Read each raw channel vector as exactly n_channels consecutive values.
    # Calibration is metadata only and must never alter or reorder channels.
    remaining_text = "".join(lines[base_end:])
    tokens = remaining_text.split()

    # A FORMAT 3 export can contain a few trailing base-spectrum values or
    # padding lines before the first delta record. Locate the first genuine
    # record header rather than silently treating padding as timestamp/lat/
    # lon/duration and shifting every channel vector.
    idx = 0
    while idx + 4 + n_channels <= len(tokens):
        try:
            candidate_ts = int(float(tokens[idx]))
            candidate_lat = float(tokens[idx + 1])
            candidate_lon = float(tokens[idx + 2])
            candidate_duration = float(tokens[idx + 3])
        except ValueError:
            idx += 1
            continue
        if (
            candidate_ts > 1e11
            and -90.0 <= candidate_lat <= 90.0
            and -180.0 <= candidate_lon <= 180.0
            and 0.0 < candidate_duration <= 3600.0
        ):
            break
        idx += 1
    else:
        idx = len(tokens)

    # Determine whether this export uses four metadata fields
    # (timestamp, lat, lon, duration) or five (plus altitude). Exact token
    # grouping prevents a different base integration time from shifting data.
    if (len(tokens) - idx) % (5 + n_channels) == 0:
        per_record_header = 5
    elif (len(tokens) - idx) % (4 + n_channels) == 0:
        per_record_header = 4
    else:
        per_record_header = 5 if idx + 5 < len(tokens) else 4

    records: List[GammaRecord] = [GammaRecord(
        spectrum_id=0, timestamp_ms=gps_start_ms,
        datetime_utc=dt.datetime.fromtimestamp(gps_start_ms / 1000.0, tz=dt.timezone.utc),
        latitude_phone=phone_lat, longitude_phone=phone_lon, altitude_phone=math.nan,
        duration_s=base_duration_s, channels=base_spectrum, record_type="Base")]
    spectrum_id = 1

    while idx + per_record_header + n_channels <= len(tokens):
        try:
            ts_ms = int(float(tokens[idx])); idx += 1
            lat = float(tokens[idx]); idx += 1
            lon = float(tokens[idx]); idx += 1
            fourth = float(tokens[idx]); idx += 1
            altitude = math.nan
            duration = fourth
            if per_record_header == 5:
                altitude = fourth
                duration = float(tokens[idx]); idx += 1

        except (ValueError, IndexError) as exc:
            print(f"[WARN] Stopping delta-spectrum parse at token {idx}: {exc}")
            break

        channel_vals = tokens[idx: idx + n_channels]
        if len(channel_vals) != n_channels:
            print(
                f"[WARN] Incomplete channel set at token {idx}: "
                f"got {len(channel_vals)}, expected {n_channels}; stopping."
            )
            break

        # Counts are raw detector channels. Convert only numeric formatting
        # (some exporters write 12.0); never energy-calibrate or reorder them.
        channels = np.fromiter(
            (int(float(value)) for value in channel_vals),
            dtype=np.int32,
            count=n_channels,
        )
        idx += n_channels

        # The four fields are always: timestamp_ms, latitude, longitude,
        # duration_s.  Keep the channel vector aligned exactly after them;
        # do not infer or substitute header fields from channel data.
        dt_utc = dt.datetime.fromtimestamp(ts_ms / 1000.0, tz=dt.timezone.utc)

        records.append(
            GammaRecord(
                spectrum_id=spectrum_id,
                timestamp_ms=ts_ms,
                datetime_utc=dt_utc,
                latitude_phone=lat,
                longitude_phone=lon,
                altitude_phone=altitude,
                duration_s=duration,
                channels=channels,
                record_type=f"Delta {spectrum_id}",
            )
        )
        spectrum_id += 1

    if not records:
        print("[WARN] No delta-spectrum records parsed; file may contain only base spectrum.")

    return header, records


def _ensure_datetime_utc(series: pd.Series) -> pd.Series:
    """Convert a pandas Series to timezone-aware UTC datetimes."""

    dt_series = pd.to_datetime(series, utc=True, errors="coerce")
    if dt_series.isna().all():
        raise ValueError("Could not parse any UTC datetimes from flight log")
    return dt_series


def parse_flight_log(path: Path) -> pd.DataFrame:
    """Parse Airdata flight log CSV and add SI-converted columns."""

    df = pd.read_csv(path)

    # Column lookup helper (case-insensitive exact match)
    col = lambda name: next((c for c in df.columns if c.strip().lower() == name.lower()), None)

    time_ms_col = col("time(millisecond)") or col("time_ms")
    datetime_col = col("datetime(utc)") or col("datetime_utc")
    lat_col = col("latitude")
    lon_col = col("longitude")

    required = [time_ms_col, datetime_col, lat_col, lon_col]
    if any(c is None for c in required):
        raise ValueError(f"Flight log missing required core columns: {required}")

    df["time_ms"] = df[time_ms_col]
    df["datetime_utc"] = _ensure_datetime_utc(df[datetime_col])
    df["latitude_drone"] = pd.to_numeric(df[lat_col], errors='coerce')
    df["longitude_drone"] = pd.to_numeric(df[lon_col], errors='coerce')

    ft_to_m = 0.3048
    for src, dest in [
        ("height_above_takeoff(feet)", "height_above_takeoff_m"),
        ("height_above_ground_at_drone_location(feet)", "height_above_ground_at_drone_location_m"),
        ("ground_elevation_at_drone_location(feet)", "ground_elevation_at_drone_location_m"),
        ("altitude_above_seaLevel(feet)", "altitude_above_seaLevel_m"),
        ("height_sonar(feet)", "height_sonar_m"),
    ]:
        src_col = col(src)
        if src_col is not None:
            df[dest] = pd.to_numeric(df[src_col], errors='coerce') * ft_to_m

    mph_to_mps = 0.44704
    for src, dest in [
        ("speed(mph)", "speed_mps"),
        ("xSpeed(mph)", "xSpeed_mps"),
        ("ySpeed(mph)", "ySpeed_mps"),
        ("zSpeed(mph)", "zSpeed_mps"),
    ]:
        src_col = col(src)
        if src_col is not None:
            df[dest] = pd.to_numeric(df[src_col], errors='coerce') * mph_to_mps

    for src, dest in [
        ("distance(feet)", "distance_m"),
        ("mileage(feet)", "mileage_m"),
    ]:
        src_col = col(src)
        if src_col is not None:
            df[dest] = pd.to_numeric(df[src_col], errors='coerce') * ft_to_m

    for name in [
        "satellites",
        "gpslevel",
        "flycStateRaw",
        "flycStatemessage",
        "compassheadingdegrees",
        "pitchdegrees",
        "rolldegrees",
    ]:
        src_col = col(name)
        if src_col is not None:
            df[name] = df[src_col]

    df = df.sort_values("datetime_utc").reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# Calibration fitting (factory + best-fit survey)
# ---------------------------------------------------------------------------

REFERENCE_LINES_KEV = {
    "Cs137": 661.7,
    "K40": 1460.8,
    "Tl208_583": 583.0,
    "Tl208_2614": 2614.5,
}


def poly_energy(ch: np.ndarray, a0: float, a1: float, a2: float = 0.0, a3: float = 0.0) -> np.ndarray:
    """Polynomial channel->energy mapping."""

    return a0 + a1 * ch + a2 * ch ** 2 + a3 * ch ** 3


def fit_best_calibration(
    factory_coeffs: List[float],
    channel_axis: np.ndarray,
    aggregated_counts: np.ndarray,
) -> Tuple[List[float], str]:
    """Fit a best-fit calibration using all spectra in the survey.

    - factory_coeffs: [a0, a1, a2, a3] from ImpulseQt Cs-check screen.
    - channel_axis: np.arange(n_channels).
    - aggregated_counts: counts per channel aggregated across all spectra.

    Returns best-fit coefficients [b0..b3] and a textual summary.
    If fitting fails or insufficient peaks are found, returns factory_coeffs.
    """

    if len(factory_coeffs) < 4:
        factory_coeffs = factory_coeffs + [0.0] * (4 - len(factory_coeffs))
    factory_coeffs = factory_coeffs[:4]

    a0_f, a1_f, a2_f, a3_f = factory_coeffs

    energy_est = poly_energy(channel_axis, a0_f, a1_f, a2_f, a3_f)

    if aggregated_counts.max() <= 0:
        return factory_coeffs, "Aggregated spectrum has no counts; using factory calibration."

    peaks, _ = find_peaks(aggregated_counts, prominence=aggregated_counts.max() * 0.01)
    if peaks.size < 2:
        return factory_coeffs, "Insufficient peaks in aggregated spectrum; using factory calibration."

    obs_channels = []
    ref_energies = []
    for name, ref_E in REFERENCE_LINES_KEV.items():
        idx = np.argmin(np.abs(energy_est[peaks] - ref_E))
        obs_channels.append(peaks[idx])
        ref_energies.append(ref_E)

    obs_channels = np.array(obs_channels, dtype=float)
    ref_energies = np.array(ref_energies, dtype=float)

    models = []

    def f1(x, b0, b1):
        return poly_energy(x, b0, b1)

    try:
        popt1, _ = curve_fit(f1, obs_channels, ref_energies)
        pred1 = f1(obs_channels, *popt1)
        rms1 = float(np.sqrt(np.mean((pred1 - ref_energies) ** 2)))
        models.append(("linear", [popt1[0], popt1[1], 0.0, 0.0], rms1, 2))
    except Exception:
        pass

    def f2(x, b0, b1, b2):
        return poly_energy(x, b0, b1, b2)

    try:
        popt2, _ = curve_fit(f2, obs_channels, ref_energies)
        pred2 = f2(obs_channels, *popt2)
        rms2 = float(np.sqrt(np.mean((pred2 - ref_energies) ** 2)))
        models.append(("quadratic", [popt2[0], popt2[1], popt2[2], 0.0], rms2, 3))
    except Exception:
        pass

    def f3(x, b0, b1, b2, b3):
        return poly_energy(x, b0, b1, b2, b3)

    try:
        popt3, _ = curve_fit(f3, obs_channels, ref_energies)
        pred3 = f3(obs_channels, *popt3)
        rms3 = float(np.sqrt(np.mean((pred3 - ref_energies) ** 2)))
        models.append(("cubic", [popt3[0], popt3[1], popt3[2], popt3[3]], rms3, 4))
    except Exception:
        pass

    if not models:
        return factory_coeffs, "Could not fit polynomial calibration; using factory calibration."

    lambda_penalty = 0.05  # keV per parameter
    scored = [(name, coeffs, rms + lambda_penalty * n_params) for name, coeffs, rms, n_params in models]
    best_name, best_coeffs, _ = min(scored, key=lambda x: x[2])

    summary = (
        f"Best-fit survey calibration: {best_name} (b0={best_coeffs[0]:.6f}, "
        f"b1={best_coeffs[1]:.6f}, b2={best_coeffs[2]:.6f}, b3={best_coeffs[3]:.6f})."
    )
    return best_coeffs, summary


# ---------------------------------------------------------------------------
# Joining gamma and flight log
# ---------------------------------------------------------------------------

ESSENTIAL_COLUMNS = [
    "spectrum_id",
    "gamma_datetime_utc",
    "gamma_timestamp_ms",
    "datetime_utc",
    "time_ms",
    "latitude_drone",
    "longitude_drone",
    "altitude_above_seaLevel_m",
    "height_above_ground_at_drone_location_m",
    "height_above_takeoff_m",
    "ground_elevation_at_drone_location_m",
    "height_sonar_m",
    "speed_mps",
    "distance_m",
    "mileage_m",
    "satellites",
    "gpslevel",
    "flycStateRaw",
    "flycStatemessage",
    "compassheadingdegrees",
    "pitchdegrees",
    "rolldegrees",
    "xSpeed_mps",
    "ySpeed_mps",
    "zSpeed_mps",
]


def records_to_dataframe(header: SpectrogramHeader, records: List[GammaRecord]) -> pd.DataFrame:
    """Convert GammaRecord list to DataFrame with metadata and channels."""

    if not records:
        raise ValueError("No gamma records found in spectrogram file.")

    n_channels = header.n_channels

    data = {
        "spectrum_id": [r.spectrum_id for r in records],
        "gamma_timestamp_ms": [r.timestamp_ms for r in records],
        "gamma_datetime_utc": [r.datetime_utc for r in records],
        "gamma_lat_phone": [r.latitude_phone for r in records],
        "gamma_lon_phone": [r.longitude_phone for r in records],
        "gamma_alt_phone": [r.altitude_phone for r in records],
        "gamma_duration_s": [r.duration_s for r in records],
        "spectrum_type": [r.record_type for r in records],
        "gamma_counts_total": header.counts_total,
        "gamma_cps": header.cps,
        "gamma_integration_time_s": header.integration_time_s,
        "gamma_base_duration_s": header.base_duration_s,
    }

    channel_matrix = np.vstack([r.channels for r in records])  # (n_records, n_channels)
    for ch in range(n_channels):
        data[f"ch_{ch}"] = channel_matrix[:, ch]

    df = pd.DataFrame(data)
    df["gamma_datetime_utc"] = pd.to_datetime(df["gamma_datetime_utc"], utc=True)
    return df


def join_gamma_with_flight(
    gamma_df: pd.DataFrame,
    flight_df: pd.DataFrame,
    tolerance_seconds: float = 5.0,
) -> pd.DataFrame:
    """Nearest-time join between gamma spectra and flight log."""

    gamma_df = gamma_df.sort_values("gamma_datetime_utc").reset_index(drop=True)

    return pd.merge_asof(
        gamma_df,
        flight_df,
        left_on="gamma_datetime_utc",
        right_on="datetime_utc",
        direction="nearest",
        tolerance=pd.Timedelta(seconds=tolerance_seconds),
    )


# ---------------------------------------------------------------------------
# Calibration metadata file (two sets per project)
# ---------------------------------------------------------------------------

CALIBRATION_TEXT_TEMPLATE = """Project: {project_name}
Detector: {detector}
Software: {software}

[Factory / Cs-check calibration]
Source: ImpulseQt calibration spectrum (screen values)
Equation: E = a0 + a1 * ch + a2 * ch^2 + a3 * ch^3
Coefficients:
  a0 = {a0_factory:.6f}
  a1 = {a1_factory:.6f}
  a2 = {a2_factory:.6f}
  a3 = {a3_factory:.6f}

Comment:
- Taken from ImpulseQt calibration screen (e.g. Cs-137 check).
- Represents instrument baseline energy scale prior to airborne survey.

[Best-fit survey calibration]
Source: Fitted from aggregated airborne spectra
Equation: E = b0 + b1 * ch + b2 * ch^2 + b3 * ch^3
Coefficients:
  b0 = {b0_best:.6f}
  b1 = {b1_best:.6f}
  b2 = {b2_best:.6f}
  b3 = {b3_best:.6f}

Comment:
- Derived using natural background peaks (K-40, Cs-137, Tl-208, etc.).
- Minimizes RMS error across reference energies; recommended for project analyses.

[Comparison]
- Slope difference (b1 - a1): {slope_diff:.6f} keV/channel.
- Relative slope change: {slope_rel:.2f}%.
- Use best-fit coefficients for energy binning and REE mapping; use factory
  coefficients for reproducing original ImpulseQt displays or tracking long-term
  instrument stability.
"""


def write_calibration_metadata(
    output_dir: Path,
    project_name: str,
    header: SpectrogramHeader,
    factory_coeffs: List[float],
    best_coeffs: List[float],
    best_summary: str,
) -> Path:
    """Write calibration metadata (factory + best-fit) to a separate text file."""

    if len(factory_coeffs) < 4:
        factory_coeffs = factory_coeffs + [0.0] * (4 - len(factory_coeffs))
    factory_coeffs = factory_coeffs[:4]

    if len(best_coeffs) < 4:
        best_coeffs = best_coeffs + [0.0] * (4 - len(best_coeffs))
    best_coeffs = best_coeffs[:4]

    a0_f, a1_f, a2_f, a3_f = factory_coeffs
    b0_b, b1_b, b2_b, b3_b = best_coeffs

    slope_diff = b1_b - a1_f
    slope_rel = (slope_diff / a1_f * 100.0) if a1_f != 0.0 else 0.0

    text = CALIBRATION_TEXT_TEMPLATE.format(
        project_name=project_name,
        detector=header.device,
        software="ImpulseQt / GammaSpectacular",
        a0_factory=a0_f, a1_factory=a1_f, a2_factory=a2_f, a3_factory=a3_f,
        b0_best=b0_b, b1_best=b1_b, b2_best=b2_b, b3_best=b3_b,
        slope_diff=slope_diff, slope_rel=slope_rel,
    )

    text += "\nBest-fit summary:\n" + "\n".join(textwrap.wrap(best_summary, width=80)) + "\n"

    output_dir.mkdir(parents=True, exist_ok=True)
    calib_path = output_dir / f"{project_name}_calibration.txt"
    calib_path.write_text(text, encoding="utf-8")
    return calib_path


def write_run_summary(
    output_dir: Path,
    project_name: str,
    header: SpectrogramHeader,
    n_spectra: int,
    n_flight_records: int,
    n_matched: int,
    tolerance_seconds: float,
    factory_coeffs: List[float],
    best_coeffs: List[float],
) -> Path:
    """Write a machine-readable JSON summary of the run."""

    summary = {
        "project_name": project_name,
        "detector": header.device,
        "description": header.description,
        "format_version": header.format_version,
        "n_channels": header.n_channels,
        "survey_start_local": header.start_local_dt.isoformat(),
        "counts_total": header.counts_total,
        "cps": header.cps,
        "integration_time_s": header.integration_time_s,
        "n_spectra": int(n_spectra),
        "n_flight_records": int(n_flight_records),
        "n_matched": int(n_matched),
        "match_rate": round(n_matched / n_spectra, 4) if n_spectra else 0.0,
        "time_tolerance_seconds": tolerance_seconds,
        "factory_calibration": {"a0": factory_coeffs[0], "a1": factory_coeffs[1],
                                 "a2": factory_coeffs[2], "a3": factory_coeffs[3]},
        "best_fit_calibration": {"b0": best_coeffs[0], "b1": best_coeffs[1],
                                  "b2": best_coeffs[2], "b3": best_coeffs[3]},
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    summary_path = output_dir / f"{project_name}_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Join gamma spectrogram (FORMAT 3) with Airdata flight log and "
            "produce a joined CSV plus calibration metadata (factory + best-fit)."
        )
    )
    parser.add_argument("--spectrogram", type=str, required=True,
                        help="Path to spectrogram text file in FORMAT 3.")
    parser.add_argument("--flightlog", type=str, required=True,
                        help="Path to Airdata flight log CSV file.")
    parser.add_argument("--output-csv", type=str, default="joined_gamma_flight.csv",
                        help="Output CSV filename (default: joined_gamma_flight.csv).")
    parser.add_argument("--project-name", type=str, default="project",
                        help="Short name for the project (used in output filenames).")
    parser.add_argument("--time-tolerance", type=float, default=1.0,
                        help="Max time difference (seconds) for matching (default: 1).")
    parser.add_argument("--output-dir", type=str, default=".",
                        help="Directory for output files.")
    parser.add_argument("--factory-a0", type=float, default=0.0, help="Factory offset a0 (keV).")
    parser.add_argument("--factory-a1", type=float, default=0.739863,
                        help="Factory slope a1 (keV/channel), e.g. from ImpulseQt.")
    parser.add_argument("--factory-a2", type=float, default=0.0, help="Factory quadratic a2.")
    parser.add_argument("--factory-a3", type=float, default=0.0, help="Factory cubic a3.")
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    spectrogram_path = Path(args.spectrogram).expanduser().resolve()
    flightlog_path = Path(args.flightlog).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_csv_path = output_dir / args.output_csv

    print(f"[INFO] Spectrogram file: {spectrogram_path}")
    print(f"[INFO] Flight log file:  {flightlog_path}")
    print(f"[INFO] Output directory: {output_dir}")

    header, records = parse_spectrogram(spectrogram_path)
    print(
        f"[INFO] Parsed spectrogram header: format={header.format_version}, "
        f"start_local={header.start_local_dt.isoformat()}, "
        f"counts_total={header.counts_total}, cps={header.cps:.3f}, "
        f"n_channels={header.n_channels}"
    )
    print(f"[INFO] Parsed {len(records)} spectra (Base + {max(0, len(records) - 1)} delta spectra).")

    gamma_df = records_to_dataframe(header, records)

    channel_cols = [c for c in gamma_df.columns if c.startswith("ch_")]
    channel_axis = np.arange(header.n_channels, dtype=float)
    aggregated_counts = gamma_df[channel_cols].to_numpy().sum(axis=0)

    factory_coeffs = [args.factory_a0, args.factory_a1, args.factory_a2, args.factory_a3]
    best_coeffs, best_summary = fit_best_calibration(factory_coeffs, channel_axis, aggregated_counts)
    print(f"[INFO] {best_summary}")

    flight_df = parse_flight_log(flightlog_path)
    print(f"[INFO] Flight log records: {len(flight_df)}")

    joined_df = join_gamma_with_flight(gamma_df, flight_df, tolerance_seconds=args.time_tolerance)

    cols_to_keep = set(ESSENTIAL_COLUMNS)
    cols_to_keep.update([
        "gamma_datetime_utc", "gamma_timestamp_ms", "gamma_lat_phone",
        "gamma_lon_phone", "gamma_duration_s", "gamma_counts_total",
        "gamma_cps", "gamma_integration_time_s", "gamma_base_duration_s",
        "gamma_alt_phone", "spectrum_type",
    ])

    channel_cols = [c for c in joined_df.columns if c.startswith("ch_")]
    cols_to_keep.update(channel_cols)

    missing = [c for c in ESSENTIAL_COLUMNS if c not in joined_df.columns]
    if missing:
        print(f"[WARN] Missing expected flight log columns in output: {missing}")

    ordered_cols = [c for c in joined_df.columns if c in cols_to_keep]
    output_df = joined_df[ordered_cols].copy()

    calib_profile_name = f"{args.project_name}_calibration.txt"
    output_df["calibration_profile"] = calib_profile_name

    output_dir.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(output_csv_path, index=False)
    print(f"[INFO] Wrote joined CSV: {output_csv_path}")

    calib_path = write_calibration_metadata(
        output_dir=output_dir,
        project_name=args.project_name,
        header=header,
        factory_coeffs=factory_coeffs,
        best_coeffs=best_coeffs,
        best_summary=best_summary,
    )
    print(f"[INFO] Wrote calibration metadata: {calib_path}")

    matched = int(output_df["datetime_utc"].notna().sum()) if "datetime_utc" in output_df.columns else 0

    summary_path = write_run_summary(
        output_dir=output_dir,
        project_name=args.project_name,
        header=header,
        n_spectra=len(output_df),
        n_flight_records=len(flight_df),
        n_matched=matched,
        tolerance_seconds=args.time_tolerance,
        factory_coeffs=factory_coeffs[:4],
        best_coeffs=(best_coeffs + [0.0] * 4)[:4],
    )
    print(f"[INFO] Wrote run summary: {summary_path}")
    print(f"[INFO] Spectra matched to flight log within {args.time_tolerance:.1f}s: {matched}/{len(output_df)}")


if __name__ == "__main__":
    main()
