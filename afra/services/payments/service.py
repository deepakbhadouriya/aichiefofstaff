from libs.provider_clients.setu import SetuClient
from libs.schemas.payment import PaymentRecord
from libs.schemas.runtime import PaymentIntentRecord, WorkflowRunRecord
from libs.time import utc_now
from services.personas.service import get_profile
from services.runtime.store import load_state, save_state

_SETU_CLIENT = SetuClient()


def fetch_live_bill(
    tenant_id: str,
    profile_id: str,
    vendor_name: str,
    biller_reference: str,
    amount_minor_hint: int | None = None,
) -> dict[str, str | int]:
    bill = _SETU_CLIENT.fetch_bill(vendor_name, biller_reference, amount_minor_hint)
    profile = get_profile(tenant_id, profile_id)
    source_type = "seeded_demo" if profile.seeded_data_enabled else "connector_live"
    return {
        "vendor_name": bill.vendor_name,
        "biller_reference": bill.biller_reference,
        "amount_minor": bill.amount_minor,
        "currency": bill.currency,
        "status": bill.status,
        "integration_mode": profile.operating_mode,
        "source_type": source_type,
    }


def list_payments(tenant_id: str, profile_id: str) -> list[PaymentRecord]:
    state = load_state()
    payments = [
        PaymentRecord.model_validate(item)
        for item in state["payments"].values()
        if item["tenant_id"] == tenant_id and item["profile_id"] == profile_id
    ]
    return sorted(payments, key=lambda item: item.created_at, reverse=True)


def get_or_create_payment_intent(workflow: WorkflowRunRecord) -> PaymentIntentRecord:
    state = load_state()
    if workflow.payment_intent_id and workflow.payment_intent_id in state["payment_intents"]:
        return PaymentIntentRecord.model_validate(state["payment_intents"][workflow.payment_intent_id])

    intent = PaymentIntentRecord(
        id=f"pi-{workflow.id}",
        workflow_run_id=workflow.id,
        tenant_id=workflow.tenant_id,
        profile_id=workflow.profile_id,
        idempotency_key=f"{workflow.tenant_id}:{workflow.profile_id}:{workflow.id}",
        amount_minor=workflow.amount_minor,
        currency=workflow.currency,
        provider="setu-bbps-mock" if workflow.integration_mode == "demo_seeded" else "setu-bbps-live-ready",
        status="reserved",
        created_at=utc_now(),
    )
    state["payment_intents"][intent.id] = intent.model_dump(mode="json")
    save_state(state)
    return intent


def execute_payment(workflow: WorkflowRunRecord, intent: PaymentIntentRecord) -> PaymentRecord:
    state = load_state()
    existing = next(
        (
            PaymentRecord.model_validate(item)
            for item in state["payments"].values()
            if item["payment_intent_id"] == intent.id
        ),
        None,
    )
    if existing:
        return existing

    source_type = "seeded_demo" if workflow.integration_mode == "demo_seeded" else "connector_live"
    payment = PaymentRecord(
        id=f"pay-{workflow.id}",
        workflow_run_id=workflow.id,
        payment_intent_id=intent.id,
        tenant_id=workflow.tenant_id,
        profile_id=workflow.profile_id,
        vendor_name=workflow.request.vendor_name,
        amount_minor=workflow.amount_minor,
        currency=workflow.currency,
        status="succeeded",
        provider=intent.provider,
        integration_mode=workflow.integration_mode,
        source_type=source_type,
        idempotency_key=intent.idempotency_key,
        created_at=utc_now(),
    )
    state["payments"][payment.id] = payment.model_dump(mode="json")
    state["payment_intents"][intent.id]["status"] = "executed"
    save_state(state)
    return payment
