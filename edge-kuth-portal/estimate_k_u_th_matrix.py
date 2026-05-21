#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Estimate K (%), U (ppm), Th (ppm) for each .spc using PAD spectra and full 3x3 PAD composition matrix.

- Energy calibrated with a quadratic (Geomon anchors).
- Features = ROI sums around key lines (K-40, U-chain, Th-chain).
- Fit y ≈ M_ref @ w to get PAD weights w≥0.
- Convert PAD weights to concentrations with c = C @ w, where C is 3x3 PAD composition matrix:
  rows = [K, U, Th], cols = [PAD_K_A, PAD_U_A, PAD_Th_A].

Usage:
    # Interactive mode (default):
    python estimate_k_u_th_matrix.py

    # CLI mode:
    python estimate_k_u_th_matrix.py --spectra-dir /path/to/spc/files \\
        --pad-dir /path/to/pad/files --output results.csv

    # CLI with options:
    python estimate_k_u_th_matrix.py --spectra-dir /input --pad-dir /pads \\
        --output /out/results.csv --roi-half-width 25 --normalize-live-time
"""

import sys
import argparse
from pathlib import Path
import csv
import numpy as np

__version__ = "2.0.0"

# ====== Energy calibration anchors ======
ANCHORS_CH = np.array([870.5, 720.8, 31.6, 484.0], dtype=float)
ANCHORS_KEV = np.array([2611.4, 2162.3, 94.8, 1451.9], dtype=float)

# ====== Reference lines for features (keV) ======
REF_LINES = {
    "K": [1460.8],
    "U": [351.9, 609.3, 1120.3, 1764.5],
    "Th": [583.2, 911.1, 968.9, 2614.5],
}
ROI_HALF_WIDTH_KEV = 20.0  # default ±20 keV around each line

# ====== Hard-coded 3x3 PAD composition matrix ======
# Rows: [K(%), U(ppm), Th(ppm)] ; Columns: [PAD_K_A, PAD_U_A, PAD_Th_A]
C_PAD = np.array([
    [6.85, 1.17, 0.98],     # K (%)
    [1.38, 40.87, 1.90],    # U (ppm)
    [2.54, 4.42, 111.59],   # Th (ppm)
], dtype=float)

PAD_FILENAMES = ["PAD_K_A.spc", "PAD_U_A.spc", "PAD_Th_A.spc"]


def first_numeric_token_or_none(line: str):
    """Extract the first numeric token from a string."""
    for tok in line.strip().split():
        try:
            return float(tok)
        except ValueError:
            continue
    return None


def parse_spc_metadata(all_lines: list, header_lines: int = 2, n_channels: int = 1024):
    """
    Parse location and elevation metadata from lines after the 1024 channel counts.

    Typical trailing lines in a .spc file:
        line[header_lines + n_channels + 0]: "10.72 0 3 0"   (processing metadata)
        line[header_lines + n_channels + 1]: "53.2506660000"  (latitude)
        line[header_lines + n_channels + 2]: "-9.5073843000" (longitude)
        line[header_lines + n_channels + 3]: "84"             (elevation)
        line[header_lines + n_channels + 4]: "7 0:0:0"       (time)

    Returns dict with lat, lon, elevation (or None if not found).
    """
    meta = {"lat": None, "lon": None, "elevation": None}
    meta_start = header_lines + n_channels
    if len(all_lines) <= meta_start:
        return meta  # No metadata lines

    trailing = all_lines[meta_start:]
    # Find numeric values in trailing lines
    numeric_values = []
    for line in trailing:
        for tok in line.strip().split():
            try:
                numeric_values.append(float(tok))
            except ValueError:
                continue

    # Expect pattern: 4 metadata numbers, then lat, lon, elevation
    # After the 4 processing numbers, look for latitude/mid-range, longitude/negative, elevation/positive
    if len(numeric_values) >= 7:
        meta["lat"] = numeric_values[4]
        meta["lon"] = numeric_values[5]
        meta["elevation"] = int(numeric_values[6]) if numeric_values[6] == int(numeric_values[6]) else numeric_values[6]
    elif len(numeric_values) >= 5:
        meta["lat"] = numeric_values[3]
        meta["lon"] = numeric_values[4]

    return meta


def read_spc_counts_and_times(path: Path, header_lines: int = 2, n_channels: int = 1024):
    """
    Read a .spc file and return (counts_array, live_time_us, metadata).

    Format:
        Line 1: live time (microseconds)
        Line 2: clock time (microseconds)
        Lines 3..1026: count values (one per channel)
        Lines 1027+: optional metadata (lat, lon, elevation, etc.)

    Returns
    -------
    counts : np.ndarray
        1024 channel counts
    live_time_us : float or None
        Live time in microseconds
    metadata : dict
        Parsed trailing metadata with keys: lat, lon, elevation
    """
    if not path.exists():
        raise FileNotFoundError(f"SPC not found: {path}")
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        lines = [ln.rstrip("\n") for ln in f]
    if len(lines) < header_lines + n_channels:
        raise RuntimeError(
            f"SPC too short: {len(lines)} lines; need at least {header_lines + n_channels}."
        )
    live_time_us = first_numeric_token_or_none(lines[0])
    data_block = lines[header_lines: header_lines + n_channels]
    counts = []
    for raw in data_block:
        val = first_numeric_token_or_none(raw)
        counts.append(val if val is not None else 0.0)
    metadata = parse_spc_metadata(lines, header_lines, n_channels)
    return np.array(counts, dtype=float), live_time_us, metadata


def calibrate_energy_quadratic(ch: np.ndarray, anchors_ch: np.ndarray, anchors_keV: np.ndarray):
    """Quadratic energy calibration: E(ch) = c0 + c1*ch + c2*ch^2."""
    A = np.vstack([np.ones_like(anchors_ch), anchors_ch, anchors_ch**2]).T
    coeffs = np.linalg.lstsq(A, anchors_keV, rcond=None)[0]
    E = coeffs[0] + coeffs[1] * ch + coeffs[2] * (ch**2)
    return coeffs, E


def integrate_rois(energy_keV: np.ndarray, counts: np.ndarray, roi_lines: list, half_width_keV: float):
    """Sum counts within ±half_width_keV of each reference line."""
    feats = []
    for E0 in roi_lines:
        mask = (energy_keV >= (E0 - half_width_keV)) & (energy_keV <= (E0 + half_width_keV))
        feats.append(counts[mask].sum())
    return np.array(feats, dtype=float)


def build_feature_vector(energy_keV: np.ndarray, counts: np.ndarray, half_width_keV: float):
    """Concatenate ROI sums across all element lines -> length-9 feature vector."""
    fK = integrate_rois(energy_keV, counts, REF_LINES["K"], half_width_keV)
    fU = integrate_rois(energy_keV, counts, REF_LINES["U"], half_width_keV)
    fTh = integrate_rois(energy_keV, counts, REF_LINES["Th"], half_width_keV)
    return np.concatenate([fK, fU, fTh], axis=0)  # shape (9,)


def fit_pad_weights(y_feats: np.ndarray, M_ref: np.ndarray):
    """Solve y ≈ M_ref @ w, clip w >= 0, return (w, r2)."""
    w_hat, _, _, _ = np.linalg.lstsq(M_ref, y_feats, rcond=None)
    w_hat = np.maximum(w_hat, 0.0)
    y_pred = M_ref @ w_hat
    ss_res = np.sum((y_feats - y_pred)**2)
    ss_tot = np.sum((y_feats - np.mean(y_feats))**2) if np.any(y_feats) else 0.0
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 1.0
    return w_hat, r2


def load_pad_spectra(pad_dir: Path, normalize_live_time: bool = False):
    """
    Load all three PAD spectra from a directory.

    Returns dict mapping 'K'/'U'/'Th' to count arrays (optionally rate-normalized).
    """
    elements = ['K', 'U', 'Th']
    pad_counts = {}
    for elem, fname in zip(elements, PAD_FILENAMES):
        counts, live_us, _ = read_spc_counts_and_times(pad_dir / fname)
        if normalize_live_time and live_us and live_us > 0:
            counts = counts / (live_us * 1e-6)  # counts per second
        pad_counts[elem] = counts
    return pad_counts


def build_reference_matrix(energy_keV: np.ndarray, pad_counts: dict, half_width_keV: float):
    """Build the 9x3 reference feature matrix from PAD spectra."""
    fK = build_feature_vector(energy_keV, pad_counts['K'], half_width_keV)
    fU = build_feature_vector(energy_keV, pad_counts['U'], half_width_keV)
    fTh = build_feature_vector(energy_keV, pad_counts['Th'], half_width_keV)
    return np.stack([fK, fU, fTh], axis=1)  # shape (9, 3)


def process_spectrum(
    counts: np.ndarray,
    energy_keV: np.ndarray,
    M_ref: np.ndarray,
    half_width_keV: float = ROI_HALF_WIDTH_KEV,
    normalize_live_time: bool = False,
    live_time_us: float = None,
    lat: float = None,
    lon: float = None,
    elevation: float = None,
):
    """
    Process a single spectrum and return K/U/Th results with location metadata.

    Parameters
    ----------
    counts : np.ndarray
        Raw count data (1024 channels).
    energy_keV : np.ndarray
        Energy calibration (1024 values in keV).
    M_ref : np.ndarray
        9x3 reference feature matrix.
    half_width_keV : float
        ROI half-width around reference lines.
    normalize_live_time : bool
        If True, divide counts by live time (seconds).
    live_time_us : float, optional
        Live time in microseconds (required if normalize_live_time=True).
    lat : float, optional
        Latitude from spectrum metadata.
    lon : float, optional
        Longitude from spectrum metadata.
    elevation : float, optional
        Elevation from spectrum metadata.

    Returns
    -------
    dict with keys: K_percent, U_ppm, Th_ppm, w_PADK, w_PADU, w_PADTh, fit_r2, lat, lon, elevation
    """
    if normalize_live_time and live_time_us and live_time_us > 0:
        counts = counts / (live_time_us * 1e-6)

    y_feats = build_feature_vector(energy_keV, counts, half_width_keV)
    w_hat, r2 = fit_pad_weights(y_feats, M_ref)

    # Concentrations via c = C_PAD @ w
    c = C_PAD @ w_hat
    K_percent, U_ppm, Th_ppm = c.tolist()

    return {
        "K_percent": float(K_percent),
        "U_ppm": float(U_ppm),
        "Th_ppm": float(Th_ppm),
        "w_PADK": float(w_hat[0]),
        "w_PADU": float(w_hat[1]),
        "w_PADTh": float(w_hat[2]),
        "fit_r2": float(r2),
        "lat": lat,
        "lon": lon,
        "elevation": elevation,
    }


def process_batch(
    spectra_dir: Path,
    pad_dir: Path,
    output_path: Path,
    half_width_keV: float = ROI_HALF_WIDTH_KEV,
    normalize_live_time: bool = False,
    verbose: bool = True,
):
    """
    Process all .spc files in a directory and save results to CSV.

    Returns list of result dicts.
    """
    # Channels & energy calibration (common for all files)
    n_channels = 1024
    channels = np.arange(n_channels, dtype=float)
    _, energy_keV = calibrate_energy_quadratic(channels, ANCHORS_CH, ANCHORS_KEV)

    # Load PAD spectra and build reference matrix
    if verbose:
        print("Loading PAD reference spectra...")
    pad_counts = load_pad_spectra(pad_dir, normalize_live_time)
    M_ref = build_reference_matrix(energy_keV, pad_counts, half_width_keV)

    # Find .spc files
    spc_files = sorted(spectra_dir.glob("*.spc"))
    if not spc_files:
        print(f"[WARN] No .spc files found in: {spectra_dir}")
        return []

    if verbose:
        print(f"Found {len(spc_files)} .spc files to process")

    results = []
    for i, spc in enumerate(spc_files, 1):
        try:
            counts, live_us, metadata = read_spc_counts_and_times(spc)
            result = process_spectrum(
                counts, energy_keV, M_ref,
                half_width_keV=half_width_keV,
                normalize_live_time=normalize_live_time,
                live_time_us=live_us,
                lat=metadata.get("lat"),
                lon=metadata.get("lon"),
                elevation=metadata.get("elevation"),
            )
            result["file"] = spc.name
            results.append(result)

            if verbose:
                loc = ""
                if metadata["lat"] is not None and metadata["lon"] is not None:
                    loc = f"  [{metadata['lat']:.4f}, {metadata['lon']:.4f}]"
                elev = f"  elev={int(metadata['elevation'])}m" if metadata["elevation"] is not None else ""
                print(
                    f"  [{i}/{len(spc_files)}] {spc.name}: "
                    f"K={result['K_percent']:.3f}%  "
                    f"U={result['U_ppm']:.3f} ppm  "
                    f"Th={result['Th_ppm']:.3f} ppm  "
                    f"(R^2={result['fit_r2']:.3f}){loc}{elev}"
                )
        except Exception as e:
            print(f"  [ERR] {spc.name} -> {e}")

    # Determine CSV columns based on whether location data is available
    has_location = any(r["lat"] is not None for r in results)
    has_elevation = any(r["elevation"] is not None for r in results)

    # Write CSV
    with output_path.open("w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        csv_cols = ["file"]
        if has_location:
            csv_cols += ["lat", "lon"]
        if has_elevation:
            csv_cols.append("elevation")
        csv_cols += ["K_percent", "U_ppm", "Th_ppm", "w_PADK", "w_PADU", "w_PADTh", "fit_r2"]
        writer.writerow(csv_cols)
        for r in results:
            row = [r["file"]]
            if has_location:
                row.append(f"{r['lat']:.7f}" if r["lat"] is not None else "")
                row.append(f"{r['lon']:.7f}" if r["lon"] is not None else "")
            if has_elevation:
                row.append(str(int(r["elevation"])) if r["elevation"] is not None else "")
            row += [
                f"{r['K_percent']:.3f}",
                f"{r['U_ppm']:.3f}",
                f"{r['Th_ppm']:.3f}",
                f"{r['w_PADK']:.4f}",
                f"{r['w_PADU']:.4f}",
                f"{r['w_PADTh']:.4f}",
                f"{r['fit_r2']:.4f}",
            ]
            writer.writerow(row)

    if verbose:
        print(f"\nResults saved to: {output_path}")
        print(f"Processed {len(results)} files successfully.")

    return results


def interactive_mode():
    """Run interactively, prompting the user for paths."""
    print("=" * 60)
    print("K/U/Th Estimation Tool v" + __version__)
    print("=" * 60)
    print()

    # Get spectra directory
    while True:
        raw = input("Folder with input .spc spectra: ").strip()
        spectra_dir = Path(raw)
        if spectra_dir.exists() and spectra_dir.is_dir():
            break
        print(f"Error: Directory not found: {raw}\n")

    # Get PAD directory
    while True:
        raw = input("Folder with PAD spectra files (PAD_K_A.spc, etc.): ").strip()
        pad_dir = Path(raw)
        if pad_dir.exists() and pad_dir.is_dir():
            missing = [f for f in PAD_FILENAMES if not (pad_dir / f).exists()]
            if not missing:
                break
            print(f"Warning: Missing PAD files: {', '.join(missing)}")
            cont = input("Continue anyway? (y/N): ").strip().lower()
            if cont in ('y', 'yes'):
                break
            print()
        else:
            print(f"Error: Directory not found: {raw}\n")

    # Output path
    while True:
        raw = input("Output CSV file path: ").strip()
        out = Path(raw)
        if out.parent.exists() or out.parent == Path("."):
            break
        print(f"Error: Parent directory does not exist: {out.parent}\n")

    # ROI half-width
    raw = input(f"ROI half width (keV) [{ROI_HALF_WIDTH_KEV}]: ").strip()
    hw = float(raw) if raw else ROI_HALF_WIDTH_KEV

    # Normalize
    raw = input("Normalize counts by live time? (y/N): ").strip().lower()
    normalize = raw in ('y', 'yes')

    print()
    print("Processing...\n")
    process_batch(spectra_dir, pad_dir, out, half_width_keV=hw, normalize_live_time=normalize)


def parse_args(argv=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="K/U/Th Estimation from gamma-ray .spc spectra",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python estimate_k_u_th_matrix.py --spectra-dir ./spectra --pad-dir ./pads --output results.csv
  python estimate_k_u_th_matrix.py -s ./data -p ./ref -o out.csv --roi-half-width 25 --normalize
        """,
    )
    parser.add_argument("--spectra-dir", "-s", help="Directory containing .spc files to analyze")
    parser.add_argument("--pad-dir", "-p", help="Directory containing PAD reference spectra")
    parser.add_argument("--output", "-o", help="Output CSV file path")
    parser.add_argument("--roi-half-width", type=float, default=ROI_HALF_WIDTH_KEV,
                        help=f"ROI half-width around reference lines in keV (default: {ROI_HALF_WIDTH_KEV})")
    parser.add_argument("--normalize-live-time", "-n", action="store_true",
                        help="Normalize counts by live time (counts per second)")
    parser.add_argument("--version", "-v", action="version", version=f"%(prog)s {__version__}")
    return parser.parse_args(argv)


def main():
    args = parse_args()

    # If all required CLI args provided, run in batch mode
    if args.spectra_dir and args.pad_dir and args.output:
        spectra_dir = Path(args.spectra_dir)
        pad_dir = Path(args.pad_dir)
        output_path = Path(args.output)

        if not spectra_dir.exists():
            print(f"Error: Spectra directory not found: {spectra_dir}", file=sys.stderr)
            sys.exit(1)
        if not pad_dir.exists():
            print(f"Error: PAD directory not found: {pad_dir}", file=sys.stderr)
            sys.exit(1)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        process_batch(
            spectra_dir, pad_dir, output_path,
            half_width_keV=args.roi_half_width,
            normalize_live_time=args.normalize_live_time,
        )
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
