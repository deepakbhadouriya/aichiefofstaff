from fastapi import APIRouter, Depends, Header
from typing import Optional

from libs.schemas.onboarding import OnboardingStartRequest, OnboardingStatus
from services.onboarding.service import start_onboarding, get_onboarding_status, complete_onboarding

router = APIRouter(tags=["onboarding"])

@router.post("/onboarding/start", response_model=OnboardingStatus)
def post_onboarding_start(request: OnboardingStartRequest) -> OnboardingStatus:
    return start_onboarding(request)

@router.get("/onboarding/status", response_model=OnboardingStatus)
def get_status(x_profile_id: Optional[str] = Header(None)) -> OnboardingStatus:
    return get_onboarding_status(x_profile_id or "unknown")

@router.post("/onboarding/complete", response_model=OnboardingStatus)
def post_onboarding_complete(x_profile_id: Optional[str] = Header(None)) -> OnboardingStatus:
    return complete_onboarding(x_profile_id or "unknown")

@router.post("/onboarding/link-integration")
def post_link_integration(
    request: OnboardingIntegrationRequest,
    x_profile_id: Optional[str] = Header(None)
):
    success = link_integration(x_profile_id or "unknown", request.integration_id, request.config)
    return {"success": success}
