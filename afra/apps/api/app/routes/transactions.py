from fastapi import APIRouter, Depends

from apps.api.app.dependencies import get_request_context
from libs.schemas.payment import PaymentRecord
from services.payments.service import list_payments

router = APIRouter(tags=["transactions"])


@router.get("/payments", response_model=list[PaymentRecord])
def get_payments(context: dict[str, str] = Depends(get_request_context)) -> list[PaymentRecord]:
    return list_payments(context["tenant_id"], context["profile_id"])
