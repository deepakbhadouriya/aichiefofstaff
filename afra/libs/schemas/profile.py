from pydantic import BaseModel


class PersonaSummary(BaseModel):
    profile_id: str
    label: str
    description: str
    operating_mode: str


class UserProfileView(BaseModel):
    id: str
    tenant_id: str
    display_name: str
    email: str
    persona_label: str
    description: str
    operating_mode: str
    seeded_data_enabled: bool
    capabilities: list[str]
    default_vendor_count: int
    integration_status_summary: str
    # New Context Instructions (LifeOS inspiration)
    communication_style: str = "Concise, professional, and firm."
    decision_preferences: str = "Prioritize cash flow and long-term vendor relationships."

