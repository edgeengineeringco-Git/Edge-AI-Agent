#!/usr/bin/env python3
"""
Generate synthetic .spc test files for verifying the K/U/Th estimation pipeline.

Creates realistic-looking gamma spectra with known K/U/Th concentrations
so you can validate the estimation results.

Usage:
    # Generate 3 test spectra + default PAD reference files
    python generate_test_data.py

    # Generate with specific output directory
    python generate_test_data.py --output-dir /tmp/kuth_test_data

    # Then run:
    python estimate_k_u_th_matrix.py \\
        --spectra-dir /tmp/kuth_test_data/spectra \\
        --pad-dir /tmp/kuth_test_data/pads \\
        --output /tmp/kuth_test_data/results.csv
"""

import argparse
import math
import random
from pathlib import Path

import numpy as np

# Reference lines (keV) from the estimation script
REF_LINES = {
    "K": [1460.8],
    "U": [351.9, 609.3, 1120.3, 1764.5],
    "Th": [583.2, 911.1, 968.9, 2614.5],
}

# Energy calibration constants (from the estimation script)
ANCHORS_CH = np.array([870.5, 720.8, 31.6, 484.0], dtype=float)
ANCHORS_KEV = np.array([2611.4, 2162.3, 94.8, 1451.9], dtype=float)

N_CHANNELS = 1024
HEADER_LINES = 2

# Known concentrations for each PAD (for verification)
PAD_COMPOSITION = {
    "PAD_K_A":  {"K": 6.85, "U": 1.38,  "Th": 2.54},
    "PAD_U_A":  {"K": 1.17, "U": 40.87, "Th": 4.42},
    "PAD_Th_A": {"K": 0.98, "U": 1.90,  "Th": 111.59},
}


def energy_calibration():
    channels = np.arange(N_CHANNELS, dtype=float)
    A = np.vstack([np.ones_like(ANCHORS_CH), ANCHORS_CH, ANCHORS_CH**2]).T
    c0, c1, c2 = np.linalg.lstsq(A, ANCHORS_KEV, rcond=None)[0]
    return c0 + c1 * channels + c2 * (channels**2)


def gaussian_peak(energy_keV, center_keV, amplitude, fwhm=15.0):
    """Gaussian peak with energy-dependent width."""
    sigma = fwhm / 2.355
    # Broaden at higher energies (sqrt(E) dependence)
    sigma_adj = sigma * math.sqrt(center_keV / 500.0) if center_keV > 0 else sigma
    return amplitude * np.exp(-0.5 * ((energy_keV - center_keV) / sigma_adj) ** 2)


def generate_spectrum(
    energy_keV: np.ndarray,
    concentrations: dict,
    live_time_s: float = 300.0,
    noise_level: float = 3.0,
):
    """
    Generate a realistic gamma spectrum for given K/U/Th concentrations.

    Parameters
    ----------
    concentrations : dict
        {"K": K_percent, "U": U_ppm, "Th": Th_ppm}
    live_time_s : float
        Live time in seconds (affects total counts)
    noise_level : float
        Background noise amplitude

    Returns
    -------
    np.ndarray of counts (1024 channels), live_time_us
    """
    counts = np.zeros(N_CHANNELS, dtype=float)

    # Continuum background (Compton + bremsstrahlung)
    background = noise_level * (1.0 + 0.5 * np.sin(np.linspace(0, math.pi, N_CHANNELS)))
    counts += background

    # Add peaks for each element
    base_amplitude = live_time_s * 0.5

    for elem, lines in REF_LINES.items():
        conc = concentrations.get(elem, 0.0)
        element_factor = {
            "K": conc * 10.0,    # K in percent
            "U": conc * 2.0,     # U in ppm
            "Th": conc * 1.5,    # Th in ppm
        }.get(elem, 1.0)

        for line_idx, E0 in enumerate(lines):
            # Relative intensities within each chain
            rel_intensity = {
                "K": [1.0],
                "U": [0.8, 1.0, 0.4, 0.3],
                "Th": [0.6, 1.0, 0.5, 0.9],
            }.get(elem, [1.0])

            amp = base_amplitude * element_factor * rel_intensity[line_idx]
            counts += gaussian_peak(energy_keV, E0, amp, fwhm=12.0 + E0 * 0.005)

    # Add Poisson noise
    counts = np.maximum(counts, 0)
    noisy = np.random.poisson(counts).astype(float)

    return noisy, live_time_s * 1e6  # return live_time in microseconds


def write_spc(path: Path, counts: np.ndarray, live_time_us: float, clock_time_us: float = None,
              lat: float = None, lon: float = None, elevation: float = None):
    """Write a .spc file with channel data and optional location metadata."""
    if clock_time_us is None:
        clock_time_us = live_time_us * 1.05  # 5% dead time
    with path.open("w") as f:
        f.write(f"{int(live_time_us)}\n")
        f.write(f"{int(clock_time_us)}\n")
        for c in counts:
            f.write(f"{int(c)}\n")
        # Metadata footer matching client .spc format
        if lat is not None and lon is not None:
            f.write("10.72 0 3 0\n")
            f.write(f"{lat:.10f}\n")
            f.write(f"{lon:.10f}\n")
            if elevation is not None:
                f.write(f"{int(elevation)}\n")
            f.write("7 0:0:0\n")


def main():
    parser = argparse.ArgumentParser(description="Generate test .spc data for K/U/Th pipeline")
    parser.add_argument("--output-dir", "-o", default="/tmp/kuth_test_data",
                        help="Output directory for test data")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)

    output_dir = Path(args.output_dir)
    spectra_dir = output_dir / "spectra"
    pads_dir = output_dir / "pads"
    spectra_dir.mkdir(parents=True, exist_ok=True)
    pads_dir.mkdir(parents=True, exist_ok=True)

    energy_keV = energy_calibration()

    print("=" * 60)
    print("Generating K/U/Th Test Data")
    print("=" * 60)
    print()

    # Generate PAD reference spectra (pure end-members)
    print("Generating PAD reference spectra...")
    for pad_name, conc in PAD_COMPOSITION.items():
        counts, live_us = generate_spectrum(
            energy_keV, conc, live_time_s=600.0, noise_level=2.0
        )
        write_spc(pads_dir / pad_name, counts, live_us)
        print(f"  {pad_name}: K={conc['K']}%, U={conc['U']}ppm, Th={conc['Th']}ppm")

    print()

    # Generate test spectra with known mixtures + synthetic location data
    test_mixtures = [
        ("granite_01",    {"K": 3.5, "U": 5.0, "Th": 15.0}, 53.250666, -9.507384, 84),
        ("basalt_01",     {"K": 0.8, "U": 1.0, "Th": 2.0},  53.260123, -9.510456, 62),
        ("shale_01",      {"K": 2.5, "U": 3.5, "Th": 10.0}, 53.245678, -9.498765, 95),
        ("sandstone_01",  {"K": 1.2, "U": 2.0, "Th": 5.0},  53.255432, -9.515432, 71),
        ("limestone_01",  {"K": 0.3, "U": 1.5, "Th": 1.5},  53.248901, -9.502345, 108),
    ]

    print("Generating test spectra...")
    for name, conc, lat, lon, elev in test_mixtures:
        counts, live_us = generate_spectrum(
            energy_keV, conc, live_time_s=300.0, noise_level=3.0
        )
        write_spc(spectra_dir / f"{name}.spc", counts, live_us, lat=lat, lon=lon, elevation=elev)
        print(f"  {name}.spc: K={conc['K']}%, U={conc['U']}ppm, Th={conc['Th']}ppm  [{lat:.4f}, {lon:.4f}] elev={elev}m")

    print()
    print(f"Test data generated in: {output_dir}")
    print(f"  Spectra: {spectra_dir}/ ({len(test_mixtures)} files)")
    print(f"  PAD refs: {pads_dir}/ (3 files)")
    print()
    print("To run the estimation:")
    print(f"  cd {Path(__file__).parent}")
    print(f"  python estimate_k_u_th_matrix.py \\")
    print(f"    --spectra-dir {spectra_dir} \\")
    print(f"    --pad-dir {pads_dir} \\")
    print(f"    --output {output_dir/'results.csv'}")


if __name__ == "__main__":
    main()
