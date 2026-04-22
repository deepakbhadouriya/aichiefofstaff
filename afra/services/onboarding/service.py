from typing import Dict
from libs.schemas.onboarding import OnboardingStartRequest, OnboardingStatus
from services.personas.service import create_dynamic_profile

# In-memory store for onboarding progress
_ONBOARDING_STATE: Dict[str, OnboardingStatus] = {}

def start_onboarding(request: OnboardingStartRequest) -> OnboardingStatus:
    # Logic to create a tenant and a profile
    tenant_id = f"tenant-{request.company_name.lower().replace(' ', '-')}"
    profile_id = f"user-{request.name.lower().replace(' ', '-')}"
    
    # Create the profile in the personas service
    create_dynamic_profile(
        tenant_id=tenant_id,
        profile_id=profile_id,
        display_name=request.name,
        email=str(request.email),
        description=f"Founder profile for {request.company_name}"
    )
    
    status = OnboardingStatus(
        step="integrations",
        is_complete=False,
        tenant_id=tenant_id,
        profile_id=profile_id
    )
    _ONBOARDING_STATE[profile_id] = status
    return status

def get_onboarding_status(profile_id: str) -> OnboardingStatus:
    return _ONBOARDING_STATE.get(profile_id, OnboardingStatus(step="start", is_complete=False))

def complete_onboarding(profile_id: str) -> OnboardingStatus:
    if profile_id in _ONBOARDING_STATE:
        _ONBOARDING_STATE[profile_id].is_complete = True
        _ONBOARDING_STATE[profile_id].step = "complete"
    return _ONBOARDING_STATE.get(profile_id, OnboardingStatus(step="complete", is_complete=True))

def link_integration(profile_id: str, integration_id: str, config: dict) -> bool:
    # Logic to record that an integration was linked during onboarding
    # For now, we'll just log it to the console or update the status summary
    if profile_id in _ONBOARDING_STATE:
        # We could update the profile's integration_status_summary here
        return True
    return False
