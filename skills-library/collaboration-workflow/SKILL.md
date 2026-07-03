---
name: collaboration-workflow
description: Multi-user collaboration, role-based access control, audit logging, and workflow state management for exploration teams using the REE prospecting platform.
---

# Collaboration and Workflow Management

## When to use

- Multiple geologists need to work on the same project simultaneously.
- You need role-based permissions (viewer, geologist, manager, admin).
- You want audit trails for data changes and decisions.
- You need workflow state machines (e.g., Target → Prospect → Advanced → Mine).

## User Roles and Permissions

| Role | Permissions | Typical User |
|---|---|---|
| **Viewer** | Read-only access to reports and maps | Investors, regulators |
| **Field Geologist** | Upload field data, view own data | Junior geologists |
| **Senior Geologist** | All data CRUD, run analyses, write reports | Project geologists |
| **Project Manager** | Manage team, approve budgets, view all | Project manager |
| **Competent Person** | Sign off on resource estimates, final reports | CP/QP |
| **Admin** | Full system access, user management | IT/Platform admin |

## Workflow State Machine

```python
from enum import Enum

class TargetStatus(str, Enum):
    GENERATED = "generated"           # AI/targeting generated
    FIELD_CHECKED = "field_checked"   # Field visit completed
    SAMPLED = "sampled"               # Geochemical samples collected
    ANOMALOUS = "anomalous"           # Confirmed geochemical anomaly
    DRILL_READY = "drill_ready"       # Approved for drilling
    DRILLING = "drilling"             # Drill program in progress
    MINERALIZED = "mineralized"       # Drilling confirmed mineralization
    RESOURCE = "resource"             # JORC resource estimated
    ADVANCED = "advanced"             # PFS/DFS completed
    MINE = "mine"                     # Production
    ABANDONED = "abandoned"           # Decision to cease

class TransitionRules:
    """
    Valid state transitions and required approvals
    """
    RULES = {
        TargetStatus.GENERATED: [TargetStatus.FIELD_CHECKED, TargetStatus.ABANDONED],
        TargetStatus.FIELD_CHECKED: [TargetStatus.SAMPLED, TargetStatus.ABANDONED],
        TargetStatus.SAMPLED: [TargetStatus.ANOMALOUS, TargetStatus.ABANDONED],
        TargetStatus.ANOMALOUS: [TargetStatus.DRILL_READY, TargetStatus.ABANDONED],
        TargetStatus.DRILL_READY: [TargetStatus.DRILLING],
        TargetStatus.DRILLING: [TargetStatus.MINERALIZED, TargetStatus.ABANDONED],
        TargetStatus.MINERALIZED: [TargetStatus.RESOURCE, TargetStatus.ADVANCED],
        TargetStatus.RESOURCE: [TargetStatus.ADVANCED],
        TargetStatus.ADVANCED: [TargetStatus.MINE, TargetStatus.ABANDONED]
    }
    
    REQUIRED_APPROVALS = {
        TargetStatus.DRILL_READY: ['senior_geologist', 'project_manager'],
        TargetStatus.RESOURCE: ['competent_person'],
        TargetStatus.ABANDONED: ['project_manager']
    }
    
    @classmethod
    def can_transition(cls, from_status, to_status, user_role):
        if to_status not in cls.RULES.get(from_status, []):
            return False
        
        required = cls.REQUIRED_APPROVALS.get(to_status, [])
        if required and user_role not in required:
            return False
        
        return True
```

## Audit Logging

```python
import json
from datetime import datetime
from typing import Dict, Any

class AuditLogger:
    """
    Immutable audit trail for all data changes and decisions
    """
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    async def log_event(
        self,
        event_type: str,  # 'data_create', 'data_update', 'data_delete', 'state_change', 'report_sign'
        user_id: str,
        entity_type: str,  # 'sample', 'drill_hole', 'target', 'report'
        entity_id: str,
        old_value: Dict[str, Any],
        new_value: Dict[str, Any],
        ip_address: str,
        notes: str = ""
    ):
        """
        Log an auditable event
        """
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'old_value': json.dumps(old_value),
            'new_value': json.dumps(new_value),
            'ip_address': ip_address,
            'notes': notes,
            'hash': self._compute_hash(old_value, new_value, timestamp)
        }
        
        await self.db.execute("""
            INSERT INTO audit_log (timestamp, event_type, user_id, entity_type, 
                                 entity_id, old_value, new_value, ip_address, notes, hash)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """, *event.values())
    
    def _compute_hash(self, *data):
        """Tamper-evident hash chain"""
        import hashlib
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

# Audit log table schema
"""
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    old_value JSONB,
    new_value JSONB,
    ip_address INET,
    notes TEXT,
    hash VARCHAR(64) NOT NULL,
    previous_hash VARCHAR(64)
);
"""
```

## Comment and Annotation System

```python
class AnnotationSystem:
    """
    Contextual comments on maps, sections, and data points
    """
    
    async def add_annotation(
        self,
        user_id: str,
        entity_type: str,  # 'map', 'section', 'sample', 'target'
        entity_id: str,
        annotation_type: str,  # 'comment', 'measurement', 'interpretation', 'flag'
        content: str,
        geometry: dict = None,  # GeoJSON point/line/polygon
        attachments: list = None
    ):
        annotation = {
            'annotation_id': generate_uuid(),
            'user_id': user_id,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'annotation_type': annotation_type,
            'content': content,
            'geometry': json.dumps(geometry) if geometry else None,
            'attachments': attachments or [],
            'created_at': datetime.utcnow().isoformat(),
            'resolved': False,
            'parent_id': None  # For threaded discussions
        }
        
        await self.db.execute("""
            INSERT INTO annotations 
            (annotation_id, user_id, entity_type, entity_id, annotation_type, 
             content, geometry, attachments, created_at, resolved, parent_id)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        """, *annotation.values())
        
        return annotation['annotation_id']
    
    async def get_annotations_for_entity(self, entity_type, entity_id):
        """Get all annotations for a specific entity with threaded replies"""
        rows = await self.db.fetch("""
            SELECT * FROM annotations 
            WHERE entity_type = $1 AND entity_id = $2
            ORDER BY created_at ASC
        """, entity_type, entity_id)
        
        # Build thread structure
        threads = {}
        for row in rows:
            if row['parent_id'] is None:
                threads[row['annotation_id']] = {'main': row, 'replies': []}
            else:
                threads[row['parent_id']]['replies'].append(row)
        
        return threads
```

## Notification System

```python
class NotificationEngine:
    """
    Notify users of relevant events
    """
    
    async def notify(self, event_type: str, payload: dict, recipients: list):
        """
        Send notifications via user's preferred channel
        """
        for user_id in recipients:
            user_prefs = await self.get_user_preferences(user_id)
            
            channels = []
            if user_prefs['email_notifications']:
                channels.append(self.send_email)
            if user_prefs['telegram_notifications']:
                channels.append(self.send_telegram)
            if user_prefs['in_app_notifications']:
                channels.append(self.send_in_app)
            
            for channel in channels:
                await channel(user_id, event_type, payload)
    
    async def send_telegram(self, user_id, event_type, payload):
        # Integration with agent-job-dm skill
        message = self.format_telegram_message(event_type, payload)
        await telegram_send(user_id, message)
    
    EVENT_TEMPLATES = {
        'target_state_change': "🎯 Target {target_id} moved to {new_status} by {user_name}",
        'qc_fail': "⚠️ QC FAILED for survey {survey_id}. {n_failed} samples flagged.",
        'anomaly_detected': "🔍 New anomaly cluster found: {cluster_id} ({n_samples} samples, max TREO {max_treo}%)",
        'drill_complete': "🪨 Drill hole {hole_id} completed: {total_depth}m",
        'report_ready': "📄 Report {report_name} is ready for review"
    }
```

## Best Practices

1. **Immutable audit trail:** Never delete or modify audit logs. Append-only.
2. **Principle of least privilege:** Users get minimum access needed for their role.
3. **Separation of duties:** CP cannot also be the one who collected the data.
4. **Approval workflows:** State transitions that affect project decisions require approval.
5. **Offline capability:** Field geologists need to sync when back in coverage.
6. **Conflict resolution:** Last-write-wins with conflict markers for manual merge.
