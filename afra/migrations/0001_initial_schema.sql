BEGIN;

CREATE TABLE IF NOT EXISTS tenants (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    region TEXT NOT NULL DEFAULT 'IN',
    data_residency_zone TEXT NOT NULL DEFAULT 'india-local',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    role TEXT NOT NULL,
    capabilities JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS payment_policies (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    vendor_name TEXT NOT NULL,
    max_amount_minor BIGINT NOT NULL CHECK (max_amount_minor > 0),
    currency TEXT NOT NULL DEFAULT 'INR',
    requires_hitl_above_minor BIGINT NOT NULL CHECK (requires_hitl_above_minor > 0),
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS workflow_runs (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    graph_name TEXT NOT NULL,
    graph_state JSONB NOT NULL DEFAULT '{}'::jsonb,
    status TEXT NOT NULL,
    checkpoint_ref TEXT,
    x_request_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bills (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    vendor_name TEXT NOT NULL,
    source TEXT NOT NULL,
    external_bill_id TEXT NOT NULL,
    amount_minor BIGINT NOT NULL CHECK (amount_minor >= 0),
    due_at TIMESTAMPTZ,
    status TEXT NOT NULL,
    hash TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS payment_intents (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    bill_id TEXT NOT NULL REFERENCES bills(id) ON DELETE CASCADE,
    workflow_id TEXT NOT NULL REFERENCES workflow_runs(id) ON DELETE CASCADE,
    idempotency_key TEXT NOT NULL UNIQUE,
    requested_amount_minor BIGINT NOT NULL CHECK (requested_amount_minor > 0),
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS payments (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    payment_intent_id TEXT NOT NULL REFERENCES payment_intents(id) ON DELETE CASCADE,
    provider TEXT NOT NULL,
    provider_txn_id TEXT,
    status TEXT NOT NULL,
    submitted_at TIMESTAMPTZ,
    settled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_events (
    id BIGSERIAL PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    workflow_run_id TEXT REFERENCES workflow_runs(id) ON DELETE SET NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_payment_policies_tenant_vendor
    ON payment_policies (tenant_id, vendor_name);

CREATE INDEX IF NOT EXISTS idx_workflow_runs_tenant_request
    ON workflow_runs (tenant_id, x_request_id);

CREATE INDEX IF NOT EXISTS idx_bills_tenant_external
    ON bills (tenant_id, external_bill_id);

CREATE INDEX IF NOT EXISTS idx_payments_tenant_status
    ON payments (tenant_id, status);

CREATE INDEX IF NOT EXISTS idx_audit_events_tenant_entity
    ON audit_events (tenant_id, entity_type, entity_id);

INSERT INTO tenants (id, name)
VALUES ('demo-tenant', 'Demo Tenant')
ON CONFLICT (id) DO NOTHING;

INSERT INTO payment_policies (
    id,
    tenant_id,
    category,
    vendor_name,
    max_amount_minor,
    currency,
    requires_hitl_above_minor,
    status
)
VALUES (
    'pol-electricity-001',
    'demo-tenant',
    'electricity',
    'Tata Power',
    1000000,
    'INR',
    500000,
    'active'
)
ON CONFLICT (id) DO NOTHING;

COMMIT;

