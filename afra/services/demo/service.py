from libs.schemas.demo import DemoScenario, DemoSeedResult
from libs.schemas.policy import PaymentPolicyCreate
from libs.schemas.workflow import WorkflowRunRequest
from services.audit.service import list_reviews
from services.payments.orchestration import reject_review_workflow, run_bill_payment_flow
from services.payments.service import list_payments
from services.policy.service import upsert_policy


def demo_scenarios() -> list[DemoScenario]:
    return [
        DemoScenario(
            id="happy-electricity-autopay",
            persona="demo_user",
            title="Happy path utility autopay",
            vendor_name="Tata Power",
            category="electricity",
            biller_reference="TP-DEMO-1001",
            amount_minor_hint=420000,
            expected_outcome="Auto-approved, paid, ledger synced",
            walkthrough_hint="Use this first to show the full green path from rule to payment to ledger update.",
        ),
        DemoScenario(
            id="happy-broadband-autopay",
            persona="demo_user",
            title="Happy path broadband renewal",
            vendor_name="Airtel Business",
            category="internet",
            biller_reference="AB-DEMO-2001",
            amount_minor_hint=185000,
            expected_outcome="Auto-approved under the broadband threshold",
            walkthrough_hint="Use this to show that SMEs can automate recurring connectivity bills, not just utilities.",
        ),
        DemoScenario(
            id="negative-threshold-review",
            persona="demo_user",
            title="High amount routed to review",
            vendor_name="Tata Power",
            category="electricity",
            biller_reference="TP-REVIEW-3001",
            amount_minor_hint=640000,
            expected_outcome="Pending human review because the amount crosses policy threshold",
            walkthrough_hint="Open the review queue and approve this to demonstrate controlled human escalation.",
        ),
        DemoScenario(
            id="negative-new-vendor-reject",
            persona="demo_user",
            title="Unknown vendor rejected",
            vendor_name="Fresh Pest Control Services",
            category="vendor_services",
            biller_reference="NEW-VENDOR-4001",
            amount_minor_hint=88000,
            expected_outcome="Pending review due to low evidence and typically rejected in demo",
            walkthrough_hint="Use this to show anomaly handling for new or weakly matched vendors.",
        ),
        DemoScenario(
            id="actual-live-ready-flow",
            persona="actual_user",
            title="Actual user live-ready execution",
            vendor_name="Tata Power",
            category="electricity",
            biller_reference="TP-LIVE-5001",
            amount_minor_hint=415000,
            expected_outcome="Runs on the live-connectors profile while keeping real connector switch-over ready",
            walkthrough_hint="Use this to explain how the same flow will switch from seeded mode to live credentials later.",
        ),
    ]


def seed_demo_data(tenant_id: str, profile_id: str) -> DemoSeedResult:
    _seed_demo_policies(tenant_id)
    workflow_ids: list[str] = []

    for scenario in demo_scenarios():
        if scenario.persona != profile_id:
            continue
        result = run_bill_payment_flow(
            tenant_id=tenant_id,
            profile_id=profile_id,
            request_id=f"seed-{scenario.id}",
            request=WorkflowRunRequest(
                vendor_name=scenario.vendor_name,
                category=scenario.category,
                biller_reference=scenario.biller_reference,
                amount_minor_hint=scenario.amount_minor_hint,
            ),
        )
        workflow_ids.append(result.id)
        if scenario.id == "negative-new-vendor-reject":
            reject_review_workflow(tenant_id, profile_id, result.id, "demo-seeder")

    reviews = list_reviews(tenant_id)
    payments = list_payments(tenant_id, profile_id)
    return DemoSeedResult(
        tenant_id=tenant_id,
        seeded_for_profile=profile_id,
        scenario_count=len([item for item in demo_scenarios() if item.persona == profile_id]),
        workflow_ids=workflow_ids,
        review_queue_count=len([item for item in reviews if item.profile_id == profile_id]),
        payment_count=len(payments),
    )


def _seed_demo_policies(tenant_id: str) -> None:
    policies = [
        PaymentPolicyCreate(
            category="electricity",
            vendor_name="Tata Power",
            max_amount_minor=1000000,
            currency="INR",
            requires_hitl_above_minor=500000,
        ),
        PaymentPolicyCreate(
            category="internet",
            vendor_name="Airtel Business",
            max_amount_minor=300000,
            currency="INR",
            requires_hitl_above_minor=250000,
        ),
        PaymentPolicyCreate(
            category="vendor_services",
            vendor_name="Fresh Pest Control Services",
            max_amount_minor=50000,
            currency="INR",
            requires_hitl_above_minor=50000,
        ),
    ]
    for policy in policies:
        upsert_policy(tenant_id, policy)

