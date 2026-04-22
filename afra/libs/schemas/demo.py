from pydantic import BaseModel


class DemoScenario(BaseModel):
    id: str
    persona: str
    title: str
    vendor_name: str
    category: str
    biller_reference: str
    amount_minor_hint: int
    expected_outcome: str
    walkthrough_hint: str


class DemoSeedResult(BaseModel):
    tenant_id: str
    seeded_for_profile: str
    scenario_count: int
    workflow_ids: list[str]
    review_queue_count: int
    payment_count: int

