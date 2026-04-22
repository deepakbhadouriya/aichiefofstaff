from fastapi import APIRouter, Depends, HTTPException

from apps.api.app.dependencies import get_request_context
from libs.schemas.review import ReviewDecision, ReviewItem
from services.audit.service import list_reviews

router = APIRouter(tags=["reviews"])


@router.get("/reviews", response_model=list[ReviewItem])
def get_reviews(context: dict[str, str] = Depends(get_request_context)) -> list[ReviewItem]:
    return list_reviews(context["tenant_id"])


@router.post("/reviews/{workflow_run_id}/approve", response_model=ReviewDecision)
def approve_review(
    workflow_run_id: str,
    context: dict[str, str] = Depends(get_request_context),
) -> ReviewDecision:
    if not workflow_run_id:
        raise HTTPException(status_code=400, detail="workflow_run_id is required")
    return ReviewDecision(
        workflow_run_id=workflow_run_id,
        decision="approved",
        actor="human-reviewer",
        tenant_id=context["tenant_id"],
    )


@router.post("/reviews/{workflow_run_id}/reject", response_model=ReviewDecision)
def reject_review(
    workflow_run_id: str,
    context: dict[str, str] = Depends(get_request_context),
) -> ReviewDecision:
    if not workflow_run_id:
        raise HTTPException(status_code=400, detail="workflow_run_id is required")
    return ReviewDecision(
        workflow_run_id=workflow_run_id,
        decision="rejected",
        actor="human-reviewer",
        tenant_id=context["tenant_id"],
    )

