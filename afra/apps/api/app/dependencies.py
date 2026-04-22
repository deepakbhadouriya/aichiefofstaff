from fastapi import Header

from libs.db.settings import get_settings


def get_request_context(
    x_request_id: str | None = Header(default=None, alias="X-Request-ID"),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
    x_profile_id: str | None = Header(default=None, alias="X-Profile-ID"),
) -> dict[str, str]:
    settings = get_settings()
    return {
        "x_request_id": x_request_id or "req-local-dev",
        "tenant_id": x_tenant_id or settings.default_tenant,
        "profile_id": x_profile_id or settings.default_profile_id,
    }
