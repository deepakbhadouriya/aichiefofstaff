from libs.schemas.profile import UserProfileView

_PROFILES: dict[str, list[UserProfileView]] = {
    "demo-tenant": [
        UserProfileView(
            id="demo_user",
            tenant_id="demo-tenant",
            display_name="Demo Finance Manager",
            email="demo@afra.local",
            persona_label="Persona 1",
            description="Seeded walkthrough profile with realistic bills, vendors, and approvals until live source systems are connected.",
            operating_mode="demo_seeded",
            seeded_data_enabled=True,
            capabilities=["policy:read", "policy:write", "payment:approve", "audit:read"],
            default_vendor_count=6,
            integration_status_summary="Demo data active with live-connector preview and safe fallbacks.",
        ),
        UserProfileView(
            id="actual_user",
            tenant_id="demo-tenant",
            display_name="Actual Finance Operator",
            email="ops@customer.example",
            persona_label="Persona 2",
            description="Production-oriented profile for real tenants using actual connectors, realtime status monitoring, and seeded fallback only when a source is not ready.",
            operating_mode="live_connectors",
            seeded_data_enabled=False,
            capabilities=["policy:read", "payment:approve", "payment:execute", "audit:read", "review:resolve"],
            default_vendor_count=0,
            integration_status_summary="Ready for live connectors once credentials and provider onboarding are completed.",
        ),
    ]
}


def list_profiles(tenant_id: str) -> list[UserProfileView]:
    return _PROFILES.get(tenant_id, _PROFILES["demo-tenant"])


def get_profile(tenant_id: str, profile_id: str) -> UserProfileView:
    profiles = list_profiles(tenant_id)
    for profile in profiles:
        if profile.id == profile_id:
            return profile
    return profiles[0]

