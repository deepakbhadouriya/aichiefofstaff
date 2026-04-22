from datetime import UTC, datetime

from libs.provider_clients.setu import SetuClient
from libs.schemas.payment import PaymentRecord

_SETU_CLIENT = SetuClient()


def fetch_live_bill(
    vendor_name: str,
    biller_reference: str,
    amount_minor_hint: int | None = None,
) -> dict[str, str | int]:
    bill = _SETU_CLIENT.fetch_bill(vendor_name, biller_reference, amount_minor_hint)
    return {
        "vendor_name": bill.vendor_name,
        "biller_reference": bill.biller_reference,
        "amount_minor": bill.amount_minor,
        "currency": bill.currency,
        "status": bill.status,
    }


def list_payments(tenant_id: str) -> list[PaymentRecord]:
    return [
        PaymentRecord(
            id="pay-demo-001",
            tenant_id=tenant_id,
            vendor_name="Tata Power",
            amount_minor=420000,
            currency="INR",
            status="succeeded",
            provider="setu-bbps-mock",
            created_at=datetime.now(UTC),
        )
    ]

