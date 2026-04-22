from datetime import datetime

from pydantic import BaseModel


class LedgerSyncRecord(BaseModel):
    id: str
    tenant_id: str
    workflow_run_id: str
    payment_id: str
    adapter_name: str
    status: str
    synced_at: datetime

