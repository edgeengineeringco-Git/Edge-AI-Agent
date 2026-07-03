---
name: collaboration-workflow
description: Multi-user collaboration, role-based access control, audit logging, and workflow orchestration for REE exploration teams.
---

# Collaboration and Workflow Management

## When to use

- Multiple geologists need to work on the same project simultaneously.
- You need role-based access (junior geo vs. CP vs. manager vs. investor).
- You want audit trails for all data changes.
- You need approval workflows before data is promoted to "official" status.

## Role Definitions

| Role | Permissions | Typical User |
|---|---|---|
| **Admin** | Full access, user management, system config | IT / Project manager |
| **Competent Person** | Approve resource estimates, sign off reports | Senior geologist |
| **Senior Geologist** | Upload/edit all data, run models, create targets | Team lead |
| **Geologist** | Upload field data, edit own data, view all | Field geo |
| **Technician** | Upload lab data, QC checks, no interpretation | Lab tech |
| **Viewer** | Read-only access to maps and reports | Investor, regulator |

## Workflow States

```
DRAFT → UNDER_REVIEW → APPROVED → OFFICIAL → ARCHIVED
   ↑         ↓
REJECTED → REVISION_REQUIRED
```

| State | Meaning | Who Can Promote |
|---|---|---|
| **DRAFT** | Work in progress, editable by owner | Owner → UNDER_REVIEW |
| **UNDER_REVIEW** | Locked for editing, under CP review | CP → APPROVED or REJECTED |
| **APPROVED** | CP has reviewed and approved | Auto → OFFICIAL after 24h |
| **OFFICIAL** | Locked permanently, versioned, auditable | No one (immutable) |
| **ARCHIVED** | Superseded by newer version | Admin only |

## Python Implementation

```python
from enum import Enum
from datetime import datetime
import hashlib
import json

class WorkflowState(Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    OFFICIAL = "official"
    ARCHIVED = "archived"
    REJECTED = "rejected"
    REVISION_REQUIRED = "revision_required"

class DataObject:
    def __init__(self, obj_id, obj_type, owner_id, data):
        self.obj_id = obj_id
        self.obj_type = obj_type  # 'survey', 'assay', 'target', 'report'
        self.owner_id = owner_id
        self.state = WorkflowState.DRAFT
        self.data = data
        self.versions = []
        self.audit_log = []
        self.approved_by = None
        self.approved_at = None
        
    def transition(self, new_state, user_id, comment=""):
        """
        State transition with validation
        """
        valid_transitions = {
            WorkflowState.DRAFT: [WorkflowState.UNDER_REVIEW],
            WorkflowState.UNDER_REVIEW: [WorkflowState.APPROVED, WorkflowState.REJECTED, WorkflowState.REVISION_REQUIRED],
            WorkflowState.APPROVED: [WorkflowState.OFFICIAL],
            WorkflowState.REJECTED: [WorkflowState.DRAFT],
            WorkflowState.REVISION_REQUIRED: [WorkflowState.DRAFT],
            WorkflowState.OFFICIAL: [WorkflowState.ARCHIVED]
        }
        
        if new_state not in valid_transitions.get(self.state, []):
            raise ValueError(f"Invalid transition: {self.state.value} → {new_state.value}")
        
        # Record previous version
        self.versions.append({
            'state': self.state.value,
            'data_hash': self._hash_data(),
            'timestamp': datetime.now().isoformat()
        })
        
        # Log transition
        self.audit_log.append({
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'action': 'state_transition',
            'from_state': self.state.value,
            'to_state': new_state.value,
            'comment': comment,
            'data_hash': self._hash_data()
        })
        
        self.state = new_state
        
        if new_state == WorkflowState.APPROVED:
            self.approved_by = user_id
            self.approved_at = datetime.now().isoformat()
        
        if new_state == WorkflowState.OFFICIAL:
            self.data = self._freeze_data()
    
    def _hash_data(self):
        return hashlib.sha256(json.dumps(self.data, sort_keys=True).encode()).hexdigest()[:16]
    
    def _freeze_data(self):
        """Make data immutable by converting to tuple/frozen structures"""
        return json.loads(json.dumps(self.data))  # Deep copy
    
    def edit(self, user_id, new_data):
        """
        Edit data with permission check
        """
        if self.state in [WorkflowState.OFFICIAL, WorkflowState.ARCHIVED]:
            raise PermissionError("Cannot edit OFFICIAL or ARCHIVED data")
        
        if self.state == WorkflowState.UNDER_REVIEW and user_id != self.approved_by:
            raise PermissionError("Only approver can edit during review")
        
        # Log edit
        self.audit_log.append({
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'action': 'edit',
            'old_hash': self._hash_data(),
            'new_hash': hashlib.sha256(json.dumps(new_data, sort_keys=True).encode()).hexdigest()[:16]
        })
        
        self.data = new_data

class ProjectACL:
    def __init__(self):
        self.permissions = {
            'admin': ['*'],
            'cp': ['read:*', 'write:official', 'approve:*', 'sign:report'],
            'senior_geo': ['read:*', 'write:survey', 'write:assay', 'write:target', 'run:model'],
            'geologist': ['read:*', 'write:own', 'upload:field'],
            'technician': ['read:assay', 'write:lab_data', 'run:qc'],
            'viewer': ['read:official', 'read:report']
        }
    
    def can(self, user_role, action, resource_owner=None, current_user=None):
        perms = self.permissions.get(user_role, [])
        
        if '*' in perms:
            return True
        if action in perms:
            return True
        if f"{action.split(':')[0]}:*" in perms:
            return True
        
        # Ownership check
        if 'write:own' in perms and resource_owner == current_user:
            return True
        
        return False
```

## Audit Trail Requirements

Every action must log:
- Timestamp (UTC)
- User ID
- Action type (create, read, update, delete, transition, export)
- Object ID and type
- Before/after hash (for data changes)
- IP address
- Client application

## Notifications

```python
async def notify_on_transition(obj, old_state, new_state):
    """
    Send notifications on important transitions
    """
    if new_state == WorkflowState.UNDER_REVIEW:
        await notify_role('cp', f"{obj.obj_type} {obj.obj_id} ready for review")
    
    elif new_state == WorkflowState.APPROVED:
        await notify_user(obj.owner_id, f"Your {obj.obj_type} has been approved")
    
    elif new_state == WorkflowState.REJECTED:
        await notify_user(obj.owner_id, f"Your {obj.obj_type} was rejected. See comments.")
    
    elif new_state == WorkflowState.OFFICIAL:
        await notify_all(f"New official {obj.obj_type} available: {obj.obj_id}")
```

## Best Practices

1. **Immutable official data:** Once OFFICIAL, never edit. Create new version instead.
2. **Digital signatures:** CP approval should use cryptographic signing.
3. **Time-locked transitions:** APPROVED → OFFICIAL after 24h cooling-off period.
4. **Export watermarks:** All exports include user ID, timestamp, and "UNOFFICIAL" if not official.
5. **Conflict detection:** Warn if two users edit same object simultaneously.
