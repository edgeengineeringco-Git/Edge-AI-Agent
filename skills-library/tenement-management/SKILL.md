---
name: tenement-management
description: Tenement and license management for REE and critical mineral exploration — boundary mapping, compliance tracking, expenditure reporting, and renewal automation.
---

# Tenement Management

## When to use

- You need to track exploration license boundaries and expiry dates.
- You want to ensure minimum expenditure commitments are met.
- You need to manage landowner agreements and access permissions.
- You want automated alerts for renewals, reporting deadlines, and compliance.

## Tenement Data Model

```python
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Optional

@dataclass
class Tenement:
    tenement_id: str           # e.g., "EL12345"
    tenement_type: str         # "EL" (Exploration License), "ML" (Mining Lease), "EPM"
    jurisdiction: str          # "Queensland", "Western Australia", "Ontario", etc.
    status: str                # "granted", "application", "renewal_pending", "expired", "surrendered"
    
    # Dates
    application_date: date
    grant_date: Optional[date]
    expiry_date: Optional[date]
    renewal_date: Optional[date]
    
    # Spatial
    area_km2: float
    boundary_wkt: str          # Well-known text polygon
    centroid_easting: float
    centroid_northing: float
    crs: str = "EPSG:4326"
    
    # Obligations
    min_expenditure_annual: float  # Local currency
    min_expenditure_currency: str
    reporting_frequency_months: int
    next_report_due: date
    
    # Land access
    land_type: str             # "crown", "freehold", "native_title", "mixed"
    native_title_claim: Optional[str]
    landowner_agreements: List[str]
    
    # History
    previous_owners: List[str]
    previous_tenement_ids: List[str]
    
    def days_to_expiry(self):
        if self.expiry_date:
            return (self.expiry_date - date.today()).days
        return None
    
    def is_compliant(self, expenditure_ytd: float):
        if self.min_expenditure_annual:
            return expenditure_ytd >= self.min_expenditure_annual
        return True
    
    def renewal_urgency(self):
        days = self.days_to_expiry()
        if days is None:
            return "unknown"
        if days < 30:
            return "critical"
        elif days < 90:
            return "urgent"
        elif days < 180:
            return "planning"
        return "ok"
```

## Compliance Tracking

```python
class TenementComplianceTracker:
    """
    Track all compliance obligations across tenement portfolio
    """
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    async def get_upcoming_deadlines(self, days_ahead=90):
        """
        Get all deadlines within the next N days
        """
        deadline_types = [
            'expiry', 'renewal_application', 'annual_report', 
            'expenditure_report', 'environmental_report',
            'rental_payment', 'landowner_meeting'
        ]
        
        deadlines = []
        for dtype in deadline_types:
            rows = await self.db.fetch("""
                SELECT t.tenement_id, t.jurisdiction, d.deadline_date, d.deadline_type, d.description
                FROM tenements t
                JOIN tenement_deadlines d ON t.tenement_id = d.tenement_id
                WHERE d.deadline_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '%s days'
                AND d.completed = FALSE
                ORDER BY d.deadline_date
            """, days_ahead)
            
            deadlines.extend(rows)
        
        return deadlines
    
    async def check_expenditure_compliance(self, financial_year):
        """
        Check if all tenements meet minimum expenditure
        """
        results = await self.db.fetch("""
            SELECT 
                t.tenement_id,
                t.min_expenditure_annual,
                COALESCE(SUM(e.amount), 0) as spent
            FROM tenements t
            LEFT JOIN expenditure e ON t.tenement_id = e.tenement_id
                AND e.financial_year = $1
            WHERE t.status = 'granted'
            GROUP BY t.tenement_id, t.min_expenditure_annual
        """, financial_year)
        
        non_compliant = []
        for r in results:
            if r['spent'] < r['min_expenditure_annual']:
                non_compliant.append({
                    'tenement_id': r['tenement_id'],
                    'required': r['min_expenditure_annual'],
                    'spent': r['spent'],
                    'shortfall': r['min_expenditure_annual'] - r['spent']
                })
        
        return non_compliant
    
    async def generate_renewal_application(self, tenement_id):
        """
        Auto-generate renewal application package
        """
        tenement = await self.get_tenement(tenement_id)
        
        # Gather required documents
        documents = {
            'expenditure_report': await self.get_expenditure_report(tenement_id),
            'activity_report': await self.get_activity_report(tenement_id),
            'environmental_report': await self.get_environmental_report(tenement_id),
            'work_program': await self.generate_work_program(tenement_id),
            'boundary_map': await self.generate_boundary_map(tenement_id),
            'landowner_consents': await self.get_landowner_consents(tenement_id)
        }
        
        # Check completeness
        missing = [k for k, v in documents.items() if v is None]
        
        return {
            'tenement_id': tenement_id,
            'documents': documents,
            'complete': len(missing) == 0,
            'missing': missing,
            'submission_deadline': tenement.expiry_date - timedelta(days=30)
        }
```

## Expenditure Categories

```python
EXPENDITURE_CATEGORIES = {
    'exploration': {
        'drilling': ['diamond_drilling', 'rc_drilling', 'ac_drilling', 'geotech_drilling'],
        'geophysics': ['magnetic_survey', 'gravity_survey', 'radiometric_survey', 'em_survey', 'ip_survey'],
        'geochemistry': ['soil_sampling', 'rock_sampling', 'stream_sampling', 'drill_assaying', 'pxrf'],
        'remote_sensing': ['satellite_imagery', 'drone_survey', 'aerial_photo'],
        'mapping': ['geological_mapping', 'structural_mapping', 'regolith_mapping']
    },
    'studies': {
        'resource_estimation': ['geostatistics', 'resource_model', 'independent_review'],
        'metallurgical': ['testwork', 'pilot_plant', 'process_design'],
        'environmental': ['baseline_study', 'eia', 'hydrology_study'],
        'engineering': ['mining_study', 'infrastructure_study', 'capex_estimate']
    },
    'administration': {
        'permits': ['license_fees', 'rental_fees', 'legal_fees'],
        'community': ['consultation', 'benefit_sharing', 'compensation'],
        'overhead': ['salaries', 'camp_costs', 'vehicle_costs', 'insurance']
    }
}
```

## Automated Alerts

```python
class TenementAlertEngine:
    """
    Generate alerts for tenement management
    """
    
    async def generate_alerts(self):
        alerts = []
        
        # 1. Expiry alerts
        expiring = await self.db.fetch("""
            SELECT tenement_id, expiry_date
            FROM tenements
            WHERE expiry_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '6 months'
            AND status = 'granted'
        """)
        
        for t in expiring:
            days_remaining = (t['expiry_date'] - date.today()).days
            if days_remaining < 30:
                priority = 'critical'
            elif days_remaining < 90:
                priority = 'high'
            else:
                priority = 'medium'
            
            alerts.append({
                'type': 'expiry',
                'tenement_id': t['tenement_id'],
                'priority': priority,
                'message': f"Tenement {t['tenement_id']} expires in {days_remaining} days",
                'action_required': 'Submit renewal application'
            })
        
        # 2. Expenditure shortfall
        fy = get_current_financial_year()
        shortfalls = await self.check_expenditure_compliance(fy)
        
        for s in shortfalls:
            months_remaining = 12 - date.today().month + 1
            alerts.append({
                'type': 'expenditure',
                'tenement_id': s['tenement_id'],
                'priority': 'high',
                'message': f"Expenditure shortfall: ${s['shortfall']:,.0f} remaining {months_remaining} months",
                'action_required': 'Accelerate exploration activities'
            })
        
        # 3. Reporting deadlines
        reports = await self.db.fetch("""
            SELECT tenement_id, deadline_date, deadline_type
            FROM tenement_deadlines
            WHERE deadline_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '3 months'
            AND completed = FALSE
        """)
        
        for r in reports:
            alerts.append({
                'type': 'reporting',
                'tenement_id': r['tenement_id'],
                'priority': 'medium',
                'message': f"{r['deadline_type']} due {r['deadline_date']}",
                'action_required': 'Prepare and submit report'
            })
        
        return sorted(alerts, key=lambda x: ['critical', 'high', 'medium', 'low'].index(x['priority']))
```

## Best Practices

1. **Calendar integration:** Sync all deadlines to Google Calendar / Outlook with reminders.
2. **Document vault:** Store all tenement documents in version-controlled repository.
3. **Spatial overlap check:** Before applying for new ground, check for overlaps with existing tenements.
4. **Native title:** Always check native title status before applying — can add 6–12 months.
5. **Expenditure documentation:** Keep all receipts and timesheets — regulators audit randomly.
6. **Renewal buffer:** Start renewal process 6 months before expiry.
7. **Multi-jurisdiction:** Each state/country has different rules — maintain separate playbooks.
