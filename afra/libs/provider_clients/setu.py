from dataclasses import dataclass
from datetime import datetime

from libs.time import utc_now

@dataclass
class SetuBill:
    vendor_name: str
    biller_reference: str
    amount_minor: int
    currency: str = "INR"
    status: str = "outstanding"


@dataclass
class ConnectorHeartbeat:
    status: str
    checked_at: datetime
    message: str


class SetuClient:
    """Mock provider client until BBPS credentials and contracts are available."""

    def fetch_bill(
        self,
        vendor_name: str,
        biller_reference: str,
        amount_minor_hint: int | None = None,
    ) -> SetuBill:
        return SetuBill(
            vendor_name=vendor_name,
            biller_reference=biller_reference,
            amount_minor=amount_minor_hint or 420000,
        )

    def heartbeat(self, live_mode: bool) -> ConnectorHeartbeat:
        if live_mode:
            return ConnectorHeartbeat(
                status="pending_credentials",
                checked_at=utc_now(),
                message="Live BBPS transport is configured in code and waiting for provider secrets.",
            )
        return ConnectorHeartbeat(
            status="healthy",
            checked_at=utc_now(),
            message="Demo BBPS polling is healthy with seeded balances and deterministic responses.",
        )
