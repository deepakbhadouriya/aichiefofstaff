# Local Development Runbook

## Goals

Use this setup to iterate on the API, workflow logic, and dashboard without touching live payment infrastructure.

## Standard Flow

1. Create `.env` from `.env.example`.
2. Start local dependencies with `docker compose up --build`.
3. Apply `migrations/0001_initial_schema.sql` to PostgreSQL.
4. Open `http://localhost:8000/docs` for API testing.
5. Open `http://localhost:3000` for the dashboard shell.

## Notes

- The current provider adapter is mocked and does not submit real payments.
- The current workflow stores example data in memory for fast iteration.
- Real Setu / BBPS integration should be introduced behind the existing provider client boundary.

