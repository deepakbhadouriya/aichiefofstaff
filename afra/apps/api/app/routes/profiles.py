from fastapi import APIRouter, Depends
from pydantic import BaseModel

from apps.api.app.dependencies import get_request_context
from libs.schemas.profile import UserProfileView
from services.personas.service import get_profile, list_profiles, update_persona_context

router = APIRouter(tags=["profiles"])

class ContextUpdateRequest(BaseModel):
    communication_style: str
    decision_preferences: str

@router.get("/profiles", response_model=list[UserProfileView])
def get_profiles(context: dict[str, str] = Depends(get_request_context)) -> list[UserProfileView]:
    return list_profiles(context["tenant_id"])


@router.get("/profiles/me", response_model=UserProfileView)
def get_my_profile(context: dict[str, str] = Depends(get_request_context)) -> UserProfileView:
    return get_profile(context["tenant_id"], context["profile_id"])

@router.post("/profiles/me/context", response_model=UserProfileView)
def post_context_update(
    request: ContextUpdateRequest,
    context: dict[str, str] = Depends(get_request_context)
) -> UserProfileView:
    return update_persona_context(
        context["tenant_id"], 
        context["profile_id"], 
        request.communication_style, 
        request.decision_preferences
    )
