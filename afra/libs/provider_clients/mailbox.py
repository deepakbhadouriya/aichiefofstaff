from dataclasses import dataclass
from datetime import datetime

from libs.time import utc_now

@dataclass
class MailboxHeartbeat:
    status: str
    checked_at: datetime
    message: str


class MailboxClient:
    def heartbeat(self, live_mode: bool) -> MailboxHeartbeat:
        if live_mode:
            return MailboxHeartbeat(
                status="pending_oauth",
                checked_at=utc_now(),
                message="Mailbox sync is waiting for OAuth consent and scoped mailbox access.",
            )
        return MailboxHeartbeat(
            status="healthy",
            checked_at=utc_now(),
            message="Seeded invoice emails and vendor conversation trails are available for demo mode.",
        )
