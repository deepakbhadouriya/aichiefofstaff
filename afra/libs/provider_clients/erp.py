from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass
class ERPHeartbeat:
    status: str
    checked_at: datetime
    message: str


class ERPClient:
    def heartbeat(self, live_mode: bool) -> ERPHeartbeat:
        if live_mode:
            return ERPHeartbeat(
                status="pending_mapping",
                checked_at=datetime.now(UTC),
                message="ERP connector is waiting for vendor master and chart-of-accounts mapping.",
            )
        return ERPHeartbeat(
            status="healthy",
            checked_at=datetime.now(UTC),
            message="Seeded ledger sync is ready for walkthrough and audit demonstrations.",
        )

