from datetime import datetime

from pydantic import BaseModel, Field

from libs.schemas.workflow import WorkflowEvidence, WorkflowRunRequest


class PaymentIntentRecord(BaseModel):
    id: str
    workflow_run_id: str
    tenant_id: str
    profile_id: str
    idempotency_key: str
    amount_minor: int
    currency: str
    provider: str
    status: str
    created_at: datetime


class WorkflowRunRecord(BaseModel):
    id: str
    tenant_id: str
    profile_id: str
    x_request_id: str
    request: WorkflowRunRequest
    current_state: str
    decision: str
    amount_minor: int
    currency: str
    integration_mode: str
    requires_human_review: bool
    evidence: list[WorkflowEvidence] = Field(default_factory=list)
    payment_intent_id: str | None = None
    payment_id: str | None = None
    ledger_sync_id: str | None = None
    created_at: datetime
    updated_at: datetime

