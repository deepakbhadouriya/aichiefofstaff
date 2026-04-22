from libs.schemas.ledger import LedgerSyncRecord
from libs.time import utc_now
from services.runtime.store import load_state, save_state


def sync_payment_outcome(
    tenant_id: str,
    workflow_run_id: str,
    payment_id: str,
    adapter_name: str = "seeded-ledger-adapter",
) -> LedgerSyncRecord:
    state = load_state()
    sync_id = f"ledger-{payment_id}"
    existing = state["ledger_syncs"].get(sync_id)
    if existing:
        return LedgerSyncRecord.model_validate(existing)

    record = LedgerSyncRecord(
        id=sync_id,
        tenant_id=tenant_id,
        workflow_run_id=workflow_run_id,
        payment_id=payment_id,
        adapter_name=adapter_name,
        status="synced",
        synced_at=utc_now(),
    )
    state["ledger_syncs"][record.id] = record.model_dump(mode="json")
    save_state(state)
    return record


def list_ledger_syncs() -> list[LedgerSyncRecord]:
    state = load_state()
    return [LedgerSyncRecord.model_validate(item) for item in state["ledger_syncs"].values()]

