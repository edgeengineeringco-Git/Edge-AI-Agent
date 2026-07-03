---
name: api-gateway
description: Design and implement REST APIs and webhooks for the REE prospecting platform — FastAPI architecture, authentication, data ingestion endpoints, and integration patterns.
---

# API Gateway for REE Prospecting Platform

## When to use

- You need to expose platform capabilities to external tools or mobile apps.
- You want a webhook-based pipeline (e.g., pXRF uploads → processing → notification).
- You need to integrate with Google Drive, Telegram, or other cloud services.
- You want a microservices architecture for scaling.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Clients   │────▶│  API Gateway │────▶│  Auth (OAuth2)  │
│  (Web/App)  │     │   (FastAPI)  │     └─────────────────┘
└─────────────┘     └──────────────┘              │
                           │                      │
              ┌────────────┼────────────┐        │
              ▼            ▼            ▼        │
        ┌─────────┐  ┌──────────┐  ┌─────────┐  │
        │  Data   │  │ Processing│  │ Report  │  │
        │ Services│  │ Services │  │ Services│  │
        └─────────┘  └──────────┘  └─────────┘  │
              │            │            │        │
              └────────────┴────────────┘        │
                           │                     │
                    ┌──────▼──────┐              │
                    │  PostgreSQL │◀─────────────┘
                    │  + PostGIS  │
                    └─────────────┘
```

## FastAPI Implementation

```python
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn
import json

app = FastAPI(
    title="EDGE Prospector AI API",
    description="Geochemical and geospatial processing for REE exploration",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ─── Models ───

class GeochemSample(BaseModel):
    sample_id: str
    easting: float
    northing: float
    elevation: Optional[float] = None
    la_ppm: Optional[float] = None
    ce_ppm: Optional[float] = None
    # ... all REE elements
    treo_pct: Optional[float] = None

class DrillHole(BaseModel):
    hole_id: str
    easting: float
    northing: float
    elevation: float
    azimuth: float
    dip: float
    total_depth: float
    date_drilled: str

class ProcessingJob(BaseModel):
    job_id: str
    status: str  # 'queued', 'running', 'completed', 'failed'
    input_file: str
    output_url: Optional[str] = None
    created_at: str

# ─── Authentication ───

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Verify JWT token
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

# ─── Endpoints ───

@app.post("/auth/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 token endpoint"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/data/samples/bulk", response_model=ProcessingJob)
async def upload_samples(
    samples: List[GeochemSample],
    background_tasks: BackgroundTasks,
    user = Depends(get_current_user)
):
    """
    Bulk upload geochemical samples
    """
    job_id = generate_job_id()
    
    # Queue processing
    background_tasks.add_task(process_samples_job, job_id, samples, user.username)
    
    return ProcessingJob(
        job_id=job_id,
        status='queued',
        input_file=f'bulk_{job_id}.json',
        created_at=datetime.now().isoformat()
    )

@app.post("/data/drill-holes")
async def create_drill_hole(
    hole: DrillHole,
    user = Depends(get_current_user)
):
    """
    Create a new drill hole record
    """
    hole_id = await insert_drill_hole(hole)
    return {"hole_id": hole_id, "status": "created"}

@app.post("/processing/qc")
async def run_qc(
    survey_id: str,
    background_tasks: BackgroundTasks,
    user = Depends(get_current_user)
):
    """
    Run QC checks on a survey dataset
    """
    job_id = generate_job_id()
    background_tasks.add_task(run_qc_job, job_id, survey_id)
    return {"job_id": job_id, "status": "queued"}

@app.post("/processing/anomaly")
async def detect_anomalies(
    survey_id: str,
    eps: float = 100.0,
    min_samples: int = 5,
    user = Depends(get_current_user)
):
    """
    Run DBSCAN anomaly detection on a survey
    """
    clusters = await run_anomaly_detection(survey_id, eps, min_samples)
    return {
        "survey_id": survey_id,
        "n_clusters": len(clusters),
        "clusters": clusters
    }

@app.post("/processing/resource")
async def estimate_resource(
    cluster_id: str,
    bulk_density: float = 2.5,
    depth: float = 50.0,
    user = Depends(get_current_user)
):
    """
    Estimate resources for an anomaly cluster
    """
    resource = await calculate_resource(cluster_id, bulk_density, depth)
    return resource

@app.get("/data/samples/nearby")
async def get_nearby_samples(
    easting: float,
    northing: float,
    radius_m: float = 500.0,
    user = Depends(get_current_user)
):
    """
    Get samples within radius of a point
    """
    samples = await query_nearby_samples(easting, northing, radius_m)
    return samples

@app.get("/reports/survey/{survey_id}")
async def get_survey_report(
    survey_id: str,
    format: str = "html",  # or 'pdf'
    user = Depends(get_current_user)
):
    """
    Generate and download survey report
    """
    report_path = await generate_report(survey_id, format)
    return FileResponse(report_path)

@app.post("/webhooks/pxrf-upload")
async def webhook_pxrf_upload(
    file: UploadFile = File(...),
    api_key: str = Header(...)
):
    """
    Webhook for pXRF instrument uploads
    Authenticated via API key (instrument-specific)
    """
    if not verify_instrument_key(api_key):
        raise HTTPException(status_code=403, detail="Invalid instrument key")
    
    contents = await file.read()
    job_id = await queue_pxrf_processing(contents)
    
    return {"job_id": job_id, "status": "received"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# ─── Run ───
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Webhook Patterns

```python
# Async webhook dispatcher
import httpx
import asyncio

async def dispatch_webhook(event_type: str, payload: dict, url: str):
    """
    Dispatch webhook with retry logic
    """
    headers = {
        "X-Webhook-Signature": generate_signature(payload),
        "Content-Type": "application/json"
    }
    
    for attempt in range(3):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=30)
                if response.status_code < 400:
                    return True
        except Exception as e:
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    # Log failure
    await log_webhook_failure(event_type, url, payload)
    return False
```

## API Design Principles

1. **Versioning:** `/v1/data/samples`, `/v2/data/samples`
2. **Pagination:** `?limit=50&offset=100`
3. **Filtering:** `?treo_min=0.5&date_from=2026-01-01`
4. **Sorting:** `?sort=-treo_pct` (descending)
5. **Rate limiting:** 100 req/min for standard, 1000 req/min for premium
6. **Idempotency:** `Idempotency-Key` header for POST requests
7. **Async jobs:** Return job ID immediately, poll `/jobs/{job_id}` for status

## Authentication

```python
# JWT token with role-based access
from jose import jwt

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_access_token(username: str, role: str, expires_delta: timedelta = timedelta(hours=8)):
    to_encode = {
        "sub": username,
        "role": role,
        "exp": datetime.utcnow() + expires_delta
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Roles
ROLES = {
    'viewer': ['GET'],
    'geologist': ['GET', 'POST'],
    'admin': ['GET', 'POST', 'PUT', 'DELETE']
}
```

## Best Practices

1. **Validate inputs:** Use Pydantic models strictly.
2. **Sanitize file uploads:** Check MIME types, scan for malware.
3. **Log everything:** API calls, errors, data access for audit trails.
4. **Rate limit:** Prevent abuse and ensure fair use.
5. **Cache reads:** Redis for frequently accessed data.
6. **Queue heavy tasks:** Celery or RQ for background processing.
7. **Monitor:** Prometheus + Grafana for API health metrics.
