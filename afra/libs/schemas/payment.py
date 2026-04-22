from datetime import datetime

from pydantic import BaseModel


class PaymentRecord(BaseModel):
    id: str
    workflow_run_id: str
    payment_intent_id: str
    tenant_id: str
    profile_id: str
    vendor_name: str
    amount_minor: int
    currency: str
    status: str
    provider: str
    integration_mode: str
    source_type: str
    idempotency_key: str
    created_at: datetime
