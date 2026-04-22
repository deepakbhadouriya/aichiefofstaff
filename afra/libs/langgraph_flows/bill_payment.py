from dataclasses import dataclass, field

from libs.schemas.runtime import WorkflowRunRecord
from libs.schemas.workflow import WorkflowEvidence, WorkflowRunRequest, WorkflowRunView
from libs.time import utc_now
from services.audit.service import append_audit_event, save_workflow_record
from services.ledger_sync.service import sync_payment_outcome
from services.payments.service import execute_payment, fetch_live_bill, get_or_create_payment_intent
from services.policy.service import choose_policy_for_vendor
from services.retrieval.service import retrieve_evidence


@dataclass
class BillPaymentState:
    tenant_id: str
    profile_id: str
    x_request_id: str
    request: WorkflowRunRequest
    current_state: str = "created"
    decision: str = "pending"
    amount_minor: int = 0
    currency: str = "INR"
    integration_mode: str = "demo_seeded"
    requires_human_review: bool = False
    evidence: list[WorkflowEvidence] = field(default_factory=list)
    payment_intent_id: str | None = None
    payment_id: str | None = None
    ledger_sync_id: str | None = None
    created_at: object | None = None


class BillPaymentFlow:
    """A deterministic scaffold mirroring the LangGraph nodes from the blueprint."""

    def run(
        self,
        tenant_id: str,
        profile_id: str,
        x_request_id: str,
        request: WorkflowRunRequest,
    ) -> WorkflowRunView:
        state = BillPaymentState(
            tenant_id=tenant_id,
            profile_id=profile_id,
            x_request_id=x_request_id,
            request=request,
            created_at=utc_now(),
        )
        workflow_id = f"wf-{profile_id}-{request.biller_reference.lower()}"
        self.context_definition(workflow_id, state)
        self.retrieve_context(workflow_id, state)
        self.fetch_bill(workflow_id, state)
        self.validate_bill(workflow_id, state)
        self.decision_gate(workflow_id, state)
        if state.decision == "approved_for_autopay":
            self.reserve_funds(workflow_id, state)
            self.execute_payment(workflow_id, state)
            self.update_ledger(workflow_id, state)
        self.write_audit(workflow_id, state)
        return self._to_view(workflow_id, state)

    def context_definition(self, workflow_id: str, state: BillPaymentState) -> None:
        choose_policy_for_vendor(state.tenant_id, state.request.vendor_name)
        state.current_state = "policy_loaded"
        self._checkpoint(workflow_id, state)

    def retrieve_context(self, workflow_id: str, state: BillPaymentState) -> None:
        state.evidence = retrieve_evidence(
            tenant_id=state.tenant_id,
            vendor_name=state.request.vendor_name,
            category=state.request.category,
            biller_reference=state.request.biller_reference,
        )
        state.current_state = "context_retrieved"
        self._checkpoint(workflow_id, state)

    def fetch_bill(self, workflow_id: str, state: BillPaymentState) -> None:
        bill = fetch_live_bill(
            tenant_id=state.tenant_id,
            profile_id=state.profile_id,
            vendor_name=state.request.vendor_name,
            biller_reference=state.request.biller_reference,
            amount_minor_hint=state.request.amount_minor_hint,
        )
        state.amount_minor = bill["amount_minor"]
        state.currency = bill["currency"]
        state.integration_mode = str(bill["integration_mode"])
        state.current_state = "bill_fetched"
        self._checkpoint(workflow_id, state)

    def validate_bill(self, workflow_id: str, state: BillPaymentState) -> None:
        policy = choose_policy_for_vendor(state.tenant_id, state.request.vendor_name)
        exceeds_threshold = state.amount_minor > policy.requires_hitl_above_minor
        no_strong_evidence = all(item.confidence < 0.8 for item in state.evidence)
        state.requires_human_review = exceeds_threshold or no_strong_evidence
        state.current_state = "validated"
        self._checkpoint(workflow_id, state)

    def decision_gate(self, workflow_id: str, state: BillPaymentState) -> None:
        if state.requires_human_review:
            state.decision = "requires_human_review"
            state.current_state = "pending_human_review"
        else:
            state.decision = "approved_for_autopay"
            state.current_state = "approved"
        self._checkpoint(workflow_id, state)

    def reserve_funds(self, workflow_id: str, state: BillPaymentState) -> None:
        workflow = self._to_record(workflow_id, state)
        intent = get_or_create_payment_intent(workflow)
        state.payment_intent_id = intent.id
        state.current_state = "payment_reserved"
        self._checkpoint(workflow_id, state)

    def execute_payment(self, workflow_id: str, state: BillPaymentState) -> None:
        workflow = self._to_record(workflow_id, state)
        intent = get_or_create_payment_intent(workflow)
        payment = execute_payment(workflow, intent)
        state.payment_intent_id = intent.id
        state.payment_id = payment.id
        state.current_state = "payment_succeeded"
        self._checkpoint(workflow_id, state)

    def update_ledger(self, workflow_id: str, state: BillPaymentState) -> None:
        if not state.payment_id:
            return
        ledger_sync = sync_payment_outcome(
            tenant_id=state.tenant_id,
            workflow_run_id=workflow_id,
            payment_id=state.payment_id,
        )
        state.ledger_sync_id = ledger_sync.id
        state.current_state = "ledger_updated"
        self._checkpoint(workflow_id, state)

    def write_audit(self, workflow_id: str, state: BillPaymentState) -> None:
        append_audit_event(
            tenant_id=state.tenant_id,
            workflow_run_id=workflow_id,
            event_type="workflow_state_changed",
            entity_type="workflow_run",
            entity_id=workflow_id,
            payload={
                "current_state": state.current_state,
                "decision": state.decision,
                "payment_intent_id": state.payment_intent_id,
                "payment_id": state.payment_id,
                "ledger_sync_id": state.ledger_sync_id,
                "x_request_id": state.x_request_id,
            },
        )

    def _checkpoint(self, workflow_id: str, state: BillPaymentState) -> None:
        record = self._to_record(workflow_id, state)
        save_workflow_record(record)

    def _to_record(self, workflow_id: str, state: BillPaymentState) -> WorkflowRunRecord:
        created_at = state.created_at or utc_now()
        return WorkflowRunRecord(
            id=workflow_id,
            tenant_id=state.tenant_id,
            profile_id=state.profile_id,
            x_request_id=state.x_request_id,
            request=state.request,
            current_state=state.current_state,
            decision=state.decision,
            amount_minor=state.amount_minor,
            currency=state.currency,
            integration_mode=state.integration_mode,
            requires_human_review=state.requires_human_review,
            evidence=state.evidence,
            payment_intent_id=state.payment_intent_id,
            payment_id=state.payment_id,
            ledger_sync_id=state.ledger_sync_id,
            created_at=created_at,
            updated_at=utc_now(),
        )

    def _to_view(self, workflow_id: str, state: BillPaymentState) -> WorkflowRunView:
        record = self._to_record(workflow_id, state)
        return WorkflowRunView(
            id=workflow_id,
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
