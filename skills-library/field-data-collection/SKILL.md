---
name: field-data-collection
description: Digital field data collection for REE exploration — mobile forms, GPS integration, photo management, offline sync, and QA/QC in the field.
---

# Digital Field Data Collection

## When to use

- You need to collect structured field data on tablets or phones.
- You want GPS-tagged photos and samples with barcodes.
- You need offline capability with sync when back in coverage.
- You want real-time validation to catch errors in the field.

## Mobile Form Schema

```python
FIELD_FORM_SCHEMA = {
    'sample_collection': {
        'fields': [
            {'name': 'sample_id', 'type': 'barcode', 'required': True, 'unique': True},
            {'name': 'sample_type', 'type': 'select', 'options': ['rock', 'soil', 'stream_sed', 'water', 'core']},
            {'name': 'easting', 'type': 'gps_auto', 'required': True},
            {'name': 'northing', 'type': 'gps_auto', 'required': True},
            {'name': 'elevation', 'type': 'gps_auto'},
            {'name': 'datum', 'type': 'select', 'options': ['WGS84', 'GDA2020', 'local']},
            {'name': 'photo_ids', 'type': 'camera_multi', 'min': 1, 'max': 5},
            {'name': 'lithology', 'type': 'select', 'options': ['CARB', 'FEN', 'GRAN', 'SHAL', 'BREC', 'OTHER']},
            {'name': 'alteration', 'type': 'multiselect', 'options': ['FENI', 'HEMI', 'SILi', 'CHLO', 'NONE']},
            {'name': 'mineralization', 'type': 'multiselect', 'options': ['BAST', 'MONA', 'XENO', 'NONE']},
            {'name': 'color', 'type': 'color_picker'},
            {'name': 'hardness', 'type': 'select', 'options': ['very_soft', 'soft', 'medium', 'hard', 'very_hard']},
            {'name': 'magnetic', 'type': 'toggle'},
            {'name': 'effervescence', 'type': 'select', 'options': ['none', 'weak', 'strong']},
            {'name': 'notes', 'type': 'text_area', 'max_length': 500},
            {'name': 'collected_by', 'type': 'text', 'default': '{user_name}'},
            {'name': 'datetime', 'type': 'datetime_auto'}
        ],
        'validation_rules': [
            'sample_id must match pattern S-[A-Z]{3}-[0-9]{4}',
            'easting and northing must be within tenement boundary',
            'photo must include scale bar or GPS timestamp',
            'if sample_type == "rock" then lithology != "OTHER"'
        ]
    },
    'drill_hole_logging': {
        'fields': [
            {'name': 'hole_id', 'type': 'barcode', 'required': True},
            {'name': 'from_m', 'type': 'number', 'min': 0, 'required': True},
            {'name': 'to_m', 'type': 'number', 'min': 0, 'required': True},
            {'name': 'lith_code', 'type': 'select', 'required': True},
            {'name': 'alt_code', 'type': 'select'},
            {'name': 'min_code', 'type': 'select'},
            {'name': 'rqd', 'type': 'number', 'min': 0, 'max': 100},
            {'name': 'recovery', 'type': 'number', 'min': 0, 'max': 100},
            {'name': 'fracture_count', 'type': 'number', 'min': 0},
            {'name': 'photo_ids', 'type': 'camera_multi'}
        ],
        'validation_rules': [
            'to_m > from_m',
            'from_m must equal previous to_m (no gaps) or have gap_reason',
            'interval length <= 2.0m for geochem comparison'
        ]
    }
}
```

## Offline Sync Architecture

```python
class OfflineSyncManager:
    """
    Manages data collection when offline, syncs when connected
    """
    
    def __init__(self, local_db_path):
        self.local_db = sqlite3.connect(local_db_path)
        self.server_url = None
        self.pending_queue = []
    
    def save_record(self, record_type, data):
        """Save to local SQLite immediately"""
        record_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        self.local_db.execute("""
            INSERT INTO pending_sync (record_id, record_type, data, timestamp, synced)
            VALUES (?, ?, ?, ?, 0)
        """, (record_id, record_type, json.dumps(data), timestamp))
        self.local_db.commit()
        
        return record_id
    
    async def sync_to_server(self):
        """Push pending records to server when online"""
        cursor = self.local_db.execute(
            "SELECT record_id, record_type, data FROM pending_sync WHERE synced = 0 ORDER BY timestamp"
        )
        
        async with httpx.AsyncClient() as client:
            for row in cursor:
                record_id, record_type, data = row
                try:
                    response = await client.post(
                        f"{self.server_url}/api/v1/data/{record_type}",
                        json=json.loads(data),
                        headers={'Authorization': f'Bearer {self.get_token()}'},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        self.local_db.execute(
                            "UPDATE pending_sync SET synced = 1 WHERE record_id = ?",
                            (record_id,)
                        )
                    else:
                        # Keep in queue, log error
                        self.log_sync_error(record_id, response.status_code, response.text)
                        
                except httpx.ConnectError:
                    # Still offline, stop trying
                    break
        
        self.local_db.commit()
    
    def get_sync_status(self):
        """Return sync statistics for UI display"""
        total = self.local_db.execute("SELECT COUNT(*) FROM pending_sync").fetchone()[0]
        synced = self.local_db.execute("SELECT COUNT(*) FROM pending_sync WHERE synced = 1").fetchone()[0]
        pending = total - synced
        
        return {
            'total_records': total,
            'synced': synced,
            'pending': pending,
            'status': 'synced' if pending == 0 else f'{pending} pending'
        }
```

## Barcode and Sample Tracking

```python
class SampleTracker:
    """
    End-to-end sample tracking from field to lab
    """
    
    def generate_sample_id(self, project_code, sample_type, sequence):
        """
        Generate standardized sample ID
        Format: PRJ-TYP-YYYY-NNNN
        """
        year = datetime.now().year
        return f"{project_code}-{sample_type}-{year}-{sequence:04d}"
    
    def print_field_labels(self, sample_ids):
        """
        Generate PDF for thermal printer labels
        """
        from reportlab.lib.pagesizes import labels
        from reportlab.graphics.barcode import code128
        
        for sample_id in sample_ids:
            # QR code + human readable
            label = {
                'sample_id': sample_id,
                'qr_data': json.dumps({
                    'id': sample_id,
                    'project': project_code,
                    'created': datetime.now().isoformat()
                })
            }
            yield label
    
    def track_sample(self, sample_id, event, location, user):
        """
        Record sample chain of custody event
        """
        custody_record = {
            'sample_id': sample_id,
            'event': event,  # 'collected', 'shipped', 'received_lab', 'prepared', 'analyzed'
            'timestamp': datetime.utcnow().isoformat(),
            'location': location,
            'user': user,
            'condition': 'good',  # 'good', 'damaged', 'contaminated'
            'notes': ''
        }
        
        # Save to database
        save_custody_record(custody_record)
        
        return custody_record
```

## Field QA/QC

```python
FIELD_QC_RULES = {
    'sample_spacing': {
        'rock': 'minimum 10m between samples unless mineralized',
        'soil': 'regular grid 50m or 100m',
        'stream_sed': 'every 200m along drainage, at confluences'
    },
    'duplicates': {
        'frequency': '1 per 20 samples',
        'type': 'field_duplicate (same site, separate bag)'
    },
    'blanks': {
        'frequency': '1 per 50 samples',
        'material': 'quartz sand or barren granite',
        'purpose': 'detect contamination during crushing'
    },
    'standards': {
        'frequency': '1 per 20 samples',
        'types': ['low_grade', 'medium_grade', 'high_grade'],
        'purpose': 'verify lab accuracy'
    },
    'photos': {
        'every_sample': True,
        'requirements': ['in_situ', 'with_scale', 'with_label', 'GPS_metadata'],
        'backup': 'SD card + cloud sync daily'
    }
}

def validate_field_submission(submission):
    """
    Real-time validation before allowing submission
    """
    errors = []
    warnings = []
    
    # Check sample ID format
    if not re.match(r'^[A-Z]{3}-[A-Z]{2}-\d{4}-\d{4}$', submission['sample_id']):
        errors.append('Invalid sample ID format')
    
    # Check for photos
    if len(submission.get('photo_ids', [])) < 1:
        errors.append('At least one photo required')
    
    # Check GPS accuracy
    if submission.get('gps_accuracy', 100) > 10:
        warnings.append('GPS accuracy > 10m — consider re-taking')
    
    # Check for duplicate coordinates
    if is_near_existing_sample(submission['easting'], submission['northing'], radius=5):
        warnings.append('Within 5m of existing sample — duplicate?')
    
    return {'valid': len(errors) == 0, 'errors': errors, 'warnings': warnings}
```

## Best Practices

1. **Daily backup:** Sync all data at end of each field day. Never keep >1 day unsynced.
2. **Redundant GPS:** Log handheld GPS even if tablet has GPS (backup + verification).
3. **Photo metadata:** Ensure EXIF GPS, timestamp, and device ID are embedded.
4. **Sample security:** Lock samples in vehicle; never leave unattended at camp.
5. **Chain of custody:** Every handoff must be documented with signature/timestamp.
6. **Weather notes:** Rain can mobilize soil geochemistry — note recent weather.
