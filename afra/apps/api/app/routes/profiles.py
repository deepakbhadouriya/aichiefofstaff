from fastapi import APIRouter, Depends

from apps.api.app.dependencies import get_request_context
from libs.schemas.profile import UserProfileView
from services.personas.service import get_profile, list_profiles

router = APIRouter(tags=["profiles"])


@router.get("/profiles", response_model=list[UserProfileView])
def get_profiles(context: dict[str, str] = Depends(get_request_context)) -> list[UserProfileView]:
    return list_profiles(context["tenant_id"])


@router.get("/profiles/me", response_model=UserProfileView)
def get_my_profile(context: dict[str, str] = Depends(get_request_context)) -> UserProfileView:
    return get_profile(context["tenant_id"], context["profile_id"])

