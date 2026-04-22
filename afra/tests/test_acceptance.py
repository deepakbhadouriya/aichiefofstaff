import os
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from libs.db.settings import get_settings
from libs.schemas.policy import PaymentPolicyCreate
from libs.schemas.runtime import WorkflowRunRecord
from libs.schemas.workflow import WorkflowRunRequest
from libs.time import utc_now
from services.audit.service import get_workflow_run, list_audit_events, list_reviews, save_workflow_record
from services.demo.service import demo_scenarios, seed_demo_data
from services.integrations.service import get_realtime_snapshot
from services.ledger_sync.service import list_ledger_syncs
from services.payments.orchestration import (
    resume_incomplete_workflows,
    resume_review_workflow,
    run_bill_payment_flow,
)
from services.payments.service import list_payments
from services.policy.service import list_policies, upsert_policy
from services.runtime.store import reset_state


class AcceptanceCriteriaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        os.environ["AFRA_RUNTIME_STORE_PATH"] = f"{self.temp_dir.name}/runtime_store.json"
        get_settings.cache_clear()
        reset_state()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()
        os.environ.pop("AFRA_RUNTIME_STORE_PATH", None)
        get_settings.cache_clear()

    def test_demo_user_seeded_autopay_flow_persists_payment_and_ledger(self) -> None:
        policy = upsert_policy(
            "demo-tenant",
            payload=PaymentPolicyCreate(
                category="electricity",
                vendor_name="BESCOM Demo",
                max_amount_minor=900000,
                currency="INR",
                requires_hitl_above_minor=500000,
            ),
        )
        self.assertEqual(policy.category, "electricity")

        result = run_bill_payment_flow(
            tenant_id="demo-tenant",
            profile_id="demo_user",
            request_id="req-demo-seeded",
            request=WorkflowRunRequest(
                vendor_name="Tata Power",
                category="electricity",
                biller_reference="CA-1023001",
                amount_minor_hint=420000,
            ),
        )

        self.assertEqual(result.decision, "approved_for_autopay")
        self.assertEqual(result.current_state, "ledger_updated")
        self.assertEqual(result.x_request_id, "req-demo-seeded")
        self.assertEqual(result.integration_mode, "demo_seeded")
        self.assertIsNotNone(result.payment_intent_id)
        self.assertIsNotNone(result.payment_id)
        self.assertIsNotNone(result.ledger_sync_id)

        payments = list_payments("demo-tenant", "demo_user")
        self.assertEqual(len(payments), 1)
        self.assertEqual(payments[0].idempotency_key, f"demo-tenant:demo_user:{result.id}")

        audit_events = list_audit_events(result.id)
        self.assertGreaterEqual(len(audit_events), 1)
        self.assertEqual(list_ledger_syncs()[0].payment_id, result.payment_id)

    def test_demo_user_anomaly_goes_to_review_queue_and_approval_is_idempotent(self) -> None:
        result = run_bill_payment_flow(
            tenant_id="demo-tenant",
            profile_id="demo_user",
            request_id="req-demo-review",
            request=WorkflowRunRequest(
                vendor_name="Tata Power",
                category="electricity",
                biller_reference="CA-2023002",
                amount_minor_hint=640000,
            ),
        )

        self.assertEqual(result.current_state, "pending_human_review")
        reviews = list_reviews("demo-tenant")
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0].workflow_run_id, result.id)

        first = resume_review_workflow("demo-tenant", "demo_user", result.id, "reviewer-1")
        second = resume_review_workflow("demo-tenant", "demo_user", result.id, "reviewer-1")
        self.assertEqual(first.decision, "approved")
        self.assertEqual(second.decision, "approved")

        final_workflow = get_workflow_run("demo-tenant", "demo_user", result.id)
        self.assertEqual(final_workflow.current_state, "ledger_updated")
        self.assertEqual(len(list_payments("demo-tenant", "demo_user")), 1)

    def test_worker_resume_recovers_approved_workflow(self) -> None:
        pending = WorkflowRunRecord(
            id="wf-demo-resume",
            tenant_id="demo-tenant",
            profile_id="demo_user",
            x_request_id="req-resume",
            request=WorkflowRunRequest(
                vendor_name="Tata Power",
                category="electricity",
                biller_reference="CA-3033003",
                amount_minor_hint=410000,
            ),
            current_state="approved",
            decision="approved_for_autopay",
            amount_minor=410000,
            currency="INR",
            integration_mode="demo_seeded",
            requires_human_review=False,
            evidence=[],
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        save_workflow_record(pending)

        resumed = resume_incomplete_workflows()
        self.assertEqual(len(resumed), 1)
        refreshed = get_workflow_run("demo-tenant", "demo_user", "wf-demo-resume")
        self.assertEqual(refreshed.current_state, "ledger_updated")
        self.assertIsNotNone(refreshed.payment_id)

    def test_actual_user_keeps_live_connector_mode_with_switch_ready_integration(self) -> None:
        result = run_bill_payment_flow(
            tenant_id="demo-tenant",
            profile_id="actual_user",
            request_id="req-actual-user",
            request=WorkflowRunRequest(
                vendor_name="Tata Power",
                category="electricity",
                biller_reference="CA-9090001",
                amount_minor_hint=420000,
            ),
        )

        self.assertEqual(result.integration_mode, "live_connectors")
        self.assertEqual(result.current_state, "ledger_updated")
        payments = list_payments("demo-tenant", "actual_user")
        self.assertEqual(len(payments), 1)
        self.assertEqual(payments[0].provider, "setu-bbps-live-ready")

        snapshot = get_realtime_snapshot("demo-tenant", "actual_user")
        self.assertEqual(snapshot.overall_status, "attention_required")
        self.assertTrue(any(connector.status.startswith("pending") for connector in snapshot.connectors))

    def test_seed_demo_data_creates_happy_and_negative_scenarios_for_demo_user(self) -> None:
        seeded = seed_demo_data("demo-tenant", "demo_user")
        self.assertEqual(seeded.scenario_count, 4)
        self.assertEqual(len(seeded.workflow_ids), 4)
        self.assertGreaterEqual(seeded.payment_count, 2)
        self.assertGreaterEqual(seeded.review_queue_count, 1)

        workflows = [get_workflow_run("demo-tenant", "demo_user", workflow_id) for workflow_id in seeded.workflow_ids]
        decisions = {workflow.decision for workflow in workflows}
        states = {workflow.current_state for workflow in workflows}

        self.assertIn("approved_for_autopay", decisions)
        self.assertIn("requires_human_review", decisions)
        self.assertIn("closed", states)
        self.assertIn("ledger_updated", states)

    def test_demo_scenarios_and_connector_labels_match_sme_language(self) -> None:
        scenarios = demo_scenarios()
        self.assertGreaterEqual(len(scenarios), 5)
        self.assertTrue(any(item.title == "Happy path utility autopay" for item in scenarios))

        demo_snapshot = get_realtime_snapshot("demo-tenant", "demo_user")
        product_names = {item.product_name for item in demo_snapshot.connectors}
        self.assertIn("Setu BBPS", product_names)
        self.assertIn("Zoho Books SME Ledger", product_names)
        self.assertIn("Google Workspace Gmail", product_names)


if __name__ == "__main__":
    unittest.main()
