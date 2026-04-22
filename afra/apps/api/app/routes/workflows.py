from fastapi import APIRouter, Depends

from apps.api.app.dependencies import get_request_context
from libs.schemas.audit import AuditEvent
from libs.schemas.workflow import WorkflowRunRequest, WorkflowRunView
from services.audit.service import get_workflow_run, list_audit_events
from services.payments.orchestration import run_bill_payment_flow

router = APIRouter(tags=["workflows"])


@router.get("/workflows/{workflow_run_id}", response_model=WorkflowRunView)
def get_workflow(
    workflow_run_id: str,
    context: dict[str, str] = Depends(get_request_context),
) -> WorkflowRunView:
    return get_workflow_run(context["tenant_id"], context["profile_id"], workflow_run_id)


@router.get("/workflows/{workflow_run_id}/audit-events", response_model=list[AuditEvent])
def get_workflow_audit_events(
    workflow_run_id: str,
) -> list[AuditEvent]:
    return list_audit_events(workflow_run_id)


@router.post("/workflows/run", response_model=WorkflowRunView)
def run_workflow(
    payload: WorkflowRunRequest,
    context: dict[str, str] = Depends(get_request_context),
) -> WorkflowRunView:
    return run_bill_payment_flow(
        tenant_id=context["tenant_id"],
        profile_id=context["profile_id"],
        request_id=context["x_request_id"],
        request=payload,
    )
