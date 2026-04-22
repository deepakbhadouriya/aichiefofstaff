# Autonomous Financial Reconciliation Agent (A-FRA) MVP Blueprint

## 1. Objective

Build a production-ready MVP for an Autonomous Financial Reconciliation Agent focused on autonomous bill payment for SMEs in India. The MVP must reduce manual finance operations effort, operate with deterministic control flow, and maintain full auditability for every financial action.

This blueprint translates the Statement of Work into an implementation-ready technical plan.

## 2. MVP Outcome

The MVP automates recurring B2B liabilities such as electricity bills, telecom bills, internet bills, and approved vendor payouts where a programmatic payment rail is available.

Primary user outcomes:

- Finance teams define auto-payment rules once.
- The system fetches outstanding balances in real time.
- The system validates the bill against historical context and policy.
- The system either:
  - auto-pays within policy, or
  - routes the item to human review when anomalous.
- The system writes an auditable record of every decision and action.

## 3. Non-Negotiable Design Principles

- Deterministic orchestration for all payment-critical paths.
- Durable checkpointing and resumability for every long-running workflow.
- Idempotent execution to prevent duplicate payments or ledger writes.
- Explicit Human-in-the-Loop (HITL) breakpoints on anomalies or policy violations.
- Capability-scoped access for every actor and service.
- Time-bound, delegated third-party credentials using OBO token exchange.
- India-local data residency for transaction and retrieval data.
- End-to-end auditability with request correlation IDs.

## 4. Recommended Architecture

### 4.1 Core Technology Stack

- Orchestration: LangGraph
- LLM: OpenAI API
- Backend API: Python with FastAPI
- Worker runtime: Python
- Retrieval store: PostgreSQL with `pgvector` plus PostgreSQL full-text search
- Transactional database: PostgreSQL
- Cache / task coordination: Redis
- Object storage: S3-compatible India-region object store for invoices, logs, and artifacts
- Frontend: Next.js or React SPA with a minimal operations dashboard
- Containerization: Docker
- Deployment target: Kubernetes
- Observability: OpenTelemetry, Prometheus, Grafana, Loki
- Secrets: Vault or cloud-managed secret store

### 4.2 Why `pgvector` First

For an SME-focused MVP, PostgreSQL + `pgvector` is the best default choice over Pinecone, Weaviate, or Qdrant because it simplifies compliance, tenant isolation, operational overhead, and auditability while still supporting hybrid retrieval:

- Dense retrieval: vector similarity via `pgvector`
- Sparse retrieval: PostgreSQL full-text / trigram / exact-match indexes
- Strong transactional guarantees
- Easier India-local hosting
- Lower infrastructure complexity for MVP

Qdrant is a strong second choice if retrieval scale or recall tuning outgrows PostgreSQL.

## 5. Service Decomposition

Keep the MVP modular, but avoid over-fragmenting into too many microservices early. Start with a modular monolith plus isolated workers, then split services after the workflow stabilizes.

### 5.1 Initial Services

1. `api-gateway`
- Exposes REST APIs for dashboard and webhook consumers
- Authenticates users and issues session tokens
- Generates `x-request-id` for every client request

2. `policy-service`
- Stores tenant payment rules and authorization thresholds
- Evaluates policy compliance deterministically
- Returns a machine-readable decision object

3. `orchestrator-service`
- Runs LangGraph workflows
- Persists checkpoints and graph state
- Coordinates tool calls and HITL pauses

4. `retrieval-service`
- Indexes invoices, emails, payment logs, and vendor metadata
- Performs hybrid retrieval and returns evidence bundles

5. `payments-service`
- Wraps Setu / BBPS integration
- Manages bill fetch, beneficiary verification, payment execution, and status polling
- Applies idempotency keys to external actions

6. `ledger-sync-service`
- Writes successful transaction records to ERP / accounting systems
- Retries safely on downstream failures

7. `audit-service`
- Persists immutable audit events and decision traces
- Supports search by tenant, vendor, biller, request ID, workflow ID, and payment ID

8. `notification-service`
- Sends HITL alerts via email, WhatsApp, Slack, or in-app notifications

9. `frontend-dashboard`
- Payment rule management
- Transaction monitoring
- HITL review and approval queue
- Audit search and drill-down

## 6. LangGraph Workflow Design

The workflow must be deterministic and resumable. Every state transition should be explicitly represented and checkpointed.

### 6.1 Graph Nodes

1. `context_definition`
- Load tenant payment policy, vendor rules, thresholds, user preferences, and approved billers
- Normalize constraints into structured policy state

2. `retrieve_context`
- Query hybrid retrieval against invoices, prior payments, historical bill ranges, vendor contracts, and related communication
- Return evidence and confidence metadata

3. `fetch_bill`
- Call Setu / BBPS to fetch live outstanding balance, due date, bill metadata, and biller reference

4. `validate_bill`
- Deterministically compare fetched bill with policy and retrieved evidence
- Check bill amount, biller identity, due date, recurrence pattern, duplicate risk, and prior payment status

5. `decision_gate`
- Branch into:
  - `approved_for_autopay`
  - `requires_human_review`
  - `rejected`

6. `reserve_funds`
- Trigger fund-blocking or payment-preparation step if the payment rail supports it
- If pre-blocking is unavailable, create an approval-ready payment intent with short TTL

7. `execute_payment`
- Perform the payment using idempotency keys and a stable workflow execution ID

8. `confirm_status`
- Poll or receive callback until terminal state:
  - `success`
  - `pending`
  - `failed`

9. `update_ledger`
- Sync result to ERP / accounting system
- Write transaction ID, reference ID, amount, timestamp, and status

10. `write_audit`
- Persist the full decision trail, evidence references, tool results, user approval if any, and correlated IDs

11. `notify`
- Notify finance stakeholders of success, failure, or need for review

### 6.2 HITL Breakpoints

Human review is mandatory when any of the following occurs:

- Bill amount exceeds configured threshold
- Vendor or biller mismatch
- Duplicate or near-duplicate payment suspicion
- Large deviation from historical bill range
- Missing retrieval evidence
- Setu / BBPS confidence or upstream status ambiguity
- Payment rail returns non-terminal or degraded response

### 6.3 State Model

Suggested workflow states:

- `created`
- `policy_loaded`
- `context_retrieved`
- `bill_fetched`
- `validated`
- `pending_human_review`
- `approved`
- `payment_reserved`
- `payment_submitted`
- `payment_pending`
- `payment_succeeded`
- `payment_failed`
- `ledger_updated`
- `audit_recorded`
- `closed`

## 7. Data Model

### 7.1 Core Tables

1. `tenants`
- `id`
- `name`
- `region`
- `data_residency_zone`
- `status`

2. `users`
- `id`
- `tenant_id`
- `email`
- `role`
- `capabilities`

3. `payment_policies`
- `id`
- `tenant_id`
- `category`
- `vendor_id`
- `biller_id`
- `max_amount_minor`
- `currency`
- `allowed_days`
- `requires_hitl_above_minor`
- `status`

4. `vendors`
- `id`
- `tenant_id`
- `name`
- `tax_id`
- `biller_reference`
- `payment_method`
- `status`

5. `bills`
- `id`
- `tenant_id`
- `vendor_id`
- `source`
- `external_bill_id`
- `amount_minor`
- `due_at`
- `status`
- `hash`

6. `payment_intents`
- `id`
- `tenant_id`
- `bill_id`
- `workflow_id`
- `idempotency_key`
- `requested_amount_minor`
- `status`

7. `payments`
- `id`
- `tenant_id`
- `payment_intent_id`
- `provider`
- `provider_txn_id`
- `status`
- `submitted_at`
- `settled_at`

8. `workflow_runs`
- `id`
- `tenant_id`
- `graph_name`
- `graph_state`
- `status`
- `checkpoint_ref`
- `x_request_id`

9. `audit_events`
- `id`
- `tenant_id`
- `workflow_run_id`
- `entity_type`
- `entity_id`
- `event_type`
- `payload`
- `created_at`

10. `documents`
- `id`
- `tenant_id`
- `document_type`
- `storage_uri`
- `sha256`
- `metadata`

11. `retrieval_chunks`
- `id`
- `tenant_id`
- `document_id`
- `chunk_text`
- `embedding`
- `keywords`
- `metadata`

## 8. API Design

### 8.1 Dashboard / Internal APIs

- `POST /api/v1/policies`
- `GET /api/v1/policies`
- `PATCH /api/v1/policies/{id}`
- `GET /api/v1/payments`
- `GET /api/v1/payments/{id}`
- `GET /api/v1/reviews`
- `POST /api/v1/reviews/{workflowRunId}/approve`
- `POST /api/v1/reviews/{workflowRunId}/reject`
- `GET /api/v1/audit-events`
- `GET /api/v1/workflows/{id}`

### 8.2 Integration APIs

- `POST /api/v1/webhooks/setu`
- `POST /api/v1/webhooks/erp`
- `POST /api/v1/ingest/documents`
- `POST /api/v1/ingest/emails`

### 8.3 Idempotency

All payment-affecting endpoints must accept:

- `Idempotency-Key`
- `X-Request-ID`

Rules:

- Duplicate `Idempotency-Key` with same payload returns original response
- Duplicate `Idempotency-Key` with different payload is rejected
- Every external provider request is logged against the originating workflow run

## 9. OpenAI Usage Pattern

Use OpenAI where reasoning is useful, but never allow the model to directly decide payment execution without deterministic rule enforcement.

### 9.1 Recommended LLM Responsibilities

- Parse natural-language payment rules into a structured policy draft
- Extract entities from emails, invoices, and payment memos
- Summarize retrieval evidence for reviewer display
- Classify anomaly rationale for operator readability
- Generate tool arguments where input is semi-structured

### 9.2 Where Not to Use the LLM

- Final approval logic
- Payment amount arithmetic
- Idempotency decisions
- Duplicate payment prevention
- Ledger posting success criteria
- Capability enforcement

### 9.3 Model Pattern

- Use a fast, reliable model for classification, extraction, and tool planning
- Use structured outputs and JSON schema validation
- Capture model inputs/outputs in audit logs with redaction rules

## 10. Retrieval and Hybrid Search Design

### 10.1 Retrieval Inputs

- Historical invoices
- Email conversations with vendors
- Past payment logs
- Vendor master records
- Biller metadata
- Policy documents
- Exceptions and approval history

### 10.2 Retrieval Strategy

For each billing event:

1. Exact match search for biller ID, account number, PO number, invoice number
2. Full-text search for keywords and references
3. Dense vector retrieval for semantic matches
4. Rank and merge into an evidence bundle
5. Pass evidence to deterministic validator and reviewer UI

### 10.3 Evidence Scoring

Suggested signals:

- exact identifier match
- vendor name similarity
- historical amount band fit
- recurrence consistency
- due date pattern consistency
- previous approval history

## 11. Security and Compliance Design

### 11.1 Capability-Based Access Control

Represent permissions as explicit capabilities rather than broad roles alone.

Examples:

- `policy:read`
- `policy:write`
- `payment:approve`
- `payment:execute`
- `audit:read`
- `review:resolve`

Every API route and workflow action must verify required capabilities.

### 11.2 On-Behalf-Of Token Exchange

Third-party integrations must not use long-lived universal tokens. Use delegated, narrowly scoped credentials:

- user authenticates with tenant system
- platform exchanges for short-lived OBO token
- token scoped to specific provider action
- token stored ephemerally only for active workflow

### 11.3 Data Residency

Host the following in India:

- PostgreSQL
- vector storage
- object storage
- logs containing sensitive financial data
- backups and disaster recovery replicas

### 11.4 PII and Financial Data Handling

- Encrypt at rest and in transit
- Redact sensitive values in logs
- Store provider secrets separately from application config
- Use row-level tenant isolation or physically separate databases for high-sensitivity tenants

### 11.5 Audit Trail Requirements

Every payment-related event must record:

- actor identity
- tenant ID
- workflow run ID
- `x-request-id`
- source document references
- policy version
- model version if used
- tool invocation details
- provider response code
- final decision

## 12. Reliability Requirements

### 12.1 Failure Handling

The system must gracefully recover from:

- OpenAI timeout
- provider timeout
- partial payment submission
- webhook delay
- ERP sync failure
- duplicate callback delivery
- worker restart

### 12.2 Reliability Controls

- LangGraph durable checkpoints
- idempotent external tool wrappers
- retry with backoff for safe operations only
- circuit breakers around external providers
- dead-letter queue for unrecoverable async events
- periodic reconciliation job against provider settlement status

### 12.3 Exactly-Once Payment Intent Semantics

True exactly-once execution across third-party financial systems is rarely guaranteed, so the design should implement effectively-once semantics:

- one internal payment intent per workflow
- one external idempotency key per provider call
- provider callback correlation
- reconciliation job to detect ambiguous states

## 13. Frontend MVP Scope

The dashboard should stay intentionally small and operationally focused.

### 13.1 Screens

1. Login / tenant switch
2. Payment rules
3. Pending reviews
4. Transactions list
5. Transaction detail with evidence and audit trail
6. Settings / provider connections

### 13.2 Required UX Elements

- Rule builder with plain English plus structured constraints
- Amount threshold controls
- Review queue with approve / reject / request-info actions
- Search by vendor, biller, amount, status, date, request ID
- Clear timeline of workflow execution

## 14. Suggested Repository Structure

```text
afra/
  apps/
    api/
    worker/
    dashboard/
  services/
    policy/
    retrieval/
    payments/
    ledger_sync/
    audit/
  libs/
    langgraph_flows/
    provider_clients/
    auth/
    schemas/
    observability/
    db/
  infra/
    docker/
    k8s/
    terraform/
  docs/
    architecture/
    api/
    runbooks/
```

## 15. Suggested Build Phases

### Phase 1: Foundation

- Set up repo, CI/CD, Docker, base environments
- Implement auth, tenant model, PostgreSQL, Redis
- Add OpenTelemetry and audit event framework

### Phase 2: Deterministic Workflow

- Implement LangGraph state machine
- Add checkpoint persistence
- Define schemas for policy, bill fetch, payment intent, audit events

### Phase 3: Retrieval

- Implement ingestion for invoices, emails, payment logs
- Create embedding and keyword indexing pipelines
- Build hybrid retrieval endpoint

### Phase 4: Payment Rails

- Integrate Setu / BBPS fetch and payment execution
- Add idempotency, retries, and provider webhook handling

### Phase 5: HITL and Dashboard

- Build policy management UI
- Build review queue
- Build transaction detail and audit views

### Phase 6: Hardening

- Load testing
- chaos / failure injection
- security review
- compliance evidence pack

## 16. MVP Acceptance Criteria

The MVP should be considered acceptable when all of the following are true:

- A tenant can define autopay rules for at least one supported bill category
- The system can fetch live bill data from the payment rail
- The system can validate bill data against policy and historical evidence
- The system routes anomalies to a human review queue
- Approved in-policy bills can be paid without duplicate charge risk
- All workflow transitions are recoverable after worker restart
- Every run is traceable via `x-request-id`
- Every payment outcome is written to audit storage and synced to the ledger adapter

## 17. Key Risks and Mitigations

### Risk 1: Payment API ambiguity

Mitigation:
- build provider adapter abstraction
- persist raw provider payloads
- run periodic reconciliation jobs

### Risk 2: Model hallucination in financial decisions

Mitigation:
- use LLM for extraction and explanation only
- keep policy enforcement deterministic

### Risk 3: Duplicate payments under retries

Mitigation:
- strict idempotency keys
- payment intent state machine
- ambiguous-state reconciliation

### Risk 4: Compliance drift

Mitigation:
- enforce India-local deployment policy
- log policy version and access capability checks
- maintain data flow inventory

### Risk 5: Legacy portal fallback instability

Mitigation:
- restrict visual automation to isolated fallback adapters
- require explicit enablement per vendor
- never mix API and browser automation in the same payment path without a clear control boundary

## 18. Strong Recommendation on MVP Boundary

Do not attempt full "financial reconciliation" and "autonomous bill pay" together in the first release. For the MVP, optimize for one narrow workflow:

- recurring utility and biller payments through structured APIs

Defer these until later:

- generalized invoice reconciliation
- vendor email negotiation
- multi-bank treasury optimization
- broad legacy web portal automation

This gives the team the best chance of shipping a safe, reliable, high-ROI first version.

## 19. Recommended Next Build Step

The next practical step is to scaffold the repository around this blueprint:

- FastAPI backend
- LangGraph workflow package
- PostgreSQL schema
- dashboard shell
- Docker Compose for local development

Once that exists, the first implementation milestone should be a fully simulated end-to-end flow with mocked Setu / BBPS responses before integrating real payment rails.
