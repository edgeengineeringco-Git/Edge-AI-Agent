---
name: tenement-management
description: Tenement and license management for REE exploration — boundary tracking, compliance dates, work program obligations, and regulatory filing automation.
---

# Tenement Management System

## When to use

- You hold exploration licenses and need to track expiry dates, renewal deadlines, and work commitments.
- You need to map tenement boundaries against geological data and targets.
- You want automated reminders for filing deadlines and report submissions.
- You need to manage joint venture interests and royalty obligations.

## Tenement Data Model

```sql
CREATE TABLE tenements (
    id SERIAL PRIMARY KEY,
    tenement_id VARCHAR(50) UNIQUE NOT NULL,
    tenement_name VARCHAR(200),
    jurisdiction VARCHAR(100), -- 'Western Australia', 'Ontario', 'Namibia', etc.
    tenement_type VARCHAR(50), -- 'exploration_license', 'mining_lease', 'retention', 'prospecting_license'
    status VARCHAR(50), -- 'granted', 'pending', 'renewed', 'surrendered', 'expired', 'forfeited'
    
    -- Dates
    application_date DATE,
    grant_date DATE,
    expiry_date DATE,
    renewal_deadline DATE,
    
    -- Area
    area_km2 DECIMAL(10,2),
    area_ha DECIMAL(12,2),
    geom GEOMETRY(MULTIPOLYGON, 4326),
    
    -- Ownership
    holder_company VARCHAR(200),
    holder_percentage DECIMAL(5,2),
    joint_venture_partners JSONB, -- [{"company": "X", "percentage": 30}]
    
    -- Work program
    work_program_commitment TEXT,
    minimum_expenditure_usd DECIMAL(12,2),
    work_program_due_date DATE,
    work_program_submitted BOOLEAN DEFAULT FALSE,
    
    -- Regulatory
    environmental_approval_required BOOLEAN,
    environmental_approval_status VARCHAR(50),
    native_title_status VARCHAR(50),
    heritage_clearance_status VARCHAR(50),
    
    -- Obligations
    annual_rent_due_date DATE,
    annual_rent_amount DECIMAL(10,2),
    annual_rent_paid BOOLEAN DEFAULT FALSE,
    
    reporting_due_date DATE,
    reporting_submitted BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    notes TEXT
);

CREATE TABLE tenement_events (
    id SERIAL PRIMARY KEY,
    tenement_id VARCHAR(50) REFERENCES tenements(tenement_id),
    event_type VARCHAR(50), -- 'renewal', 'report_submission', 'rent_payment', 'inspection', 'dispute'
    event_date DATE,
    description TEXT,
    documents JSONB,
    created_by VARCHAR(100)
);

CREATE TABLE tenement_targets (
    id SERIAL PRIMARY KEY,
    tenement_id VARCHAR(50) REFERENCES tenements(tenement_id),
    target_id VARCHAR(50),
    target_name VARCHAR(200),
    priority VARCHAR(20), -- 'high', 'medium', 'low'
    status VARCHAR(50), -- 'target', 'exploration', 'drilling', 'resource_definition'
    geom GEOMETRY(POINT, 4326)
);
```

## Compliance Monitoring

```python
from datetime import datetime, timedelta
import pandas as pd

class TenementComplianceMonitor:
    def __init__(self, db_connection):
        self.db = db_connection
    
    async def get_upcoming_deadlines(self, days_ahead=90):
        """
        Get all tenements with deadlines in the next N days
        """
        query = """
            SELECT 
                tenement_id,
                tenement_name,
                jurisdiction,
                expiry_date,
                renewal_deadline,
                work_program_due_date,
                annual_rent_due_date,
                reporting_due_date,
                CASE 
                    WHEN renewal_deadline <= NOW() + INTERVAL '$1 days' THEN 'RENEWAL_DUE'
                    WHEN work_program_due_date <= NOW() + INTERVAL '$1 days' THEN 'WORK_PROGRAM_DUE'
                    WHEN annual_rent_due_date <= NOW() + INTERVAL '$1 days' THEN 'RENT_DUE'
                    WHEN reporting_due_date <= NOW() + INTERVAL '$1 days' THEN 'REPORT_DUE'
                    ELSE 'OK'
                END AS alert_type
            FROM tenements
            WHERE status IN ('granted', 'renewed')
            AND (
                renewal_deadline <= NOW() + INTERVAL '$1 days'
                OR work_program_due_date <= NOW() + INTERVAL '$1 days'
                OR annual_rent_due_date <= NOW() + INTERVAL '$1 days'
                OR reporting_due_date <= NOW() + INTERVAL '$1 days'
            )
            ORDER BY 
                LEAST(renewal_deadline, work_program_due_date, annual_rent_due_date, reporting_due_date)
        """
        
        rows = await self.db.fetch(query, days_ahead)
        return pd.DataFrame([dict(r) for r in rows])
    
    async def calculate_expenditure_to_date(self, tenement_id, year):
        """
        Sum all exploration expenditure against minimum commitment
        """
        query = """
            SELECT 
                t.minimum_expenditure_usd,
                COALESCE(SUM(e.amount_usd), 0) AS spent_usd
            FROM tenements t
            LEFT JOIN exploration_expenditure e 
                ON e.tenement_id = t.tenement_id 
                AND EXTRACT(YEAR FROM e.expenditure_date) = $2
            WHERE t.tenement_id = $1
            GROUP BY t.tenement_id, t.minimum_expenditure_usd
        """
        
        row = await self.db.fetchrow(query, tenement_id, year)
        if row:
            return {
                'minimum': row['minimum_expenditure_usd'],
                'spent': row['spent_usd'],
                'remaining': row['minimum_expenditure_usd'] - row['spent_usd'],
                'pct_complete': (row['spent_usd'] / row['minimum_expenditure_usd'] * 100) if row['minimum_expenditure_usd'] > 0 else 100
            }
        return None
    
    async def generate_compliance_report(self, jurisdiction=None):
        """
        Generate compliance status report for all tenements
        """
        query = """
            SELECT 
                tenement_id,
                tenement_name,
                status,
                expiry_date,
                renewal_deadline,
                work_program_submitted,
                annual_rent_paid,
                reporting_submitted,
                CASE 
                    WHEN expiry_date < NOW() THEN 'EXPIRED'
                    WHEN expiry_date < NOW() + INTERVAL '180 days' THEN 'EXPIRING_SOON'
                    ELSE 'ACTIVE'
                END AS health_status
            FROM tenements
            WHERE status IN ('granted', 'renewed')
        """
        
        if jurisdiction:
            query += f" AND jurisdiction = '{jurisdiction}'"
        
        rows = await self.db.fetch(query)
        return pd.DataFrame([dict(r) for r in rows])
```

## Automated Alerts

```python
async def send_compliance_alerts(monitor, dm_skill):
    """
    Send Telegram alerts for upcoming deadlines
    """
    deadlines = await monitor.get_upcoming_deadlines(days_ahead=60)
    
    for _, row in deadlines.iterrows():
        days_remaining = (row['renewal_deadline'] - datetime.now().date()).days
        
        if days_remaining <= 30:
            urgency = "🚨 URGENT"
        elif days_remaining <= 60:
            urgency = "⚠️ WARNING"
        else:
            urgency = "ℹ️ REMINDER"
        
        message = f"""
{urgency} Tenement Deadline

Tenement: {row['tenement_id']} - {row['tenement_name']}
Jurisdiction: {row['jurisdiction']}
Alert: {row['alert_type']}
Days remaining: {days_remaining}

Action required immediately.
        """
        
        await dm_skill.broadcast(message)
```

## Tenement vs. Target Spatial Analysis

```python
async def targets_by_tenement(db, tenement_id):
    """
    Get all exploration targets within a tenement
    """
    query = """
        SELECT t.*
        FROM targets t
        JOIN tenements ten ON ST_Contains(ten.geom, t.geom)
        WHERE ten.tenement_id = $1
        ORDER BY t.priority, t.mean_treo_pct DESC
    """
    
    rows = await db.fetch(query, tenement_id)
    return rows

async def tenement_coverage_analysis(db, geological_unit_table):
    """
    Analyze what geological units are covered by each tenement
    """
    query = """
        SELECT 
            ten.tenement_id,
            ten.tenement_name,
            gu.unit_code,
            gu.unit_name,
            gu.lithology,
            ST_Area(ST_Intersection(ten.geom, gu.geom)::geography) / 10000 AS overlap_ha
        FROM tenements ten
        JOIN geological_units gu ON ST_Intersects(ten.geom, gu.geom)
        WHERE ten.status IN ('granted', 'renewed')
        ORDER BY ten.tenement_id, overlap_ha DESC
    """
    
    rows = await db.fetch(query)
    return pd.DataFrame([dict(r) for r in rows])
```

## Jurisdiction-Specific Rules

| Jurisdiction | Renewal Period | Min Expenditure | Key Requirements |
|---|---|---|---|
| **Western Australia** | 5 years (E) | A$10,000–50,000/yr | Annual reporting, minimum metres drilled |
| **Northern Territory** | 6 years (EL) | A$20,000–100,000/yr | Work program approval required |
| **Queensland** | 5 years (EPM) | A$10,000–100,000/yr | Financial assurance, rehab bond |
| **Ontario (Canada)** | 3 years (Claim) | CAD$400/claim/unit | Assessment work filings |
| **Namibia** | 3 years ( EPL) | Variable | Environmental clearance |
| **Tanzania** | 4 years (PL) | Variable | Local content requirements |

## Best Practices

1. **Calendar integration:** Sync all deadlines to Google Calendar / Outlook.
2. **Document repository:** Store all applications, approvals, and reports in versioned storage.
3. **Audit trail:** Every status change logged with user and timestamp.
4. **Budget tracking:** Real-time expenditure vs. commitment tracking.
5. **JV notifications:** Alert all partners 90 days before any deadline.
6. **GIS integration:** Tenement boundaries always up-to-date in mapping system.
