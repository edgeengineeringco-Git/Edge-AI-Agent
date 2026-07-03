---
name: database-geospatial
description: Design and manage geospatial databases for REE prospecting — PostGIS schema, SQLite/SpatiaLite for field use, data ingestion pipelines, and spatial queries for exploration datasets.
---

# Geospatial Database Design for REE Exploration

## When to use

- You need to store and query drill hole, geochemical, geophysical, and geological map data spatially.
- You want to perform spatial joins (e.g., samples within a geological unit).
- You need to serve data to a web map or API.
- You want version control on your exploration data.

## Database Options

| Database | Best For | Pros | Cons |
|---|---|---|---|
| **PostGIS** | Central server, multi-user, web services | Full-featured, scalable, SQL standard | Requires PostgreSQL server |
| **SpatiaLite** | Single-user, field laptop, offline | SQLite-based, portable, zero config | Limited concurrency |
| **GeoPackage** | Data exchange, mobile apps | OGC standard, single file | Read-optimized |
| **GeoParquet** | Cloud analytics, large datasets | Columnar, fast queries | Emerging standard |

## Recommended Schema

### PostgreSQL + PostGIS

```sql
-- Enable PostGIS
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;

-- 1. Project / Tenement table
CREATE TABLE tenements (
    id SERIAL PRIMARY KEY,
    tenement_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200),
    status VARCHAR(50), -- 'granted', 'application', 'expired'
    grant_date DATE,
    expiry_date DATE,
    area_km2 DECIMAL(10,2),
    owner VARCHAR(200),
    geom GEOMETRY(MULTIPOLYGON, 4326),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_tenements_geom ON tenements USING GIST(geom);

-- 2. Drill holes
CREATE TABLE drill_holes (
    id SERIAL PRIMARY KEY,
    hole_id VARCHAR(50) UNIQUE NOT NULL,
    tenement_id VARCHAR(50) REFERENCES tenements(tenement_id),
    hole_type VARCHAR(50), -- 'diamond', 'rc', 'ac', 'rabbitt'
    easting DECIMAL(12,2),
    northing DECIMAL(12,2),
    elevation DECIMAL(8,2),
    crs VARCHAR(20) DEFAULT 'EPSG:32733',
    azimuth DECIMAL(5,2),
    dip DECIMAL(5,2),
    total_depth DECIMAL(8,2),
    date_drilled DATE,
    contractor VARCHAR(100),
    geom GEOMETRY(POINT, 4326),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_drill_holes_geom ON drill_holes USING GIST(geom);

-- 3. Assay / geochemistry
CREATE TABLE assays (
    id SERIAL PRIMARY KEY,
    hole_id VARCHAR(50) REFERENCES drill_holes(hole_id),
    sample_id VARCHAR(50) NOT NULL,
    sample_type VARCHAR(50), -- 'drill', 'rock', 'soil', 'stream'
    from_m DECIMAL(8,2),
    to_m DECIMAL(8,2),
    interval_m DECIMAL(8,2) GENERATED ALWAYS AS (to_m - from_m) STORED,
    lab VARCHAR(100),
    analysis_method VARCHAR(50), -- 'ICP-MS', 'pXRF', 'XRF', 'AAS'
    
    -- REE elements (ppm)
    la_ppm DECIMAL(10,3),
    ce_ppm DECIMAL(10,3),
    pr_ppm DECIMAL(10,3),
    nd_ppm DECIMAL(10,3),
    sm_ppm DECIMAL(10,3),
    eu_ppm DECIMAL(10,3),
    gd_ppm DECIMAL(10,3),
    tb_ppm DECIMAL(10,3),
    dy_ppm DECIMAL(10,3),
    ho_ppm DECIMAL(10,3),
    er_ppm DECIMAL(10,3),
    tm_ppm DECIMAL(10,3),
    yb_ppm DECIMAL(10,3),
    lu_ppm DECIMAL(10,3),
    y_ppm DECIMAL(10,3),
    sc_ppm DECIMAL(10,3),
    
    -- Pathfinders
    th_ppm DECIMAL(10,3),
    u_ppm DECIMAL(10,3),
    nb_ppm DECIMAL(10,3),
    ta_ppm DECIMAL(10,3),
    zr_ppm DECIMAL(10,3),
    hf_ppm DECIMAL(10,3),
    sr_ppm DECIMAL(10,3),
    ba_ppm DECIMAL(10,3),
    
    -- Computed grades
    treo_pct DECIMAL(8,4),
    hreo_treo_ratio DECIMAL(6,4),
    creo_pct DECIMAL(8,4),
    
    -- QA/QC
    qc_type VARCHAR(50), -- 'blank', 'crm', 'duplicate', 'sample'
    qc_passed BOOLEAN,
    
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_assays_hole ON assays(hole_id);
CREATE INDEX idx_assays_treo ON assays(treo_pct);

-- 4. Geological units
CREATE TABLE geological_units (
    id SERIAL PRIMARY KEY,
    unit_code VARCHAR(50),
    unit_name VARCHAR(200),
    lithology VARCHAR(200),
    age VARCHAR(100),
    description TEXT,
    geom GEOMETRY(MULTIPOLYGON, 4326)
);
CREATE INDEX idx_geol_units_geom ON geological_units USING GIST(geom);

-- 5. Structural features
CREATE TABLE structures (
    id SERIAL PRIMARY KEY,
    feature_id VARCHAR(50),
    feature_type VARCHAR(50), -- 'fault', 'fold', 'shear', 'joint'
    azimuth DECIMAL(5,2),
    dip DECIMAL(5,2),
    dip_direction DECIMAL(5,2),
    length_m DECIMAL(10,2),
    description TEXT,
    geom GEOMETRY(LINESTRING, 4326)
);
CREATE INDEX idx_structures_geom ON structures USING GIST(geom);

-- 6. Anomalies / Targets
CREATE TABLE targets (
    id SERIAL PRIMARY KEY,
    target_id VARCHAR(50) UNIQUE,
    target_name VARCHAR(200),
    target_type VARCHAR(50), -- 'geochem', 'geophys', 'satellite', 'combined'
    priority VARCHAR(20), -- 'high', 'medium', 'low'
    mean_treo_pct DECIMAL(8,4),
    area_m2 DECIMAL(12,2),
    classification VARCHAR(50), -- 'inferred', 'indicated', 'measured'
    discovery_date DATE,
    status VARCHAR(50), -- 'target', 'prospect', 'advanced', 'mine'
    notes TEXT,
    geom GEOMETRY(MULTIPOLYGON, 4326)
);
CREATE INDEX idx_targets_geom ON targets USING GIST(geom);
```

## Essential Spatial Queries

```sql
-- Samples within 500m of a fault
SELECT a.sample_id, a.treo_pct, s.feature_id,
       ST_Distance(a.geom::geography, s.geom::geography) AS distance_m
FROM assays a
JOIN structures s ON ST_DWithin(a.geom::geography, s.geom::geography, 500)
WHERE s.feature_type = 'fault'
  AND a.treo_pct > 0.5
ORDER BY distance_m;

-- Average TREO by geological unit
SELECT g.unit_code, g.unit_name,
       COUNT(a.id) AS n_samples,
       AVG(a.treo_pct) AS avg_treo,
       MAX(a.treo_pct) AS max_treo
FROM geological_units g
JOIN assays a ON ST_Contains(g.geom, a.geom)
GROUP BY g.unit_code, g.unit_name
ORDER BY avg_treo DESC;

-- Drill holes inside a tenement
SELECT dh.hole_id, dh.total_depth, dh.date_drilled
FROM drill_holes dh
JOIN tenements t ON ST_Contains(t.geom, dh.geom)
WHERE t.tenement_id = 'EL12345';

-- Nearest 10 samples to a new target point
SELECT sample_id, treo_pct, hreo_treo_ratio,
       ST_Distance(geom, ST_SetSRID(ST_MakePoint(123456, 7890123), 32733)) AS dist_m
FROM assays
WHERE geom IS NOT NULL
ORDER BY geom <-> ST_SetSRID(ST_MakePoint(123456, 7890123), 32733)
LIMIT 10;

-- Create a 500m buffer around high-grade zones
INSERT INTO targets (target_id, target_name, geom)
SELECT 
    'BUF_' || a.hole_id,
    'Buffer around ' || a.hole_id,
    ST_Buffer(ST_Collect(a.geom)::geography, 500)::geometry
FROM assays a
WHERE a.treo_pct > 1.0
GROUP BY a.hole_id;
```

## Python Ingestion Pipeline

```python
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
from shapely.geometry import Point
import geopandas as gpd

def ingest_drill_data(df, db_config):
    """
    Ingest drill hole and assay data from DataFrame to PostGIS
    df must have: hole_id, easting, northing, elevation, ...
    """
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    
    # 1. Insert drill holes
    drill_data = []
    for _, row in df[['hole_id', 'easting', 'northing', 'elevation']].drop_duplicates().iterrows():
        point = Point(row['easting'], row['northing'])
        drill_data.append((
            row['hole_id'], row['easting'], row['northing'], 
            row['elevation'], point.wkt
        ))
    
    execute_values(cur, """
        INSERT INTO drill_holes (hole_id, easting, northing, elevation, geom)
        VALUES %s
        ON CONFLICT (hole_id) DO NOTHING
    """, drill_data, template="(%s, %s, %s, %s, ST_GeomFromText(%s, 32733))")
    
    # 2. Insert assays
    assay_cols = ['hole_id', 'sample_id', 'from_m', 'to_m', 'la_ppm', 'ce_ppm', ...]
    assay_data = [tuple(row[c] for c in assay_cols) for _, row in df.iterrows()]
    
    execute_values(cur, """
        INSERT INTO assays (hole_id, sample_id, from_m, to_m, la_ppm, ce_ppm, ...)
        VALUES %s
    """, assay_data)
    
    conn.commit()
    cur.close()
    conn.close()
```

## SpatiaLite for Field Use

```python
import sqlite3

conn = sqlite3.connect('field_data.sqlite')
conn.enable_load_extension(True)
conn.execute('SELECT load_extension("mod_spatialite")')
conn.execute("SELECT InitSpatialMetaData()")

# Create spatial table
conn.execute("""
    CREATE TABLE field_samples (
        id INTEGER PRIMARY KEY,
        sample_id TEXT,
        treo_pct REAL,
        notes TEXT
    )
""")
conn.execute("""
    SELECT AddGeometryColumn('field_samples', 'geom', 4326, 'POINT', 'XY')
""")

# Insert with geometry
conn.execute("""
    INSERT INTO field_samples (sample_id, treo_pct, geom)
    VALUES (?, ?, MakePoint(?, ?, 4326))
""", ('S001', 1.23, 10.5, 45.2))

conn.commit()
```

## Best Practices

1. **CRS consistency:** Store everything in a project CRS (e.g., UTM zone). Only convert to 4326 for web maps.
2. **Composite key constraints:** `(hole_id, from_m, to_m)` should be unique to prevent duplicate intervals.
3. **Triggers for computed fields:** Auto-calculate `treo_pct` on insert/update:
   ```sql
   CREATE TRIGGER calc_treo BEFORE INSERT ON assays
   FOR EACH ROW EXECUTE FUNCTION compute_treo();
   ```
4. **Partitioning:** For large datasets (>10M samples), partition by `hole_id` or date.
5. **Backups:** `pg_dump` daily. Store in version-controlled SQL migrations.
6. **Validation:** Check ranges on insert (e.g., `treo_pct` must be 0–100).
