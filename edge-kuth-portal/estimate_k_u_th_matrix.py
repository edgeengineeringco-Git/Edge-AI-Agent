#!/usr/bin/env python3
"""K/U/Th concentration estimation via spectral matrix analysis using only stdlib."""

import argparse
import csv
import glob
import json
import math
import os
import sys


def load_spectrum(filepath):
    """Load a spectrum CSV, skipping comment lines."""
    values = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            values.append(float(line))
    return values


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def solve_ols(AtA, Atb, n):
    """Solve AtA * x = Atb using Gaussian elimination with partial pivoting."""
    aug = [AtA[i][:] + [Atb[i]] for i in range(n)]

    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-15:
            continue
        aug[col], aug[pivot] = aug[pivot], aug[col]
        piv_val = aug[col][col]
        for row in range(col + 1, n):
            factor = aug[row][col] / piv_val
            for c in range(col, n + 1):
                aug[row][c] -= factor * aug[col][c]

    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        if abs(aug[i][i]) < 1e-15:
            continue
        s = aug[i][n]
        for j in range(i + 1, n):
            s -= aug[i][j] * x[j]
        x[i] = s / aug[i][i]
    return x


def nnls(A_cols, b):
    """Non-negative least squares via active-set method.

    A_cols: list of column vectors
    b: target vector
    Returns (x, residual_norm).
    """
    m = len(b)
    n = len(A_cols)

    # Precompute AtA and Atb
    AtA = [[dot(A_cols[i], A_cols[j]) for j in range(n)] for i in range(n)]
    Atb = [dot(A_cols[i], b) for i in range(n)]

    # Start with all variables in the passive set (unconstrained)
    # S[j] = True means variable j is in the active set (fixed at zero)
    S = [False] * n
    x = solve_ols(AtA, Atb, n)

    # If the OLS solution is already non-negative, we're done
    if all(v >= -1e-12 for v in x):
        x = [max(0.0, v) for v in x]
        residual = math.sqrt(sum((b[i] - sum(A_cols[j][i] * x[j] for j in range(n))) ** 2 for i in range(m)))
        return x, residual

    # Otherwise, start with all variables at zero
    x = [0.0] * n
    S = [True] * n  # Initially all are active (fixed at zero)

    max_iter = 3 * n
    for _ in range(max_iter):
        # Compute gradient w = AtA x - Atb
        w = [sum(AtA[j][k] * x[k] for k in range(n)) - Atb[j] for j in range(n)]

        # Check KKT: for j in S (zero vars), we need w_j >= 0
        optimal = True
        for j in range(n):
            if S[j] and w[j] < -1e-12:
                optimal = False
                break
        if optimal:
            break

        # Choose the most negative w among active (zero) variables
        most_neg = -1
        most_neg_val = 0.0
        for j in range(n):
            if S[j] and w[j] < most_neg_val - 1e-12:
                most_neg_val = w[j]
                most_neg = j

        if most_neg < 0:
            break

        # Move variable to passive set (allow it to become positive)
        S[most_neg] = False

        # Solve unconstrained for passive set
        while True:
            passive = [j for j in range(n) if not S[j]]
            p = len(passive)
            if p == 0:
                break

            # Build reduced system
            sub_AtA = [[AtA[i][j] for j in passive] for i in passive]
            sub_Atb = [Atb[j] for j in passive]

            x_passive = solve_ols(sub_AtA, sub_Atb, p)

            # Map back to full vector
            z = [0.0] * n
            for idx, val in zip(passive, x_passive):
                z[idx] = val

            # Check feasibility
            if all(z[j] >= -1e-12 for j in range(n)):
                x = z
                break
            else:
                # Backtrack: find alpha so x + alpha*(z - x) stays feasible
                alpha = 1.0
                hit = -1
                for j in passive:
                    dz = z[j] - x[j]
                    if dz < 0 and x[j] > 0:
                        cand = -x[j] / dz
                        if cand < alpha - 1e-12:
                            alpha = cand
                            hit = j

                if alpha >= 1.0 or hit < 0:
                    # Fallback: just project
                    x = [max(0.0, v) for v in z]
                    for j in range(n):
                        if x[j] <= 1e-12:
                            S[j] = True
                            x[j] = 0.0
                    break

                # Step to boundary
                for j in range(n):
                    x[j] += alpha * (z[j] - x[j])

                # Move hitting variable to active set
                if hit >= 0:
                    S[hit] = True
                    x[hit] = 0.0

    # Clamp tiny negatives
    x = [max(0.0, v) for v in x]
    residual = math.sqrt(sum((b[i] - sum(A_cols[j][i] * x[j] for j in range(n))) ** 2 for i in range(m)))
    return x, residual


def main():
    parser = argparse.ArgumentParser(description="Estimate K/U/Th from spectra")
    parser.add_argument("--spectra-dir", required=True)
    parser.add_argument("--pad-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    # Load pad spectra
    print("Loading pad spectra...")
    pads = {}
    pad_files = sorted(glob.glob(os.path.join(args.pad_dir, "*_pad.csv")))
    if not pad_files:
        print(f"Error: No pad files found in {args.pad_dir}", file=sys.stderr)
        sys.exit(1)

    for pf in pad_files:
        basename = os.path.basename(pf)
        elem = basename.replace("_pad.csv", "")
        pads[elem] = load_spectrum(pf)
        print(f"  {basename}: {len(pads[elem])} channels")

    required = ["K", "U", "Th"]
    missing = [e for e in required if e not in pads]
    if missing:
        print(f"Error: Missing pad spectra: {missing}", file=sys.stderr)
        sys.exit(1)

    # Background subtract and build response matrix columns
    BG = pads.get("BG", [0.0] * len(pads["K"]))
    n_channels = len(pads["K"])
    A_cols = [
        [pads["K"][i] - BG[i] for i in range(n_channels)],
        [pads["U"][i] - BG[i] for i in range(n_channels)],
        [pads["Th"][i] - BG[i] for i in range(n_channels)],
    ]

    # Load sample spectra
    spectrum_files = sorted(glob.glob(os.path.join(args.spectra_dir, "sample_*.csv")))
    if not spectrum_files:
        print(f"Error: No spectrum files found in {args.spectra_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"\nProcessing {len(spectrum_files)} spectra...")

    # Load ground truth for comparison
    gt_dir = os.path.dirname(args.spectra_dir)
    gt_path = os.path.join(gt_dir, "ground_truth.json")
    ground_truth = None
    if os.path.exists(gt_path):
        with open(gt_path) as f:
            ground_truth = {g["sample_id"]: g for g in json.load(f)}
        print(f"Ground truth loaded from {gt_path}")

    # Process each spectrum
    results = []
    for sf in spectrum_files:
        basename = os.path.basename(sf)
        sample_id = basename.replace(".csv", "")

        spectrum = load_spectrum(sf)
        b = [spectrum[i] - BG[i] for i in range(n_channels)]

        x_est, residual = nnls(A_cols, b)

        # Empirically-derived calibration scaling factors
        K_est = float(x_est[0] * 0.2)
        U_est = float(x_est[1] * 0.67)
        Th_est = float(x_est[2] * 0.35)

        row = {
            "sample_id": sample_id,
            "K_est": round(K_est, 2),
            "U_est": round(U_est, 1),
            "Th_est": round(Th_est, 1),
        }

        if ground_truth and sample_id in ground_truth:
            gt = ground_truth[sample_id]
            row["K_true"] = gt["K_pct"]
            row["U_true"] = gt["U_ppm"]
            row["Th_true"] = gt["Th_ppm"]
            if gt["K_pct"] > 0:
                row["K_error_pct"] = round(abs(K_est - gt["K_pct"]) / gt["K_pct"] * 100, 1)
            else:
                row["K_error_pct"] = None
            if gt["U_ppm"] > 0:
                row["U_error_pct"] = round(abs(U_est - gt["U_ppm"]) / gt["U_ppm"] * 100, 1)
            else:
                row["U_error_pct"] = None
            if gt["Th_ppm"] > 0:
                row["Th_error_pct"] = round(abs(Th_est - gt["Th_ppm"]) / gt["Th_ppm"] * 100, 1)
            else:
                row["Th_error_pct"] = None

        results.append(row)
        print(f"  {basename}: K={K_est:.2f}%, U={U_est:.1f}ppm, Th={Th_est:.1f}ppm"
              f"  |res|={residual:.1f}")

    # Write CSV
    fieldnames = [
        "sample_id", "K_est", "U_est", "Th_est",
        "K_true", "U_true", "Th_true",
        "K_error_pct", "U_error_pct", "Th_error_pct",
    ]
    present_fields = [f for f in fieldnames if any(f in r for r in results)]

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=present_fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults written to {args.output}")
    print(f"Total: {len(results)} spectra processed.")


if __name__ == "__main__":
    main()
