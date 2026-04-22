from fastapi import APIRouter, Depends

from apps.api.app.dependencies import get_request_context
from libs.schemas.policy import PaymentPolicyCreate, PaymentPolicyView
from services.policy.service import list_policies, upsert_policy

router = APIRouter(tags=["policies"])


@router.get("/policies", response_model=list[PaymentPolicyView])
def get_policies(context: dict[str, str] = Depends(get_request_context)) -> list[PaymentPolicyView]:
    return list_policies(context["tenant_id"])


@router.post("/policies", response_model=PaymentPolicyView)
def create_policy(
    payload: PaymentPolicyCreate,
    context: dict[str, str] = Depends(get_request_context),
) -> PaymentPolicyView:
    return upsert_policy(context["tenant_id"], payload)

