# input/

Optional local drop zone for manual/CLI runs. The live portal stores uploads in
Google Drive (one subfolder per job) via the serverless Apps Script backend — this
folder is only for hand-running the engine locally.

## Manual run example

```bash
python3 ../scripts/join_gamma_flight.py \
  --spectrogram spectrogram.txt \
  --flightlog   flightlog.csv \
  --project-name my_survey \
  --output-dir   ./out \
  --time-tolerance 1
```

## Expected input formats

- Spectrogram: FORMAT 3 text export (first line `FORMAT: 3`).
- Flight log: Airdata CSV with at least `time(millisecond)`, `datetime(utc)`,
  `latitude`, `longitude`. Feet/mph columns are auto-converted to metres / m·s⁻¹.
