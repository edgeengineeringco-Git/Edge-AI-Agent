# -*- coding: utf-8 -*-
"""
Estimate K (%), U (ppm), Th (ppm) for each .spc using PAD spectra and full 3x3 PAD composition matrix.

Energy calibrated with a quadratic (Geomon anchors).
Features = ROI sums around key lines (K-40, U-chain, Th-chain).
Fit y ≈ M_ref @ w to get PAD weights w >= 0.
Convert PAD weights to concentrations with c = C @ w.

Preprocessing modes (mutually exclusive, default = raw):
    --normalize-live-time    Divide counts by live time (counts/s)
    --normalize-total-counts Rescale each spectrum to 100000 total counts

Continuum subtraction (independent of normalization mode):
    --subtract-continuum     Subtract linear continuum from each ROI using shoulder windows

Usage:
    python estimate_k_u_th_matrix.py --spectra <dir> --pad-dir <dir> --out <csv>
    python estimate_k_u_th_matrix.py --spectra <dir> --pad-dir <dir> --out <csv> --normalize-live-time
    python estimate_k_u_th_matrix.py --spectra <dir> --pad-dir <dir> --out <csv> --normalize-total-counts --subtract-continuum
"""

import argparse
import csv
import json
import sys
import traceback
from pathlib import Path

import numpy as np


# =============================================================================
# Constants
# =============================================================================

ENGINE_VERSION = "2.0.0"

# Energy calibration anchors (Geomon, validated)
ANCHORS_CH = np.array([870.5, 720.8, 31.6, 484.0], dtype=float)
ANCHORS_KEV = np.array([2611.4, 2162.3, 94.8, 1451.9], dtype=float)

# Reference lines for ROI features (keV)
REF_LINES = {
    "K":  [1460.8],
    "U":  [351.9, 609.3, 1120.3, 1764.5],
    "Th": [583.2, 911.1, 968.9, 2614.5],
}

# Feature labels in output order
FEATURE_LABELS = [
    "K_1460", "U_351", "U_609", "U_1120", "U_1764",
    "Th_583", "Th_911", "Th_968", "Th_2614",
]

# PAD composition matrix: rows=[K%, Uppm, Thppm], cols=[PAD_K, PAD_U, PAD_Th]
C_PAD = np.array([
    [6.85, 1.17, 0.98],
    [1.38, 40.87, 1.90],
    [2.54, 4.42, 111.59],
], dtype=float)

PAD_FILENAMES = ["PAD_K_A.spc", "PAD_U_A.spc", "PAD_Th_A.spc"]
PAD_LABELS = ["PAD_K_A", "PAD_U_A", "PAD_Th_A"]

TARGET_TOTAL_COUNTS = 100000.0

# SPC file format
HEADER_LINES = 2
N_CHANNELS = 1024


# =============================================================================
# SPC I/O
# =============================================================================

def first_numeric_token_or_none(line: str):
    """Return the first numeric token in line, or None."""
    for tok in line.strip().split():
        try:
            return float(tok)
        except ValueError:
            continue
    return None


def read_spc(path: Path):
    """Read a .spc file.

    Returns:
        counts: ndarray of shape (N_CHANNELS,) — channel counts
        live_time_us: float or None — live time in microseconds
        clock_time_us: float or None — clock time in microseconds

    Raises:
        FileNotFoundError, RuntimeError on bad format.
    """
    if not path.exists():
        raise FileNotFoundError(f"SPC not found: {path}")

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        lines = [ln.rstrip("\n") for ln in f]

    if len(lines) < HEADER_LINES + N_CHANNELS:
        raise RuntimeError(
            f"SPC too short: {len(lines)} lines; "
            f"need at least {HEADER_LINES + N_CHANNELS}"
        )

    live_time_us = first_numeric_token_or_none(lines[0])
    clock_time_us = first_numeric_token_or_none(lines[1])

    counts = np.zeros(N_CHANNELS, dtype=float)
    for i in range(N_CHANNELS):
        val = first_numeric_token_or_none(lines[HEADER_LINES + i])
        if val is not None:
            counts[i] = val

    return counts, live_time_us, clock_time_us


# =============================================================================
# Preprocessing — one function, explicit modes, no hidden behaviour
# =============================================================================

def preprocess(counts: np.ndarray, live_time_us, clock_time_us, mode: str):
    """Apply the selected preprocessing mode to a spectrum.

    Modes:
        raw          — no transformation, return copy of raw counts
        live_time    — divide counts by live time (counts per second)
        total_counts — rescale so that sum(counts) == TARGET_TOTAL_COUNTS

    Returns:
        Processed counts array (same shape as input).

    Raises:
        ValueError if mode-specific requirements are not met
        (e.g. live time missing for live_time mode, zero total for total_counts mode).
    """
    if mode == "raw":
        return counts.copy()

    if mode == "live_time":
        if live_time_us is None or live_time_us <= 0:
            raise ValueError(
                f"Live-time normalization requested but live time "
                f"is unavailable or invalid ({live_time_us})"
            )
        return counts / (live_time_us * 1e-6)  # counts per second

    if mode == "total_counts":
        total = counts.sum()
        if total <= 0:
            raise ValueError(
                f"Total-count normalization requested but spectrum "
                f"has zero or negative total counts ({total})"
            )
        return counts * (TARGET_TOTAL_COUNTS / total)

    raise ValueError(f"Unknown preprocessing mode: {mode!r}")


# =============================================================================
# Energy calibration
# =============================================================================

def calibrate_energy_quadratic(channels, anchors_ch, anchors_keV):
    """Fit quadratic energy calibration: E = c0 + c1*ch + c2*ch^2.

    Returns:
        (c0, c1, c2): tuple of coefficients
        energy_keV: ndarray of calibrated energies per channel
    """
    A = np.vstack([np.ones_like(anchors_ch), anchors_ch, anchors_ch**2]).T
    c0, c1, c2 = np.linalg.lstsq(A, anchors_keV, rcond=None)[0]
    energy_keV = c0 + c1 * channels + c2 * channels**2
    return (c0, c1, c2), energy_keV


# =============================================================================
# ROI integration
# =============================================================================

def integrate_rois(energy_keV, counts, roi_lines, half_width_keV, subtract_continuum=False):
    """Sum counts in ROI windows around each reference line.

    When subtract_continuum is True, a linear continuum is estimated from
    shoulder windows (one half-width on each side of the ROI) and subtracted
    from the gross sum. Applied identically to PAD and sample spectra.

    Returns:
        ndarray of ROI sums in the order of roi_lines.
    """
    features = []
    for E0 in roi_lines:
        mask = (energy_keV >= (E0 - half_width_keV)) & (energy_keV <= (E0 + half_width_keV))
        gross = counts[mask].sum()
        n_roi = mask.sum()

        if subtract_continuum and n_roi > 0:
            # Shoulder windows: one half-width on each side of the ROI
            left_mask = (energy_keV >= (E0 - 2 * half_width_keV)) & (energy_keV < (E0 - half_width_keV))
            right_mask = (energy_keV > (E0 + half_width_keV)) & (energy_keV <= (E0 + 2 * half_width_keV))
            left_mean = counts[left_mask].mean() if left_mask.any() else 0.0
            right_mean = counts[right_mask].mean() if right_mask.any() else 0.0
            continuum_per_ch = (left_mean + right_mean) / 2.0
            gross -= continuum_per_ch * n_roi

        features.append(gross)
    return np.array(features, dtype=float)


def build_feature_vector(energy_keV, counts, half_width_keV, subtract_continuum=False):
    """Build the 9-element feature vector from a spectrum.

    Order: [K1, U1, U2, U3, U4, Th1, Th2, Th3, Th4]
    """
    fK = integrate_rois(energy_keV, counts, REF_LINES["K"], half_width_keV, subtract_continuum)
    fU = integrate_rois(energy_keV, counts, REF_LINES["U"], half_width_keV, subtract_continuum)
    fTh = integrate_rois(energy_keV, counts, REF_LINES["Th"], half_width_keV, subtract_continuum)
    return np.concatenate([fK, fU, fTh])  # shape (9,)


# =============================================================================
# PAD matrix construction
# =============================================================================

def build_pad_matrix(pad_dir: Path, energy_keV, half_width_keV, mode: str, subtract_continuum: bool = False):
    """Read PAD spectra, preprocess, and build the 9x3 reference matrix.

    Returns:
        M_ref: ndarray of shape (9, 3) — columns are PAD_K, PAD_U, PAD_Th
        pad_info: list of dicts with per-PAD metadata for the debug log
    """
    M_cols = []
    pad_info = []

    for filename, label in zip(PAD_FILENAMES, PAD_LABELS):
        path = pad_dir / filename
        counts, live_us, clock_us = read_spc(path)
        processed = preprocess(counts, live_us, clock_us, mode)
        feats = build_feature_vector(energy_keV, processed, half_width_keV, subtract_continuum)
        M_cols.append(feats)

        pad_info.append({
            "file": filename,
            "label": label,
            "live_time_us": live_us,
            "clock_time_us": clock_us,
            "total_counts_raw": int(counts.sum()),
            "total_counts_processed": float(processed.sum()),
        })

    M_ref = np.column_stack(M_cols)  # shape (9, 3)
    return M_ref, pad_info


# =============================================================================
# Fitting
# =============================================================================

def fit_pad_weights(y_feats, M_ref):
    """Solve y ≈ M_ref @ w, clip w >= 0, compute R².

    Returns:
        w: ndarray of shape (3,) — non-negative PAD weights
        r2: float — coefficient of determination
    """
    w, _, _, _ = np.linalg.lstsq(M_ref, y_feats, rcond=None)
    w = np.maximum(w, 0.0)
    y_pred = M_ref @ w
    ss_res = np.sum((y_feats - y_pred) ** 2)
    ss_tot = np.sum((y_feats - np.mean(y_feats)) ** 2)
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 1.0
    return w, r2


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Estimate K/U/Th using PAD spectra and full 3x3 PAD composition matrix."
    )
    parser.add_argument("--spectra", required=True,
                        help="Folder with input .spc spectra files.")
    parser.add_argument("--pad-dir", required=True,
                        help="Folder with PAD_K_A.spc, PAD_U_A.spc, PAD_Th_A.spc.")
    parser.add_argument("--out", required=True,
                        help="Output CSV path.")
    parser.add_argument("--roi-half-width-kev", type=float, default=20.0,
                        help="ROI half-width around reference lines in keV (default: 20).")

    # Mutually exclusive — argparse raises an error if both are passed.
    norm_group = parser.add_mutually_exclusive_group()
    norm_group.add_argument("--normalize-live-time", action="store_true",
                            help="Divide counts by live time (counts/s).")
    norm_group.add_argument("--normalize-total-counts", action="store_true",
                            help="Rescale each spectrum to 100000 total counts.")

    # Continuum subtraction (independent of normalization mode)
    parser.add_argument("--subtract-continuum", action="store_true",
                        help="Subtract linear continuum from each ROI using shoulder windows "
                             "(applied after normalization, before ROI integration).")

    args = parser.parse_args()

    # ------------------------------------------------------------------
    # Determine preprocessing mode
    # ------------------------------------------------------------------
    if args.normalize_live_time:
        mode = "live_time"
    elif args.normalize_total_counts:
        mode = "total_counts"
    else:
        mode = "raw"

    mode_descriptions = {
        "raw": "No preprocessing — using raw channel counts as-is",
        "live_time": "Counts divided by live time (counts/s)",
        "total_counts": f"Each spectrum rescaled to {TARGET_TOTAL_COUNTS:.0f} total counts",
    }

    spectra_dir = Path(args.spectra)
    pad_dir = Path(args.pad_dir)
    out_csv = Path(args.out)
    hw = args.roi_half_width_kev

    print(f"[MODE] Preprocessing: {mode}")
    print(f"[MODE] {mode_descriptions[mode]}")
    print(f"[MODE] Continuum subtraction: {'yes' if args.subtract_continuum else 'no'}")
    print(f"[MODE] ROI half-width: {hw} keV")
    print(f"[MODE] Spectra: {spectra_dir}")
    print(f"[MODE] PAD dir: {pad_dir}")
    print()

    # ------------------------------------------------------------------
    # Energy calibration
    # ------------------------------------------------------------------
    channels = np.arange(N_CHANNELS, dtype=float)
    (c0, c1, c2), energy_keV = calibrate_energy_quadratic(
        channels, ANCHORS_CH, ANCHORS_KEV
    )

    print(f"[CAL] E = {c0:.4f} + {c1:.4f}*ch + {c2:.6f}*ch^2")
    print(f"[CAL] Energy range: {energy_keV[0]:.1f} – {energy_keV[-1]:.1f} keV")
    print()

    # ------------------------------------------------------------------
    # Build PAD reference matrix
    # ------------------------------------------------------------------
    print("[PAD] Building reference matrix...")
    try:
        M_ref, pad_info = build_pad_matrix(pad_dir, energy_keV, hw, mode, args.subtract_continuum)
    except Exception as e:
        print(f"[PAD] FATAL: Could not build PAD matrix: {e}")
        sys.exit(1)

    for info in pad_info:
        print(f"  {info['file']}: "
              f"raw_counts={info['total_counts_raw']}, "
              f"processed_counts={info['total_counts_processed']:.1f}, "
              f"live_time_us={info['live_time_us']}")

    print(f"  M_ref shape: {M_ref.shape}")
    print()

    # ------------------------------------------------------------------
    # List .spc files
    # ------------------------------------------------------------------
    spc_files = sorted(spectra_dir.glob("*.spc"))
    if not spc_files:
        print(f"[WARN] No .spc files found in {spectra_dir}")
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["file", "mode", "live_time_us", "clock_time_us",
                             "K_percent", "U_ppm", "Th_ppm",
                             "w_PADK", "w_PADU", "w_PADTh", "fit_r2"])
        print("[WARN] Empty results CSV written (no input files)")
        return

    n_total = len(spc_files)
    n_ok = 0
    n_err = 0
    error_log = []

    # ------------------------------------------------------------------
    # Process spectra
    # ------------------------------------------------------------------
    print(f"[RUN] Processing {n_total} spectra...")
    print()

    with out_csv.open("w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["file", "mode", "live_time_us", "clock_time_us",
                         "K_percent", "U_ppm", "Th_ppm",
                         "w_PADK", "w_PADU", "w_PADTh", "fit_r2"])

        for spc in spc_files:
            try:
                counts, live_us, clock_us = read_spc(spc)
                processed = preprocess(counts, live_us, clock_us, mode)
                y_feats = build_feature_vector(energy_keV, processed, hw, args.subtract_continuum)
                w_hat, r2 = fit_pad_weights(y_feats, M_ref)

                # Concentrations via c = C_PAD @ w
                c = C_PAD @ w_hat
                K_percent, U_ppm, Th_ppm = c.tolist()

                writer.writerow([
                    spc.name,
                    mode,
                    f"{live_us:.0f}" if live_us is not None else "",
                    f"{clock_us:.0f}" if clock_us is not None else "",
                    f"{K_percent:.3f}",
                    f"{U_ppm:.3f}",
                    f"{Th_ppm:.3f}",
                    f"{w_hat[0]:.6f}",
                    f"{w_hat[1]:.6f}",
                    f"{w_hat[2]:.6f}",
                    f"{r2:.4f}",
                ])
                n_ok += 1
                if n_ok <= 5 or n_ok % 100 == 0:
                    print(f"[OK] {spc.name}: K={K_percent:.3f}%  "
                          f"U={U_ppm:.3f} ppm  Th={Th_ppm:.3f} ppm  "
                          f"(R²={r2:.4f})")

            except Exception as e:
                n_err += 1
                err_msg = f"{spc.name}: {e}"
                error_log.append(err_msg)
                print(f"[ERR] {err_msg}")
                traceback.print_exc()

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print()
    print(f"[DONE] {n_ok} OK, {n_err} errors out of {n_total} spectra")
    print(f"[CSV]  {out_csv}")

    if error_log:
        err_path = out_csv.with_suffix(".errors.txt")
        with err_path.open("w", encoding="utf-8") as f:
            f.write(f"Error log — {n_err} error(s)\n")
            f.write("=" * 50 + "\n")
            for msg in error_log:
                f.write(msg + "\n")
        print(f"[LOG]  {err_path} ({n_err} error(s) logged)")

    # ------------------------------------------------------------------
    # Processing metadata
    # ------------------------------------------------------------------
    meta = {
        "engine_version": ENGINE_VERSION,
        "preprocessing_mode": mode,
        "normalization_description": mode_descriptions[mode],
        "continuum_subtraction": args.subtract_continuum,
        "roi_half_width_kev": hw,
        "spectra_dir": str(spectra_dir),
        "pad_dir": str(pad_dir),
        "pad_files": PAD_FILENAMES,
        "calibration_coefficients": {
            "c0": round(c0, 4),
            "c1": round(c1, 4),
            "c2": round(c2, 6),
        },
        "energy_range_keV": {
            "min": round(float(energy_keV[0]), 1),
            "max": round(float(energy_keV[-1]), 1),
        },
        "total_spectra": n_total,
        "successful": n_ok,
        "errors": n_err,
        "pad_info": pad_info,
        "m_ref_shape": list(M_ref.shape),
        "target_total_counts": TARGET_TOTAL_COUNTS if mode == "total_counts" else None,
    }

    meta_path = out_csv.with_name("processing-metadata.json")
    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"[META] {meta_path}")


if __name__ == "__main__":
    main()
