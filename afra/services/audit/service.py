from libs.schemas.audit import AuditEvent
from libs.schemas.review import ReviewItem
from libs.schemas.runtime import WorkflowRunRecord
from libs.schemas.workflow import WorkflowEvidence, WorkflowRunView
from libs.time import utc_now
from services.runtime.store import load_state, save_state


def list_reviews(tenant_id: str) -> list[ReviewItem]:
    state = load_state()
    reviews: list[ReviewItem] = []
    for workflow in state["workflows"].values():
        if workflow["tenant_id"] != tenant_id or workflow["current_state"] != "pending_human_review":
            continue
        reviews.append(
            ReviewItem(
                workflow_run_id=workflow["id"],
                tenant_id=workflow["tenant_id"],
                profile_id=workflow["profile_id"],
                vendor_name=workflow["request"]["vendor_name"],
                amount_minor=workflow["amount_minor"],
                reason="Amount exceeds auto-pay threshold or evidence confidence is below threshold.",
                status="pending",
            )
        )
    return reviews


def get_workflow_run(tenant_id: str, profile_id: str, workflow_run_id: str) -> WorkflowRunView:
    state = load_state()
    item = state["workflows"].get(workflow_run_id)
    if not item:
        return WorkflowRunView(
            id=workflow_run_id,
            tenant_id=tenant_id,
            profile_id=profile_id,
            x_request_id="req-missing",
            current_state="missing",
            decision="missing",
            amount_minor=0,
            currency="INR",
            integration_mode="unknown",
            requires_human_review=False,
            evidence=[],
            created_at=utc_now(),
        )
    return _to_workflow_view(WorkflowRunRecord.model_validate(item))


def save_workflow_record(record: WorkflowRunRecord) -> WorkflowRunRecord:
    state = load_state()
    state["workflows"][record.id] = record.model_dump(mode="json")
    save_state(state)
    return record


def append_audit_event(
    tenant_id: str,
    workflow_run_id: str,
    event_type: str,
    entity_type: str,
    entity_id: str,
    payload: dict,
) -> AuditEvent:
    state = load_state()
    event = AuditEvent(
        id=f"audit-{workflow_run_id}-{len(state['audit_events']) + 1}",
        tenant_id=tenant_id,
        workflow_run_id=workflow_run_id,
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        payload=payload,
        created_at=utc_now(),
    )
    state["audit_events"][event.id] = event.model_dump(mode="json")
    save_state(state)
    return event


def list_audit_events(workflow_run_id: str) -> list[AuditEvent]:
    state = load_state()
    events = [
        AuditEvent.model_validate(item)
        for item in state["audit_events"].values()
        if item["workflow_run_id"] == workflow_run_id
    ]
    return sorted(events, key=lambda item: item.created_at)


def _to_workflow_view(record: WorkflowRunRecord) -> WorkflowRunView:
    return WorkflowRunView(
        id=record.id,
        tenant_id=record.tenant_id,
        profile_id=record.profile_id,
        x_request_id=record.x_request_id,
        current_state=record.current_state,
        decision=record.decision,
        amount_minor=record.amount_minor,
        currency=record.currency,
        integration_mode=record.integration_mode,
        requires_human_review=record.requires_human_review,
        evidence=record.evidence,
        payment_intent_id=record.payment_intent_id,
        payment_id=record.payment_id,
        ledger_sync_id=record.ledger_sync_id,
        created_at=record.created_at,
    )
