# input/

Optional local drop zone for manual/CLI runs. The live portal saves uploads to
`data/gamma-flight-join/jobs/{job_id}/input/` instead (git-ignored runtime data).

## Manual run example

```bash
python3 ../scripts/join_gamma_flight.py \
  --spectrogram spectrogram.txt \
  --flightlog   flightlog.csv \
  --project-name my_survey \
  --output-dir   ./out \
  --time-tolerance 5
```

## Expected input formats

- Spectrogram: FORMAT 3 text export (first line `FORMAT: 3`).
- Flight log: Airdata CSV with at least `time(millisecond)`, `datetime(utc)`,
  `latitude`, `longitude`. Feet/mph columns are auto-converted to metres / m·s⁻¹.
