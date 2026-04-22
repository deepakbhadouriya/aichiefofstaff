BEGIN;

CREATE TABLE IF NOT EXISTS user_profiles (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    display_name TEXT NOT NULL,
    email TEXT NOT NULL,
    persona_label TEXT NOT NULL,
    description TEXT NOT NULL,
    operating_mode TEXT NOT NULL,
    seeded_data_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    capabilities JSONB NOT NULL DEFAULT '[]'::jsonb,
    default_vendor_count INTEGER NOT NULL DEFAULT 0,
    integration_status_summary TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS product_integrations (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    profile_id TEXT NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    mode TEXT NOT NULL,
    status TEXT NOT NULL,
    seeded_fallback BOOLEAN NOT NULL DEFAULT FALSE,
    realtime_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    polling_interval_seconds INTEGER NOT NULL DEFAULT 30,
    last_sync_at TIMESTAMPTZ,
    status_message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_profiles_tenant_mode
    ON user_profiles (tenant_id, operating_mode);

CREATE INDEX IF NOT EXISTS idx_product_integrations_tenant_profile
    ON product_integrations (tenant_id, profile_id);

INSERT INTO user_profiles (
    id,
    tenant_id,
    display_name,
    email,
    persona_label,
    description,
    operating_mode,
    seeded_data_enabled,
    capabilities,
    default_vendor_count,
    integration_status_summary
)
VALUES
(
    'demo_user',
    'demo-tenant',
    'Demo Finance Manager',
    'demo@afra.local',
    'Persona 1',
    'Seeded walkthrough profile with realistic bills, vendors, and approvals until live source systems are connected.',
    'demo_seeded',
    TRUE,
    '["policy:read", "policy:write", "payment:approve", "audit:read"]'::jsonb,
    6,
    'Demo data active with live-connector preview and safe fallbacks.'
),
(
    'actual_user',
    'demo-tenant',
    'Actual Finance Operator',
    'ops@customer.example',
    'Persona 2',
    'Production-oriented profile for real tenants using actual connectors, realtime status monitoring, and seeded fallback only when a source is not ready.',
    'live_connectors',
    FALSE,
    '["policy:read", "payment:approve", "payment:execute", "audit:read", "review:resolve"]'::jsonb,
    0,
    'Ready for live connectors once credentials and provider onboarding are completed.'
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO product_integrations (
    id,
    tenant_id,
    profile_id,
    product_name,
    category,
    mode,
    status,
    seeded_fallback,
    realtime_enabled,
    polling_interval_seconds,
    last_sync_at,
    status_message
)
VALUES
(
    'int-setu-bbps-demo',
    'demo-tenant',
    'demo_user',
    'Setu BBPS',
    'payments',
    'demo_preview',
    'healthy',
    TRUE,
    TRUE,
    30,
    NOW(),
    'Realtime preview is polling a mocked Setu adapter with seeded bill balances.'
),
(
    'int-setu-bbps-live',
    'demo-tenant',
    'actual_user',
    'Setu BBPS',
    'payments',
    'live',
    'pending_credentials',
    TRUE,
    TRUE,
    30,
    NOW(),
    'Live BBPS connector is wired in code and waiting for provider credentials and webhook registration.'
)
ON CONFLICT (id) DO NOTHING;

COMMIT;

