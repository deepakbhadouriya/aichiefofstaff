# A-FRA MVP Scaffold

This repository scaffolds the MVP for the Autonomous Financial Reconciliation Agent (A-FRA), focused on deterministic autonomous bill payment for SMEs in India.

## Stack

- Backend API: FastAPI
- Workflow orchestration: LangGraph-inspired state graph scaffold
- Database: PostgreSQL
- Cache / coordination: Redis
- Frontend: Next.js App Router
- Deployment: Docker Compose for local development

## Repository Standards

- License: MIT
- Contribution guide: `CONTRIBUTING.md`
- CI: GitHub Actions workflow under `.github/workflows/ci.yml`
- Database bootstrap: SQL migration files under `migrations/`

## Repository Layout

```text
afra/
  apps/
    api/         FastAPI application
    worker/      Workflow runner entrypoint
    dashboard/   Minimal operations dashboard
  libs/
    auth/        Capability and token scaffolding
    db/          Settings and DB connection helpers
    langgraph_flows/
    observability/
    provider_clients/
    schemas/
  infra/
    docker/
    k8s/
```

## Quick Start

1. Copy `.env.example` to `.env`.
2. Run `docker compose up --build`.
3. Open the API docs at `http://localhost:8000/docs`.
4. Open the dashboard at `http://localhost:3000`.

## Current Scope

This is a starter scaffold, not a complete payment product. It includes:

- tenant-aware API skeleton
- deterministic workflow state model
- mocked bill fetch and payment validation path
- local Docker development setup
- dashboard shell for policies, reviews, and transactions

## Next Steps

- add real LangGraph dependency and checkpoint store
- implement PostgreSQL migrations
- integrate Setu / BBPS adapter
- add ERP sync adapter
- wire authentication and OBO token exchange
- implement full audit persistence
