# K/U/Th Spectral Analysis

Analyze gamma-ray .spc spectra to estimate potassium (%), uranium (ppm), and thorium (ppm) concentrations using the PAD composition matrix method.

## Usage

Invoke this skill when you need to process .spc spectrum files for K/U/Th estimation.

### Prerequisites

The Python engine is at `edge-kuth-portal/estimate_k_u_th_matrix.py` in the workspace root. It requires `numpy`.

### CLI Mode (recommended for batch processing)

```bash
python /home/coding-agent/workspace/edge-kuth-portal/estimate_k_u_th_matrix.py \
  --spectra /path/to/spectra/folder \
  --pad-dir /path/to/pad/reference/folder \
  --out /path/to/results.csv
```

Optional flags:
- `--roi-half-width-kev 25` — Set ROI half-width in keV (default: 20)
- `--normalize-live-time` — Normalize counts by live time (counts per second)

## How It Works

1. **Energy calibration**: Quadratic fit using Geomon anchors maps channel → keV
2. **ROI integration**: Sums counts in ±20 keV windows around reference lines:
   - K: 1460.8 keV (K-40)
   - U: 351.9, 609.3, 1120.3, 1764.5 keV (U-chain)
   - Th: 583.2, 911.1, 968.9, 2614.5 keV (Th-chain)
3. **PAD fitting**: Non-negative least-squares fit of sample 9-feature vector against PAD reference matrix M_ref (9×3, columns = PAD_K, PAD_U, PAD_Th). This yields PAD weights w (w_PADK, w_PADU, w_PADTh) and fit quality R².
4. **Concentration**: Convert PAD weights to concentrations via c = C_PAD @ w, where C_PAD is the hardcoded 3×3 composition matrix:
   - Row 0 (K%): [6.85, 1.17, 0.98]
   - Row 1 (U ppm): [1.38, 40.87, 1.90]
   - Row 2 (Th ppm): [2.54, 4.42, 111.59]
5. **Normalization** (pipeline): Before estimation, handle-upload.sh normalizes all spectra (PAD + sample) to 100k total counts, preventing count-scale differences from biasing PAD weights.

## Output Format

CSV with columns: `file, K_percent, U_ppm, Th_ppm, w_PADK, w_PADU, w_PADTh, fit_r2`

Quality check: `fit_r2` should be > 0.90 for reliable results.

## PAD Reference Files Required

- `PAD_K_A.spc` — Potassium reference spectrum
- `PAD_U_A.spc` — Uranium reference spectrum  
- `PAD_Th_A.spc` — Thorium reference spectrum

### Local files
Place them in `edge-kuth-portal/pad_reference/`.

### Google Drive (when configured)
The agent can fetch PADs from the Drive calibration folder (`1Eg04frfuGOFYbtqd-o4IMCpOaW6xoNc4`) using `edge-kuth-portal/drive-utils.sh download-pads` with a valid `GDRIVE_TOKEN`.
