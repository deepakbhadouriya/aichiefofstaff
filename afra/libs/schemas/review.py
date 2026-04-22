from pydantic import BaseModel


class ReviewItem(BaseModel):
    workflow_run_id: str
    tenant_id: str
    vendor_name: str
    amount_minor: int
    reason: str
    status: str


class ReviewDecision(BaseModel):
    workflow_run_id: str
    tenant_id: str
    decision: str
    actor: str

