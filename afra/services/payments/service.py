from datetime import UTC, datetime

from libs.provider_clients.setu import SetuClient
from libs.schemas.payment import PaymentRecord
from services.personas.service import get_profile

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
    profile = get_profile(tenant_id, profile_id)
    source_type = "seeded_demo" if profile.seeded_data_enabled else "connector_live"
    provider = "setu-bbps-mock" if profile.seeded_data_enabled else "setu-bbps-live-ready"
    return [
        PaymentRecord(
            id="pay-demo-001",
            tenant_id=tenant_id,
            profile_id=profile_id,
            vendor_name="Tata Power",
            amount_minor=420000,
            currency="INR",
            status="succeeded",
            provider=provider,
            integration_mode=profile.operating_mode,
            source_type=source_type,
            created_at=datetime.now(UTC),
        ),
        PaymentRecord(
            id="pay-demo-002" if profile.seeded_data_enabled else "pay-live-001",
            tenant_id=tenant_id,
            profile_id=profile_id,
            vendor_name="Airtel Business",
            amount_minor=1820000 if profile.seeded_data_enabled else 1160000,
            currency="INR",
            status="pending_review" if profile.seeded_data_enabled else "awaiting_connector_activation",
            provider=provider,
            integration_mode=profile.operating_mode,
            source_type=source_type,
            created_at=datetime.now(UTC),
        ),
    ]
