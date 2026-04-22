# Contributing

Thanks for contributing to A-FRA.

## Working Agreement

- Keep payment-critical paths deterministic.
- Treat auditability, idempotency, and data residency as product requirements, not polish.
- Avoid letting LLM output directly trigger financial actions without deterministic validation.
- Prefer small, reviewable pull requests.

## Local Setup

1. Copy `.env.example` to `.env`.
2. Start local services with `docker compose up --build`.
3. Run the API locally with `uvicorn apps.api.app.main:app --reload`.
4. Run the worker with `python -m apps.worker.main`.
5. Run the dashboard from `apps/dashboard` with `npm install` and `npm run dev`.

## Pull Requests

- Describe the user or operator impact clearly.
- Include any workflow-state or schema changes in the PR description.
- Add or update tests for behavior changes when practical.
- Call out compliance-sensitive changes explicitly.

## Commit Guidance

- Use focused commit messages.
- Keep infrastructure, product logic, and UI changes separated when possible.
- Never commit secrets, live credentials, or production tenant data.

## Design Expectations

- New payment rails must be wrapped behind provider adapters.
- Any change affecting approval logic should preserve replayability and audit trails.
- Database changes should ship with a new migration file under `migrations/`.

