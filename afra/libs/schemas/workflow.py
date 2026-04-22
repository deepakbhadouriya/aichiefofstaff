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
    x_request_id: str
    current_state: str
    decision: str
    amount_minor: int
    currency: str
    requires_human_review: bool
    evidence: list[WorkflowEvidence]
    created_at: datetime

