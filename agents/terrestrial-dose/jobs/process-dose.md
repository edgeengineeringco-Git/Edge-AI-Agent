# Terrestrial Dose — Point Analysis Job

Process a dose analysis request for specific coordinates.

## Trigger

Manual request or scheduled batch.

## Execution Steps

### Step 1: Install Dependencies
```bash
pip install fastapi uvicorn numpy 2>/dev/null || true
```

### Step 2: Run Dose Calculation
```bash
cd agents/terrestrial-dose
python3 -c "
from dose_core.dose_calculation_core import polygon_dose_fingerprint
import json

# Example: Dublin
fp = polygon_dose_fingerprint(lithology='world_average_soil')
print(json.dumps(fp, indent=2))
"
```

### Step 3: Start API Server (if needed)
```bash
cd agents/terrestrial-dose
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Step 4: Query a Point via API
```bash
curl 'http://localhost:8000/dose?lat=53.35&lon=-6.26'
```

### Step 5: Run Validation Tests
```bash
cd agents/terrestrial-dose
python3 -m pytest tests/test_dose_core.py -v
```

### Step 6: Notify via Telegram (optional)
Use `agent-job-dm` skill to broadcast results summary.

## Notes

- All dose formulas are in `dose_core/dose_calculation_core.py` — do not modify
- The API reads data layers at runtime via `ingest/point_sampler.py`
- Geology resolution follows national survey scale (50k–100k where available, 1M fallback)
- Missing data layers return "unavailable" — never silently defaulted
