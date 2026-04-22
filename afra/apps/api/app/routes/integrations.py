from fastapi import APIRouter, Depends

from apps.api.app.dependencies import get_request_context
from libs.schemas.integration import IntegrationRealtimeSnapshot, IntegrationView
from services.integrations.service import get_realtime_snapshot, list_integrations

router = APIRouter(tags=["integrations"])


@router.get("/integrations", response_model=list[IntegrationView])
def get_integrations(
    context: dict[str, str] = Depends(get_request_context),
) -> list[IntegrationView]:
    return list_integrations(context["tenant_id"], context["profile_id"])


@router.get("/integrations/realtime", response_model=IntegrationRealtimeSnapshot)
def get_integrations_realtime(
    context: dict[str, str] = Depends(get_request_context),
) -> IntegrationRealtimeSnapshot:
    return get_realtime_snapshot(context["tenant_id"], context["profile_id"])

