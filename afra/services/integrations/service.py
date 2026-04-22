from datetime import UTC, datetime, timedelta

from libs.db.settings import get_settings
from libs.provider_clients.erp import ERPClient
from libs.provider_clients.mailbox import MailboxClient
from libs.provider_clients.setu import SetuClient
from libs.schemas.integration import IntegrationRealtimeSnapshot, IntegrationView

_SETU_CLIENT = SetuClient()
_ERP_CLIENT = ERPClient()
_MAILBOX_CLIENT = MailboxClient()


def _demo_connectors(tenant_id: str, profile_id: str) -> list[IntegrationView]:
    settings = get_settings()
    setu = _SETU_CLIENT.heartbeat(live_mode=False)
    erp = _ERP_CLIENT.heartbeat(live_mode=False)
    mailbox = _MAILBOX_CLIENT.heartbeat(live_mode=False)
    return [
        IntegrationView(
            id="int-setu-bbps-demo",
            tenant_id=tenant_id,
            profile_id=profile_id,
            product_name="Setu BBPS",
            category="payments",
            mode="demo_preview",
            status=setu.status,
            seeded_fallback=True,
            realtime_enabled=True,
            polling_interval_seconds=settings.realtime_sync_interval_seconds,
            last_sync_at=setu.checked_at - timedelta(seconds=12),
            status_message=setu.message,
        ),
        IntegrationView(
            id="int-zoho-books-demo",
            tenant_id=tenant_id,
            profile_id=profile_id,
            product_name="Zoho Books",
            category="erp",
            mode="demo_seeded",
            status=erp.status,
            seeded_fallback=True,
            realtime_enabled=True,
            polling_interval_seconds=settings.realtime_sync_interval_seconds,
            last_sync_at=erp.checked_at - timedelta(seconds=20),
            status_message=erp.message,
        ),
        IntegrationView(
            id="int-comms-demo",
            tenant_id=tenant_id,
            profile_id=profile_id,
            product_name="Email and Vendor Comms",
            category="communications",
            mode="demo_seeded",
            status=mailbox.status,
            seeded_fallback=True,
            realtime_enabled=False,
            polling_interval_seconds=settings.realtime_sync_interval_seconds,
            last_sync_at=mailbox.checked_at - timedelta(minutes=3),
            status_message=mailbox.message,
        ),
    ]


def _live_connectors(tenant_id: str, profile_id: str) -> list[IntegrationView]:
    settings = get_settings()
    setu = _SETU_CLIENT.heartbeat(live_mode=True)
    erp = _ERP_CLIENT.heartbeat(live_mode=True)
    mailbox = _MAILBOX_CLIENT.heartbeat(live_mode=True)
    return [
        IntegrationView(
            id="int-setu-bbps-live",
            tenant_id=tenant_id,
            profile_id=profile_id,
            product_name="Setu BBPS",
            category="payments",
            mode="live",
            status=setu.status,
            seeded_fallback=True,
            realtime_enabled=True,
            polling_interval_seconds=settings.realtime_sync_interval_seconds,
            last_sync_at=setu.checked_at - timedelta(minutes=5),
            status_message=setu.message,
        ),
        IntegrationView(
            id="int-tally-erp-live",
            tenant_id=tenant_id,
            profile_id=profile_id,
            product_name="ERP / Ledger Sync",
            category="erp",
            mode="live",
            status=erp.status,
            seeded_fallback=True,
            realtime_enabled=True,
            polling_interval_seconds=settings.realtime_sync_interval_seconds,
            last_sync_at=erp.checked_at - timedelta(minutes=6),
            status_message=erp.message,
        ),
        IntegrationView(
            id="int-mailbox-live",
            tenant_id=tenant_id,
            profile_id=profile_id,
            product_name="Mailbox Sync",
            category="communications",
            mode="live",
            status=mailbox.status,
            seeded_fallback=True,
            realtime_enabled=True,
            polling_interval_seconds=settings.realtime_sync_interval_seconds,
            last_sync_at=mailbox.checked_at - timedelta(minutes=8),
            status_message=mailbox.message,
        ),
    ]


def list_integrations(tenant_id: str, profile_id: str) -> list[IntegrationView]:
    if profile_id == "actual_user":
        return _live_connectors(tenant_id, profile_id)
    return _demo_connectors(tenant_id, profile_id)


def get_realtime_snapshot(tenant_id: str, profile_id: str) -> IntegrationRealtimeSnapshot:
    connectors = list_integrations(tenant_id, profile_id)
    overall_status = "healthy"
    if any(connector.status.startswith("pending") for connector in connectors):
        overall_status = "attention_required"
    return IntegrationRealtimeSnapshot(
        tenant_id=tenant_id,
        profile_id=profile_id,
        checked_at=datetime.now(UTC),
        overall_status=overall_status,
        connectors=connectors,
    )
