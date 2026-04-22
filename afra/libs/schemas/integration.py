from datetime import datetime

from pydantic import BaseModel


class IntegrationView(BaseModel):
    id: str
    tenant_id: str
    profile_id: str
    product_name: str
    category: str
    mode: str
    status: str
    seeded_fallback: bool
    realtime_enabled: bool
    polling_interval_seconds: int
    last_sync_at: datetime
    status_message: str


class IntegrationRealtimeSnapshot(BaseModel):
    tenant_id: str
    profile_id: str
    checked_at: datetime
    overall_status: str
    connectors: list[IntegrationView]

