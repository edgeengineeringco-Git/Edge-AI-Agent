"""
Estimate K (%), U (ppm), Th (ppm) for each .spc using PAD spectra and full 3x3 PAD composition matrix.

- Energy calibrated with a quadratic (Geomon anchors).
- Features = ROI sums around key lines (K-40, U-chain, Th-chain).
- Fit y = M_ref @ w to get PAD weights w >= 0.
- Convert PAD weights to concentrations with c = C @ w, where C is 3x3 PAD composition matrix:
  rows = [K, U, Th], cols = [PAD_K_A, PAD_U_A, PAD_Th_A].
- Location data (lat, lon, elev) extracted from the 3 lines before the footer of each .spc.
"""

import sys
from pathlib import Path
import csv
import numpy as np

ANCHORS_CH = np.array([870.5, 720.8, 31.6, 484.0], dtype=float)
ANCHORS_KEV = np.array([2611.4, 2162.3, 94.8, 1451.9], dtype=float)

REF_LINES = {
    "K": [1460.8],
    "U": [351.9, 609.3, 1120.3, 1764.5],
    "Th": [583.2, 911.1, 968.9, 2614.5],
}
ROI_HALF_WIDTH_KEV = 20.0

C_PAD = np.array([
    [6.85, 1.17, 0.98],
    [1.38, 40.87, 1.90],
    [2.54, 4.42, 111.59],
], dtype=float)


def first_numeric_token_or_none(line):
    for tok in line.strip().split():
        try:
            return float(tok)
        except ValueError:
            continue
    return None


def read_spc_counts_and_times(path, header_lines=2, n_channels=1024):
    if not path.exists():
        raise FileNotFoundError(f"SPC not found: {path}")
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        lines = [ln.rstrip("\n") for ln in f]
    if len(lines) < header_lines + n_channels:
        raise RuntimeError(f"SPC too short: {len(lines)} lines; need at least {header_lines + n_channels}.")
    live_time_us = first_numeric_token_or_none(lines[0])
    data_block = lines[header_lines: header_lines + n_channels]
    counts = []
    for raw in data_block:
        val = first_numeric_token_or_none(raw)
        counts.append(val if val is not None else 0.0)
    return np.array(counts, dtype=float), live_time_us


def extract_location_from_spc(path):
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            lines = [ln.rstrip("\n") for ln in f]
        if len(lines) < 1030:
            return None, None, None
        lat = first_numeric_token_or_none(lines[-4].strip())
        lon = first_numeric_token_or_none(lines[-3].strip())
        elev = first_numeric_token_or_none(lines[-2].strip())
        return lat, lon, elev
    except Exception:
        return None, None, None


def calibrate_energy_quadratic(ch, anchors_ch, anchors_keV):
    A = np.vstack([np.ones_like(anchors_ch), anchors_ch, anchors_ch ** 2]).T
    c0, c1, c2 = np.linalg.lstsq(A, anchors_keV, rcond=None)[0]
    return (c0, c1, c2), c0 + c1 * ch + c2 * (ch ** 2)


def integrate_rois(energy_keV, counts, roi_lines, half_width_keV):
    feats = []
    for E0 in roi_lines:
        mask = (energy_keV >= (E0 - half_width_keV)) & (energy_keV <= (E0 + half_width_keV))
        feats.append(counts[mask].sum())
    return np.array(feats, dtype=float)


def build_feature_vector(energy_keV, counts, half_width_keV):
    fK = integrate_rois(energy_keV, counts, REF_LINES["K"], half_width_keV)
    fU = integrate_rois(energy_keV, counts, REF_LINES["U"], half_width_keV)
    fTh = integrate_rois(energy_keV, counts, REF_LINES["Th"], half_width_keV)
    return np.concatenate([fK, fU, fTh])


def fit_pad_weights(y_feats, M_ref):
    w_hat, _, _, _ = np.linalg.lstsq(M_ref, y_feats, rcond=None)
    w_hat = np.maximum(w_hat, 0.0)
    y_pred = M_ref @ w_hat
    ss_res = np.sum((y_feats - y_pred) ** 2)
    ss_tot = np.sum((y_feats - np.mean(y_feats)) ** 2) if np.any(y_feats) else 0.0
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 1.0
    return w_hat, r2


def get_user_input(prompt, default=""):
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    response = input(prompt).strip()
    return response if response else default


def parse_cli_args():
    args = {"spectra": None, "pad_dir": None, "out": None,
            "roi_half_width_kev": None, "normalize_live_time": False}
    i = 1
    while i < len(sys.argv):
        a = sys.argv[i]
        if a == "--spectra" and i + 1 < len(sys.argv):
            args["spectra"] = sys.argv[i + 1]; i += 2
        elif a == "--pad-dir" and i + 1 < len(sys.argv):
            args["pad_dir"] = sys.argv[i + 1]; i += 2
        elif a == "--out" and i + 1 < len(sys.argv):
            args["out"] = sys.argv[i + 1]; i += 2
        elif a == "--roi-half-width-kev" and i + 1 < len(sys.argv):
            args["roi_half_width_kev"] = sys.argv[i + 1]; i += 2
        elif a == "--normalize-live-time":
            args["normalize_live_time"] = True; i += 1
        else:
            i += 1
    return args


def main():
    cli = parse_cli_args()
    use_cli = cli["spectra"] is not None

    if not use_cli:
        print("=" * 60)
        print("K/U/Th Estimation Tool")
        print("=" * 60)
        print()
        print("Please provide the following paths:")
        print()

    if use_cli:
        spectra_dir = Path(cli["spectra"])
        if not spectra_dir.is_dir():
            print(f"[ERROR] Spectra directory not found: {cli['spectra']}")
            sys.exit(1)
    else:
        while True:
            sp = get_user_input("Folder with input .spc spectra")
            spectra_dir = Path(sp)
            if spectra_dir.exists() and spectra_dir.is_dir():
                break
            print(f"Error: Directory not found: {sp}")
            print()

    if use_cli:
        pad_dir = Path(cli["pad_dir"])
        if not pad_dir.is_dir():
            print(f"[ERROR] PAD directory not found: {cli['pad_dir']}")
            sys.exit(1)
        required = ["PAD_K_A.spc", "PAD_U_A.spc", "PAD_Th_A.spc"]
        missing = [f for f in required if not (pad_dir / f).exists()]
        if missing:
            print(f"[ERROR] Missing PAD files: {', '.join(missing)}")
            sys.exit(1)
    else:
        while True:
            pp = get_user_input("Folder with PAD_K_A.spc, PAD_U_A.spc, PAD_Th_A.spc")
            pad_dir = Path(pp)
            if pad_dir.exists() and pad_dir.is_dir():
                required = ["PAD_K_A.spc", "PAD_U_A.spc", "PAD_Th_A.spc"]
                missing = [f for f in required if not (pad_dir / f).exists()]
                if missing:
                    print(f"Warning: Missing PAD files: {', '.join(missing)}")
                    print("Please make sure all PAD files are in the specified directory.")
                    continue
                break
            print(f"Error: Directory not found: {pp}")
            print()

    if use_cli:
        out_csv = Path(cli["out"])
        out_csv.parent.mkdir(parents=True, exist_ok=True)
    else:
        while True:
            op = get_user_input("Output CSV file path")
            out_csv = Path(op)
            if out_csv.parent.exists() or out_csv.parent == Path("."):
                break
            print(f"Error: Parent directory does not exist: {out_csv.parent}")
            print()

    if use_cli and cli["roi_half_width_kev"] is not None:
        try:
            hw = float(cli["roi_half_width_kev"])
        except ValueError:
            print(f"Invalid --roi-half-width-kev, using default: {ROI_HALF_WIDTH_KEV}")
            hw = ROI_HALF_WIDTH_KEV
    else:
        try:
            ri = get_user_input("ROI half width around lines (keV)", str(ROI_HALF_WIDTH_KEV))
            hw = float(ri)
        except ValueError:
            print(f"Invalid input, using default: {ROI_HALF_WIDTH_KEV} keV")
            hw = ROI_HALF_WIDTH_KEV

    normalize_live_time = cli["normalize_live_time"] if use_cli else False
    if not use_cli:
        ni = get_user_input("Normalize counts by live time? (yes/no)", "no")
        normalize_live_time = ni.lower() in ("yes", "y", "true", "1")

    print()
    print("=" * 60)
    print("Processing with the following settings:")
    print(f"  Spectra directory: {spectra_dir}")
    print(f"  PAD directory: {pad_dir}")
    print(f"  Output CSV: {out_csv}")
    print(f"  ROI half width: {hw} keV")
    print(f"  Normalize live time: {normalize_live_time}")
    print("=" * 60)
    print()

    channels = np.arange(1024, dtype=float)
    (_, _, _), energy_keV = calibrate_energy_quadratic(channels, ANCHORS_CH, ANCHORS_KEV)

    def read_pad(fname):
        counts, live_us = read_spc_counts_and_times(pad_dir / fname)
        if normalize_live_time and live_us and live_us > 0:
            counts = counts / (live_us * 1e-6)
        return counts

    print("Reading PAD spectra...")
    pad_k_counts = read_pad("PAD_K_A.spc")
    pad_u_counts = read_pad("PAD_U_A.spc")
    pad_th_counts = read_pad("PAD_Th_A.spc")

    fK = build_feature_vector(energy_keV, pad_k_counts, hw)
    fU = build_feature_vector(energy_keV, pad_u_counts, hw)
    fTh = build_feature_vector(energy_keV, pad_th_counts, hw)
    M_ref = np.stack([fK, fU, fTh], axis=1)

    spc_files = sorted(spectra_dir.glob("*.spc"))
    if not spc_files:
        print(f"[WARN] No .spc files in: {spectra_dir}")
        return

    print(f"Found {len(spc_files)} .spc files to process")
    print()

    with out_csv.open("w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["file", "latitude", "longitude", "elevation",
                         "K_percent", "U_ppm", "Th_ppm",
                         "w_PADK", "w_PADU", "w_PADTh", "fit_r2"])

        for i, spc in enumerate(spc_files, 1):
            try:
                counts, live_us = read_spc_counts_and_times(spc)
                lat, lon, elev = extract_location_from_spc(spc)

                lat_str = f"{lat:.10f}" if lat is not None else ""
                lon_str = f"{lon:.10f}" if lon is not None else ""
                elev_str = f"{elev:.1f}" if elev is not None else ""

                if normalize_live_time and live_us and live_us > 0:
                    counts = counts / (live_us * 1e-6)

                y_feats = build_feature_vector(energy_keV, counts, hw)
                w_hat, r2 = fit_pad_weights(y_feats, M_ref)

                c = C_PAD @ w_hat
                K_percent, U_ppm, Th_ppm = c.tolist()

                writer.writerow([spc.name, lat_str, lon_str, elev_str,
                                 f"{K_percent:.3f}", f"{U_ppm:.3f}", f"{Th_ppm:.3f}",
                                 f"{w_hat[0]:.4f}", f"{w_hat[1]:.4f}", f"{w_hat[2]:.4f}",
                                 f"{r2:.4f}"])
                print(f"[{i}/{len(spc_files)}] {spc.name}: K={K_percent:.3f}%  U={U_ppm:.3f} ppm  Th={Th_ppm:.3f} ppm  (R^2={r2:.3f})")
            except Exception as e:
                print(f"[ERR] {spc.name} -> {e}")

    print()
    print("=" * 60)
    print(f"[CSV] Results saved to: {out_csv}")
    print("=" * 60)


if __name__ == "__main__":
    main()
