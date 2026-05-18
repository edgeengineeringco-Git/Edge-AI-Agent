#!/usr/bin/env python3
"""Generate synthetic K/U/Th gamma-ray spectra test data using only stdlib."""

import argparse
import json
import math
import os
import random

N_CHANNELS = 256
RNG_SEED = 42


def gaussian_peak(channels, centroid, amplitude, fwhm):
    """Generate a Gaussian photopeak (channels is a list of ints)."""
    sigma = fwhm / 2.355
    return [amplitude * math.exp(-0.5 * ((c - centroid) / sigma) ** 2) for c in channels]


def generate_pad_spectrum(element, n_channels=N_CHANNELS):
    """Generate a standard (pad) spectrum for a given element."""
    channels = list(range(n_channels))
    energy_per_channel = 8.0  # keV per channel
    spectrum = [0.0] * n_channels

    # Continuum (Compton scattering)
    continuum_amp = {"K": 50, "U": 80, "Th": 100, "BG": 30}
    base_amp = continuum_amp.get(element, 50)
    for i in range(n_channels):
        spectrum[i] += base_amp * math.exp(-i / (n_channels / 2.5))

    # Characteristic photopeaks (energy_keV, relative_amplitude)
    if element == "K":
        peaks = [(1460.8, 1000)]
    elif element == "U":
        peaks = [
            (295.2, 200),
            (352.0, 400),
            (609.3, 500),
            (1120.3, 200),
            (1764.5, 300),
        ]
    elif element == "Th":
        peaks = [
            (238.6, 500),
            (338.3, 300),
            (583.2, 400),
            (911.1, 350),
            (2614.5, 700),
        ]
    else:  # BG
        peaks = [
            (511.0, 100),
            (1460.8, 80),
            (2614.5, 60),
        ]

    fwhm_at_662 = 40.0
    for energy_keV, amplitude in peaks:
        centroid = energy_keV / energy_per_channel
        fwhm = fwhm_at_662 * math.sqrt(energy_keV / 662.0)
        peak = gaussian_peak(channels, centroid, amplitude, fwhm)
        for i in range(n_channels):
            spectrum[i] += peak[i]

    # Add Poisson noise (approximate with normal for large counts)
    spectrum = [max(0, int(p + random.gauss(0, math.sqrt(max(p, 1))))) for p in spectrum]
    return spectrum


def generate_sample_spectrum(K_pct, U_ppm, Th_ppm, K_pad, U_pad, Th_pad, BG_pad, n_channels=N_CHANNELS):
    """Generate a synthetic mixed spectrum from known concentrations."""
    K_factor = 5.0
    U_factor = 1.5
    Th_factor = 0.8

    spectrum = []
    for i in range(n_channels):
        val = (K_pct * K_factor * K_pad[i]
               + U_ppm * U_factor * U_pad[i]
               + Th_ppm * Th_factor * Th_pad[i]
               + BG_pad[i])
        spectrum.append(max(0, int(val + random.gauss(0, math.sqrt(max(val, 1))))))
    return spectrum


def save_spectrum(filepath, spectrum, metadata):
    """Save a spectrum as a simple CSV."""
    lines = []
    if "K_pct" in metadata:
        lines.append(f"# K={metadata['K_pct']:.2f}%, U={metadata['U_ppm']:.1f}ppm, Th={metadata['Th_ppm']:.1f}ppm")
    else:
        lines.append(f"# Element: {metadata.get('element', 'unknown')}")
    for v in spectrum:
        lines.append(str(v))
    with open(filepath, "w") as f:
        f.write("\n".join(lines) + "\n")

    meta_path = filepath.replace(".csv", "_meta.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Generate K/U/Th test spectra")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--n-spectra", type=int, default=20)
    args = parser.parse_args()

    random.seed(RNG_SEED)

    spectra_dir = os.path.join(args.output_dir, "spectra")
    pads_dir = os.path.join(args.output_dir, "pads")
    os.makedirs(spectra_dir, exist_ok=True)
    os.makedirs(pads_dir, exist_ok=True)

    # Generate pad spectra
    print("Generating pad spectra...")
    pad_data = {}
    for elem in ["K", "U", "Th", "BG"]:
        pad = generate_pad_spectrum(elem)
        pad_path = os.path.join(pads_dir, f"{elem}_pad.csv")
        save_spectrum(pad_path, pad, {"element": elem, "type": "pad"})
        pad_data[elem] = pad
        print(f"  {elem}_pad.csv — total counts: {sum(pad):.0f}")

    # Generate sample spectra
    print(f"\nGenerating {args.n_spectra} sample spectra...")
    ground_truths = []
    for i in range(args.n_spectra):
        K_pct = round(random.uniform(0.1, 5.0), 2)
        U_ppm = round(random.uniform(0.5, 20.0), 1)
        Th_ppm = round(random.uniform(1.0, 40.0), 1)

        spectrum = generate_sample_spectrum(
            K_pct, U_ppm, Th_ppm,
            pad_data["K"], pad_data["U"], pad_data["Th"], pad_data["BG"],
        )

        sample_path = os.path.join(spectra_dir, f"sample_{i:03d}.csv")
        metadata = {
            "sample_id": f"sample_{i:03d}",
            "K_pct": K_pct,
            "U_ppm": U_ppm,
            "Th_ppm": Th_ppm,
        }
        save_spectrum(sample_path, spectrum, metadata)
        ground_truths.append(metadata)
        print(f"  sample_{i:03d}.csv — K={K_pct}%, U={U_ppm}ppm, Th={Th_ppm}ppm — total counts: {sum(spectrum):.0f}")

    gt_path = os.path.join(args.output_dir, "ground_truth.json")
    with open(gt_path, "w") as f:
        json.dump(ground_truths, f, indent=2)
    print(f"\nGround truth saved to {gt_path}")
    print("Done.")


if __name__ == "__main__":
    main()
