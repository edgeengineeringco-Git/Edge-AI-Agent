---
name: field-data-collection
description: Digital field data collection for REE exploration — mobile forms, GPS integration, sample chain of custody, and real-time data upload workflows.
---

# Digital Field Data Collection

## When to use

- You need to collect rock, soil, stream sediment, or trench samples in the field.
- You want GPS-tagged photos and sample metadata on mobile devices.
- You need real-time data sync from field to office.
- You want to eliminate transcription errors from paper to digital.

## Mobile Data Collection Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────┐
│  Mobile App │────▶│  Offline    │────▶│  API Endpoint   │
│  (Android/  │     │  Queue      │     │  (/v1/ingest)   │
│   iOS/PWA)  │     │  (SQLite)   │     │                 │
└─────────────┘     └─────────────┘     └─────────────────┘
       │                                           │
       │ (WiFi/cellular)                           ▼
       └──────────────────────────────────▶  PostGIS Database
```

## Sample Types and Protocols

### Rock Chip Sampling
| Parameter | Specification |
|---|---|
| Sample weight | 1–2 kg |
| Dimensions | Fist-sized, representative |
| GPS accuracy | < 10 m (differential GPS preferred) |
| Photo | Wet and dry, with scale |
| Bag | Kraft paper, numbered |
| Duplicate rate | 1 in 20 (same location, second bag) |

### Soil Sampling
| Parameter | Specification |
|---|---|
| Depth | B-horizon, 10–50 cm |
| Sieve | -80 mesh (177 μm) |
| Sample weight | 200–500 g after sieving |
| Grid spacing | 50–200 m (regional), 10–25 m (detailed) |
| Background | 1 sample per 4 km² minimum |

### Stream Sediment
| Parameter | Specification |
|---|---|
| Collect from | Active stream bed, < 5 cm depth |
| Material | Fine sand to silt, avoid organic matter |
| Sample weight | 300–500 g |
| Site selection | Confluence of tributaries, inside bends |

## Mobile App Data Schema

```python
FIELD_SAMPLE_SCHEMA = {
    "sample_id": "string (auto-generated)",
    "project_id": "string",
    "sample_type": "enum: rock, soil, stream, trench, drill_core, water",
    "collection_datetime": "ISO 8601",
    "collector_name": "string",
    "gps_latitude": "float (WGS84)",
    "gps_longitude": "float (WGS84)",
    "gps_accuracy_m": "float",
    "gps_elevation_m": "float",
    "elevation_source": "enum: gps, dem, barometric",
    
    # Location description
    "tenement_id": "string",
    "prospect_name": "string",
    "grid_line": "string",
    "station_id": "string",
    
    # For drill/trench
    "hole_id": "string (optional)",
    "from_m": "float (optional)",
    "to_m": "float (optional)",
    
    # Geological description
    "lithology_code": "string",
    "lithology_description": "text",
    "alteration": "text",
    "mineralization": "text",
    "structure": "text",
    "texture": "text",
    "color": "string",
    "oxidation_pct": "int (0-100)",
    
    # Sampling metadata
    "sample_weight_g": "float",
    "sampling_method": "enum: chip, channel, grab, composite",
    "weather_conditions": "string",
    "photos": "list[uri]",
    
    # QA/QC
    "qc_type": "enum: sample, blank, duplicate, standard",
    "parent_sample_id": "string (for duplicates)",
    
    # Lab dispatch
    "lab_id": "string",
    "dispatch_date": "date",
    "analysis_requested": "list[string]",
    
    # Sync status
    "sync_status": "enum: pending, synced, failed",
    "sync_timestamp": "ISO 8601 (optional)",
    "device_id": "string"
}
```

## Python Backend for Field Sync

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import asyncpg

app = FastAPI()

class FieldSample(BaseModel):
    sample_id: str
    project_id: str
    sample_type: str
    collection_datetime: datetime
    collector_name: str
    gps_latitude: float
    gps_longitude: float
    gps_accuracy_m: float
    lithology_code: str = None
    lithology_description: str = None
    sample_weight_g: float = None
    qc_type: str = "sample"
    photos: list[str] = []

@app.post("/v1/field/sample")
async def submit_field_sample(sample: FieldSample):
    """
    Receive sample from mobile app
    """
    # Validate
    if sample.gps_accuracy_m > 50:
        raise HTTPException(400, "GPS accuracy too poor (>50m)")
    
    # Check for duplicates
    existing = await db.fetchval(
        "SELECT sample_id FROM field_samples WHERE sample_id = $1",
        sample.sample_id
    )
    if existing:
        raise HTTPException(409, "Sample ID already exists")
    
    # Insert
    await db.execute("""
        INSERT INTO field_samples (
            sample_id, project_id, sample_type, collection_datetime,
            collector_name, geom, gps_accuracy_m, lithology_code,
            lithology_description, sample_weight_g, qc_type, photos, sync_status
        ) VALUES ($1, $2, $3, $4, $5, 
                  ST_SetSRID(ST_MakePoint($6, $7), 4326), $8, $9, $10, $11, $12, $13, 'synced')
    """, sample.sample_id, sample.project_id, sample.sample_type,
         sample.collection_datetime, sample.collector_name,
         sample.gps_longitude, sample.gps_latitude, sample.gps_accuracy_m,
         sample.lithology_code, sample.lithology_description,
         sample.sample_weight_g, sample.qc_type, sample.photos)
    
    return {"status": "synced", "sample_id": sample.sample_id}

@app.get("/v1/field/pending/{device_id}")
async def get_pending_syncs(device_id: str):
    """
    Return samples that failed to sync for retry
    """
    rows = await db.fetch("""
        SELECT * FROM field_samples 
        WHERE device_id = $1 AND sync_status = 'failed'
    """, device_id)
    
    return {"pending": [dict(r) for r in rows]}
```

## Chain of Custody

```python
class ChainOfCustody:
    def __init__(self):
        self.custody_chain = []
    
    def collect(self, sample_id, collector, datetime, location):
        self.custody_chain.append({
            'sample_id': sample_id,
            'action': 'collected',
            'agent': collector,
            'datetime': datetime,
            'location': location,
            'condition': 'fresh'
        })
    
    def dispatch(self, sample_id, dispatcher, datetime, courier, tracking):
        self.custody_chain.append({
            'sample_id': sample_id,
            'action': 'dispatched',
            'agent': dispatcher,
            'datetime': datetime,
            'courier': courier,
            'tracking': tracking
        })
    
    def receive_at_lab(self, sample_id, lab_tech, datetime, condition):
        self.custody_chain.append({
            'sample_id': sample_id,
            'action': 'received_at_lab',
            'agent': lab_tech,
            'datetime': datetime,
            'condition': condition
        })
    
    def verify_integrity(self, sample_id):
        """
        Check for gaps or anomalies in custody chain
        """
        chain = [c for c in self.custody_chain if c['sample_id'] == sample_id]
        
        issues = []
        if not chain:
            issues.append("No custody records found")
            return issues
        
        if chain[0]['action'] != 'collected':
            issues.append("Missing collection record")
        
        # Check for time gaps > 48h
        for i in range(1, len(chain)):
            gap = (chain[i]['datetime'] - chain[i-1]['datetime']).total_seconds() / 3600
            if gap > 48:
                issues.append(f"Time gap of {gap:.1f} hours between {chain[i-1]['action']} and {chain[i]['action']}")
        
        return issues
```

## Best Practices

1. **Auto-generate sample IDs:** `PRJ_YYYYMMDD_NNNN` format. Never reuse numbers.
2. **Photo geotagging:** Ensure photos embed GPS coordinates and timestamp.
3. **Offline first:** Mobile app must work without connectivity; sync when available.
4. **Validate on device:** Check ranges, required fields, GPS quality before allowing save.
5. **Daily backup:** Field supervisor downloads all data every evening.
6. **Paper backup:** Print daily summary as emergency backup.
