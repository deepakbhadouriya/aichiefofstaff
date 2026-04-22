from datetime import datetime

from pydantic import BaseModel, Field


class WorkflowRunRequest(BaseModel):
    vendor_name: str = Field(examples=["Tata Power"])
    category: str = Field(examples=["electricity"])
    biller_reference: str = Field(examples=["CA-1023001"])
    amount_minor_hint: int | None = Field(default=None)


class WorkflowEvidence(BaseModel):
    source: str
    summary: str
    confidence: float


class WorkflowRunView(BaseModel):
    id: str
    tenant_id: str
    profile_id: str
    x_request_id: str
    current_state: str
    decision: str
    amount_minor: int
    currency: str
    integration_mode: str
    requires_human_review: bool
    evidence: list[WorkflowEvidence]
    payment_intent_id: str | None = None
    payment_id: str | None = None
    ledger_sync_id: Optional[str] = None
    reasoning: Optional[str] = None
    created_at: datetime
