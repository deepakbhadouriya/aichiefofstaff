from libs.langgraph_flows.bill_payment import BillPaymentFlow
from libs.schemas.review import ReviewDecision
from libs.schemas.runtime import WorkflowRunRecord
from libs.schemas.workflow import WorkflowRunRequest, WorkflowRunView
from services.audit.service import append_audit_event, get_workflow_run, save_workflow_record
from services.ledger_sync.service import sync_payment_outcome
from services.payments.service import execute_payment, get_or_create_payment_intent
from services.runtime.store import load_state

_FLOW = BillPaymentFlow()


def run_bill_payment_flow(
    tenant_id: str,
    profile_id: str,
    request_id: str,
    request: WorkflowRunRequest,
) -> WorkflowRunView:
    return _FLOW.run(
        tenant_id=tenant_id,
        profile_id=profile_id,
        x_request_id=request_id,
        request=request,
    )


def resume_review_workflow(
    tenant_id: str,
    profile_id: str,
    workflow_run_id: str,
    actor: str,
) -> ReviewDecision:
    state = load_state()
    item = state["workflows"].get(workflow_run_id)
    if not item:
        return ReviewDecision(
            workflow_run_id=workflow_run_id,
            tenant_id=tenant_id,
            profile_id=profile_id,
            decision="missing",
            actor=actor,
        )

    workflow = WorkflowRunRecord.model_validate(item)
    workflow.decision = "approved_for_autopay"
    workflow.requires_human_review = False
    workflow.current_state = "approved"
    save_workflow_record(workflow)

    intent = get_or_create_payment_intent(workflow)
    workflow.payment_intent_id = intent.id
    workflow.current_state = "payment_reserved"
    save_workflow_record(workflow)

    payment = execute_payment(workflow, intent)
    workflow.payment_id = payment.id
    workflow.current_state = "payment_succeeded"
    save_workflow_record(workflow)

    ledger_sync = sync_payment_outcome(
        tenant_id=workflow.tenant_id,
        workflow_run_id=workflow.id,
        payment_id=payment.id,
    )
    workflow.ledger_sync_id = ledger_sync.id
    workflow.current_state = "ledger_updated"
    save_workflow_record(workflow)

    append_audit_event(
        tenant_id=workflow.tenant_id,
        workflow_run_id=workflow.id,
        event_type="human_review_approved",
        entity_type="workflow_run",
        entity_id=workflow.id,
        payload={"actor": actor, "x_request_id": workflow.x_request_id},
    )
    return ReviewDecision(
        workflow_run_id=workflow_run_id,
        tenant_id=tenant_id,
        profile_id=profile_id,
        decision="approved",
        actor=actor,
    )


def reject_review_workflow(
    tenant_id: str,
    profile_id: str,
    workflow_run_id: str,
    actor: str,
) -> ReviewDecision:
    state = load_state()
    item = state["workflows"].get(workflow_run_id)
    if item:
        workflow = WorkflowRunRecord.model_validate(item)
        workflow.decision = "rejected"
        workflow.current_state = "closed"
        save_workflow_record(workflow)
        append_audit_event(
            tenant_id=workflow.tenant_id,
            workflow_run_id=workflow.id,
            event_type="human_review_rejected",
            entity_type="workflow_run",
            entity_id=workflow.id,
            payload={"actor": actor, "x_request_id": workflow.x_request_id},
        )
    return ReviewDecision(
        workflow_run_id=workflow_run_id,
        tenant_id=tenant_id,
        profile_id=profile_id,
        decision="rejected",
        actor=actor,
    )


def resume_incomplete_workflows() -> list[WorkflowRunView]:
    state = load_state()
    resumed: list[WorkflowRunView] = []
    for item in state["workflows"].values():
        workflow = WorkflowRunRecord.model_validate(item)
        if workflow.current_state not in {"approved", "payment_reserved", "payment_succeeded"}:
            continue

        if workflow.current_state == "approved":
            intent = get_or_create_payment_intent(workflow)
            workflow.payment_intent_id = intent.id
            workflow.current_state = "payment_reserved"
            save_workflow_record(workflow)

        if workflow.current_state == "payment_reserved":
            intent = get_or_create_payment_intent(workflow)
            payment = execute_payment(workflow, intent)
            workflow.payment_intent_id = intent.id
            workflow.payment_id = payment.id
            workflow.current_state = "payment_succeeded"
            save_workflow_record(workflow)

        if workflow.current_state == "payment_succeeded" and workflow.payment_id:
            ledger_sync = sync_payment_outcome(
                tenant_id=workflow.tenant_id,
                workflow_run_id=workflow.id,
                payment_id=workflow.payment_id,
            )
            workflow.ledger_sync_id = ledger_sync.id
            workflow.current_state = "ledger_updated"
            save_workflow_record(workflow)
            append_audit_event(
                tenant_id=workflow.tenant_id,
                workflow_run_id=workflow.id,
                event_type="worker_resumed_workflow",
                entity_type="workflow_run",
                entity_id=workflow.id,
                payload={"current_state": workflow.current_state, "x_request_id": workflow.x_request_id},
            )

        resumed.append(get_workflow_run(workflow.tenant_id, workflow.profile_id, workflow.id))
    return resumed
