from libs.schemas.profile import UserProfileView

_PROFILES: dict[str, list[UserProfileView]] = {
    "demo-tenant": [
        UserProfileView(
            id="sme_owner",
            tenant_id="demo-tenant",
            display_name="SME AI Chief of Staff",
            email="owner@sme-corp.com",
            persona_label="Executive Mode",
            description="The SME Owner's digital twin. Manages relationships, payments, and strategic tasks based on personal context.",
            operating_mode="executive",
            seeded_data_enabled=True,
            capabilities=["policy:read", "policy:write", "payment:approve", "audit:read", "crm:read", "crm:write"],
            default_vendor_count=6,
            integration_status_summary="Context active. Agent monitoring Gmail, Bank, and Drive.",
            communication_style="Professional, warm but firm. Emphasize SME loyalty.",
            decision_preferences="Never pay before due date unless a discount applies. Flag any 10% deviation from last month."
        ),
        UserProfileView(
            id="admin_user",
            tenant_id="demo-tenant",
            display_name="Administrator",
            email="admin@afra.local",
            persona_label="System Ops Mode",
            description="System administrator with full access to connectors, tenant configuration, and platform audit logs.",
            operating_mode="live_connectors",
            seeded_data_enabled=False,
            capabilities=["admin:full", "policy:write", "audit:read", "integrations:manage"],
            default_vendor_count=0,
            integration_status_summary="System healthy. 4 active connectors.",
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

def update_persona_context(tenant_id: str, profile_id: str, comm_style: str, dec_prefs: str) -> UserProfileView:
    profiles = list_profiles(tenant_id)
    for profile in profiles:
        if profile.id == profile_id:
            profile.communication_style = comm_style
            profile.decision_preferences = dec_prefs
            return profile
    return None

def create_dynamic_profile(
    tenant_id: str,
    profile_id: str,
    display_name: str,
    email: str,
    description: str,
) -> UserProfileView:
    profile = UserProfileView(
        id=profile_id,
        tenant_id=tenant_id,
        display_name=display_name,
        email=email,
        persona_label="Onboarded User",
        description=description,
        operating_mode="executive",
        seeded_data_enabled=False,
        capabilities=["policy:read", "policy:write", "payment:approve", "audit:read", "crm:read"],
        default_vendor_count=0,
        integration_status_summary="Account created. Define your agent context to start.",
    )
    if tenant_id not in _PROFILES:
        _PROFILES[tenant_id] = []
    _PROFILES[tenant_id].append(profile)
    return profile
