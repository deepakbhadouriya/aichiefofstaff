from datetime import UTC, datetime

from libs.schemas.review import ReviewItem
from libs.schemas.workflow import WorkflowEvidence, WorkflowRunView


def list_reviews(tenant_id: str) -> list[ReviewItem]:
    return [
        ReviewItem(
            workflow_run_id="wf-ca-1023001",
            tenant_id=tenant_id,
            vendor_name="Tata Power",
            amount_minor=640000,
            reason="Amount exceeds auto-pay threshold and requires human approval.",
            status="pending",
        )
    ]


def get_workflow_run(tenant_id: str, workflow_run_id: str) -> WorkflowRunView:
    return WorkflowRunView(
        id=workflow_run_id,
        tenant_id=tenant_id,
        x_request_id="req-local-dev",
        current_state="pending_human_review",
        decision="requires_human_review",
        amount_minor=640000,
        currency="INR",
        requires_human_review=True,
        evidence=[
            WorkflowEvidence(
                source="historical_payment_log",
                summary="Historical range is below the current outstanding amount.",
                confidence=0.84,
            )
        ],
        created_at=datetime.now(UTC),
    )

