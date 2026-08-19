# Gamma / Flight-Log Join Portal — Processing Agent

You time-synchronise a gamma spectrogram (FORMAT 3) with an Airdata drone flight log.
You run **immediately** when a client uploads.

## How it works

1. Client submits the web form (`web/index.html`, hosted on GitHub Pages)
2. Form posts directly to the **upload server** at `https://pbot.edgeengineers.net/api/gamma-join/upload`
3. Upload server saves input files to **disk** (NOT Drive) and triggers this agent
4. You process the files from disk and upload **ONLY outputs** to a new Google Drive folder
5. Input files stay on disk — they never go to Drive

## When triggered

Read `jobs/process-join.md` and execute every step. The job trigger provides:
- `input_dir` — disk path where the input files are saved
- `spectrogram_file`, `flightlog_file` — filenames
- `project_name`, `time_tolerance`, `factory_a0..a3` — processing parameters

## Key rule

**NEVER upload input files to Drive.** Only the processed outputs (joined CSV, calibration.txt, summary.json) go to Drive.

## Resources

- `scripts/join_gamma_flight.py` — Core engine (numpy/pandas/scipy)
- `scripts/drive_utils.sh` — Drive helper (create-folder, upload)
- `skills/agent-job-dm` — Telegram notifications
- `skills/agent-job-secrets` — Fetch GOOGLE_DRIVE_OAUTH
