from dataclasses import dataclass, field
from datetime import datetime, UTC

from libs.schemas.workflow import WorkflowEvidence, WorkflowRunRequest, WorkflowRunView
from services.policy.service import choose_policy_for_vendor
from services.retrieval.service import retrieve_evidence
from services.payments.service import fetch_live_bill


@dataclass
class BillPaymentState:
    tenant_id: str
    x_request_id: str
    request: WorkflowRunRequest
    current_state: str = "created"
    decision: str = "pending"
    amount_minor: int = 0
    currency: str = "INR"
    requires_human_review: bool = False
    evidence: list[WorkflowEvidence] = field(default_factory=list)


class BillPaymentFlow:
    """A deterministic scaffold mirroring the LangGraph nodes from the blueprint."""

    def run(self, tenant_id: str, x_request_id: str, request: WorkflowRunRequest) -> WorkflowRunView:
        state = BillPaymentState(tenant_id=tenant_id, x_request_id=x_request_id, request=request)
        self.context_definition(state)
        self.retrieve_context(state)
        self.fetch_bill(state)
        self.validate_bill(state)
        self.decision_gate(state)
        return WorkflowRunView(
            id=f"wf-{request.biller_reference.lower()}",
            tenant_id=state.tenant_id,
            x_request_id=state.x_request_id,
            current_state=state.current_state,
            decision=state.decision,
            amount_minor=state.amount_minor,
            currency=state.currency,
            requires_human_review=state.requires_human_review,
            evidence=state.evidence,
            created_at=datetime.now(UTC),
        )

    def context_definition(self, state: BillPaymentState) -> None:
        choose_policy_for_vendor(state.tenant_id, state.request.vendor_name)
        state.current_state = "policy_loaded"

    def retrieve_context(self, state: BillPaymentState) -> None:
        state.evidence = retrieve_evidence(
            tenant_id=state.tenant_id,
            vendor_name=state.request.vendor_name,
            category=state.request.category,
            biller_reference=state.request.biller_reference,
        )
        state.current_state = "context_retrieved"

    def fetch_bill(self, state: BillPaymentState) -> None:
        bill = fetch_live_bill(
            vendor_name=state.request.vendor_name,
            biller_reference=state.request.biller_reference,
            amount_minor_hint=state.request.amount_minor_hint,
        )
        state.amount_minor = bill["amount_minor"]
        state.currency = bill["currency"]
        state.current_state = "bill_fetched"

    def validate_bill(self, state: BillPaymentState) -> None:
        policy = choose_policy_for_vendor(state.tenant_id, state.request.vendor_name)
        exceeds_threshold = state.amount_minor > policy.requires_hitl_above_minor
        no_strong_evidence = all(item.confidence < 0.8 for item in state.evidence)
        state.requires_human_review = exceeds_threshold or no_strong_evidence
        state.current_state = "validated"

    def decision_gate(self, state: BillPaymentState) -> None:
        if state.requires_human_review:
            state.decision = "requires_human_review"
            state.current_state = "pending_human_review"
        else:
            state.decision = "approved_for_autopay"
            state.current_state = "approved"

