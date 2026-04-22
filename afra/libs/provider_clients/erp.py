from dataclasses import dataclass
from datetime import datetime

from libs.time import utc_now

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
                checked_at=utc_now(),
                message="ERP connector is waiting for vendor master and chart-of-accounts mapping.",
            )
        return ERPHeartbeat(
            status="healthy",
            checked_at=utc_now(),
            message="Seeded ledger sync is ready for walkthrough and audit demonstrations.",
        )
