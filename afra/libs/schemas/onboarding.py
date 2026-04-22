from pydantic import BaseModel, EmailStr
from typing import Optional

class OnboardingStartRequest(BaseModel):
    name: str
    email: EmailStr
    company_name: str

class OnboardingStatus(BaseModel):
    step: str
    is_complete: bool
    tenant_id: Optional[str] = None
    profile_id: Optional[str] = None

class OnboardingIntegrationRequest(BaseModel):
    integration_id: str
    config: dict
