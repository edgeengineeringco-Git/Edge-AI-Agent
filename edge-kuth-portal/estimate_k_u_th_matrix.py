# -*- coding: utf-8 -*-
"""
Estimate K (%), U (ppm), Th (ppm) for each .spc using PAD spectra and full 3x3 PAD composition matrix.

- Energy calibrated with a quadratic (Geomon anchors).
- Features = ROI sums around key lines (K-40, U-chain, Th-chain).
- Fit y ≈ M_ref @ w to get PAD weights w≥0.
- Convert PAD weights to concentrations with c = C @ w, where C is 3x3 PAD composition matrix:
  rows = [K, U, Th], cols = [PAD_K_A, PAD_U_A, PAD_Th_A].

Usage example:
    python estimate_k_u_th_matrix.py ^
        --spectra "E:\Calculations\Q12\spect_001021" ^
        --pad-dir "C:\\Users\\mousavim\\Desktop\\D230A\\spectra" ^
        --out "EE:\Calculations\Output" ^
        --normalize-live-time

"""

import argparse
from pathlib import Path
import csv
import numpy as np

# ====== Energy calibration anchors (your validated ones) ======
ANCHORS_CH  = np.array([870.5, 720.8,  31.6, 484.0], dtype=float)
ANCHORS_KEV = np.array([2611.4, 2162.3, 94.8, 1451.9], dtype=float)

# ====== Reference lines for features (keV) ======
REF_LINES = {
    "K":  [1460.8],
    "U":  [351.9, 609.3, 1120.3, 1764.5],
    "Th": [583.2, 911.1, 968.9, 2614.5],
}
ROI_HALF_WIDTH_KEV = 20.0  # default ±20 keV around each line

# ====== Hard-coded 3x3 PAD composition matrix (from your message) ======
# Rows: [K(%), U(ppm), Th(ppm)] ; Columns: [PAD_K_A, PAD_U_A, PAD_Th_A]
C_PAD = np.array([
    [6.85, 1.17, 0.98],     # K (%)
    [1.38, 40.87, 1.90],    # U (ppm)
    [2.54, 4.42, 111.59],   # Th (ppm)
], dtype=float)

def first_numeric_token_or_none(line: str):
    for tok in line.strip().split():
        try:
            return float(tok)
        except ValueError:
            continue
    return None

def extract_location_from_spc(path: Path):
    """Extract latitude, longitude, elevation from the 3 lines before the final line of an .spc file.

    File structure for measurement .spc files:
        lines[-4] = latitude
        lines[-3] = longitude
        lines[-2] = elevation
        lines[-1] = footer string (ignored)

    Returns:
        (lat, lon, elev) as floats, or None for any that are missing/invalid.
    """
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            lines = [ln.rstrip("\n") for ln in f]
        # Need at least header_lines + n_channels + 4 trailing lines
        if len(lines) < 1030:
            return None, None, None
        lat = first_numeric_token_or_none(lines[-4].strip())
        lon = first_numeric_token_or_none(lines[-3].strip())
        elev = first_numeric_token_or_none(lines[-2].strip())
        return lat, lon, elev
    except Exception:
        return None, None, None

def read_spc_counts_and_times(path: Path, header_lines: int = 2, n_channels: int = 1024):
    """Return counts array and live_time_us (float or None)."""
    if not path.exists():
        raise FileNotFoundError(f"SPC not found: {path}")
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        lines = [ln.rstrip("\n") for ln in f]
    if len(lines) < header_lines + n_channels:
        raise RuntimeError(f"SPC too short: {len(lines)} lines; need at least {header_lines + n_channels}.")
    live_time_us = first_numeric_token_or_none(lines[0])   # line 1: Live time (us)
    # clock_time_us = first_numeric_token_or_none(lines[1]) # line 2: Clock time (us), not used here
    data_block = lines[header_lines : header_lines + n_channels]
    counts = []
    for raw in data_block:
        val = first_numeric_token_or_none(raw)
        counts.append(val if val is not None else 0.0)
    return np.array(counts, dtype=float), live_time_us

def calibrate_energy_quadratic(ch: np.ndarray, anchors_ch: np.ndarray, anchors_keV: np.ndarray):
    A = np.vstack([np.ones_like(anchors_ch), anchors_ch, anchors_ch**2]).T
    c0, c1, c2 = np.linalg.lstsq(A, anchors_keV, rcond=None)[0]
    E = c0 + c1*ch + c2*(ch**2)
    return (c0, c1, c2), E

def integrate_rois(energy_keV: np.ndarray, counts: np.ndarray, roi_lines: list, half_width_keV: float):
    feats = []
    for E0 in roi_lines:
        mask = (energy_keV >= (E0 - half_width_keV)) & (energy_keV <= (E0 + half_width_keV))
        feats.append(counts[mask].sum())
    return np.array(feats, dtype=float)

def build_feature_vector(energy_keV: np.ndarray, counts: np.ndarray, half_width_keV: float):
    fK  = integrate_rois(energy_keV, counts, REF_LINES["K"],  half_width_keV)
    fU  = integrate_rois(energy_keV, counts, REF_LINES["U"],  half_width_keV)
    fTh = integrate_rois(energy_keV, counts, REF_LINES["Th"], half_width_keV)
    return np.concatenate([fK, fU, fTh], axis=0)  # shape = 9

def fit_pad_weights(y_feats: np.ndarray, M_ref: np.ndarray):
    """Solve y ≈ M_ref @ w, clip w>=0, return (w, r2)."""
    w_hat, _, _, _ = np.linalg.lstsq(M_ref, y_feats, rcond=None)
    w_hat = np.maximum(w_hat, 0.0)
    y_pred = M_ref @ w_hat
    ss_res = np.sum((y_feats - y_pred)**2)
    ss_tot = np.sum((y_feats - np.mean(y_feats))**2) if np.any(y_feats) else 0.0
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 1.0
    return w_hat, r2

def main():
    parser = argparse.ArgumentParser(description="Estimate K/U/Th using PAD spectra and full 3x3 PAD composition matrix.")
    parser.add_argument("--spectra", required=True, help="Folder with input .spc spectra (e.g., 'sum').")
    parser.add_argument("--pad-dir", required=True, help="Folder with PAD_K_A.spc, PAD_U_A.spc, PAD_Th_A.spc.")
    parser.add_argument("--out", required=True, help="Output CSV path.")
    parser.add_argument("--roi-half-width-kev", type=float, default=ROI_HALF_WIDTH_KEV, help="ROI half width around lines (keV).")
    parser.add_argument("--normalize-live-time", action="store_true", help="Normalize counts by live time (counts/s).")
    args = parser.parse_args()

    spectra_dir = Path(args.spectra)
    pad_dir = Path(args.pad_dir)
    out_csv = Path(args.out)
    hw = args.roi_half_width_kev

    # Channels & energy (common for all files)
    n_channels = 1024
    channels = np.arange(n_channels, dtype=float)
    (_, _, _), energy_keV = calibrate_energy_quadratic(channels, ANCHORS_CH, ANCHORS_KEV)

    # Read PAD spectra (rate-normalized if requested)
    def read_pad(fname: str):
        counts, live_us = read_spc_counts_and_times(pad_dir / fname)
        if args.normalize_live_time and live_us and live_us > 0:
            counts = counts / (live_us * 1e-6)  # counts per second
        return counts

    pad_k_counts = read_pad("PAD_K_A.spc")
    pad_u_counts = read_pad("PAD_U_A.spc")
    pad_th_counts = read_pad("PAD_Th_A.spc")

    # Build PAD feature matrix M_ref (n_features x 3)
    fK  = build_feature_vector(energy_keV, pad_k_counts, hw)
    fU  = build_feature_vector(energy_keV, pad_u_counts, hw)
    fTh = build_feature_vector(energy_keV, pad_th_counts, hw)
    M_ref = np.stack([fK, fU, fTh], axis=1)  # shape (9,3)

    # Process spectra
    spc_files = sorted(spectra_dir.glob("*.spc"))
    if not spc_files:
        print(f"[WARN] No .spc files in: {spectra_dir}")
        return

    with out_csv.open("w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["file", "latitude", "longitude", "elevation",
                         "K_percent", "U_ppm", "Th_ppm",
                         "K_from_PADK", "K_from_PADU", "K_from_PADTh",
                         "U_from_PADK", "U_from_PADU", "U_from_PADTh",
                         "Th_from_PADK", "Th_from_PADU", "Th_from_PADTh",
                         "w_PADK", "w_PADU", "w_PADTh", "fit_r2"])

        for spc in spc_files:
            try:
                counts, live_us = read_spc_counts_and_times(spc)
                lat, lon, elev = extract_location_from_spc(spc)

                # Format location for CSV, blank if missing
                lat_str = f"{lat:.10f}" if lat is not None else ""
                lon_str = f"{lon:.10f}" if lon is not None else ""
                elev_str = f"{elev:.1f}" if elev is not None else ""

                if args.normalize_live_time and live_us and live_us > 0:
                    counts = counts / (live_us * 1e-6)
                y_feats = build_feature_vector(energy_keV, counts, hw)
                w_hat, r2 = fit_pad_weights(y_feats, M_ref)

                # Concentrations via c = C_PAD @ w
                c = C_PAD @ w_hat
                K_percent, U_ppm, Th_ppm = c.tolist()

                # 3x3 contribution breakdown: element-wise C_PAD[i,j] * w_hat[j]
                # Rows: K%, Uppm, Thppm  |  Cols: PAD_K, PAD_U, PAD_Th
                contrib = C_PAD * w_hat[np.newaxis, :]  # shape (3,3)
                contrib_flat = contrib.flatten()         # row-major: 9 values

                writer.writerow([spc.name, lat_str, lon_str, elev_str,
                                 f"{K_percent:.3f}", f"{U_ppm:.3f}", f"{Th_ppm:.3f}",
                                 f"{contrib_flat[0]:.4f}", f"{contrib_flat[1]:.4f}", f"{contrib_flat[2]:.4f}",
                                 f"{contrib_flat[3]:.4f}", f"{contrib_flat[4]:.4f}", f"{contrib_flat[5]:.4f}",
                                 f"{contrib_flat[6]:.4f}", f"{contrib_flat[7]:.4f}", f"{contrib_flat[8]:.4f}",
                                 f"{w_hat[0]:.4f}", f"{w_hat[1]:.4f}", f"{w_hat[2]:.4f}", f"{r2:.4f}"])
                print(f"[OK] {spc.name}: K={K_percent:.3f}%  U={U_ppm:.3f} ppm  Th={Th_ppm:.3f} ppm  (R^2={r2:.3f})")
            except Exception as e:
                print(f"[ERR] {spc.name} -> {e}")

    print(f"[CSV] Saved: {out_csv}")

if __name__ == "__main__":
    main()
