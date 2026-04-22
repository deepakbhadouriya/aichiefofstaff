from dataclasses import dataclass
from datetime import UTC, datetime


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
                checked_at=datetime.now(UTC),
                message="Mailbox sync is waiting for OAuth consent and scoped mailbox access.",
            )
        return MailboxHeartbeat(
            status="healthy",
            checked_at=datetime.now(UTC),
            message="Seeded invoice emails and vendor conversation trails are available for demo mode.",
        )

