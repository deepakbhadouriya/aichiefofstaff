from datetime import datetime

from pydantic import BaseModel


class AuditEvent(BaseModel):
    id: str
    tenant_id: str
    workflow_run_id: str
    event_type: str
    entity_type: str
    entity_id: str
    payload: dict
    created_at: datetime

