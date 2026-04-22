# Demo Testing Runbook

## Goal

Use the `demo_user` profile to walk through seeded happy-path and negative-path flows in the app before real SME connectors are turned on.

## Seeded SME-Oriented Connectors

- Payments: Setu BBPS
- ERP / Ledger: TallyPrime or Zoho Books
- Email ingestion: Google Workspace Gmail or Microsoft 365

## Demo Personas

- `demo_user`
  Uses seeded workflows, sample vendor evidence, and review queue scenarios.
- `actual_user`
  Uses live-ready connector naming and status while remaining safe to demo before real credentials are provisioned.

## Seed Demo Data

Use the API docs or any REST client with these headers:

- `X-Tenant-ID: demo-tenant`
- `X-Profile-ID: demo_user`
- `X-Request-ID: req-demo-seed`

Call:

- `POST /api/v1/demo/seed`

This seeds:

- 2 happy scenarios
- 2 negative scenarios
- policies for electricity, broadband, and new vendor services

## Happy Scenarios To Show

1. `Tata Power utility autopay`
   Result: auto-approved, paid, audited, ledger synced
2. `Airtel Business broadband renewal`
   Result: auto-approved under broadband threshold

## Negative Scenarios To Show

1. `High amount electricity bill`
   Result: appears in review queue because it exceeds threshold
2. `Fresh Pest Control new vendor`
   Result: low evidence triggers review and is seeded to be rejected during the demo

## How To Verify In The App

1. Open `POST /api/v1/demo/seed` in `/docs` and execute it with `demo_user`.
2. Open `GET /api/v1/payments`.
   You should see successful seeded payments for the happy-path scenarios.
3. Open `GET /api/v1/reviews`.
   You should see the threshold-breach scenario waiting for human review.
4. Open `GET /api/v1/workflows/{workflow_id}` for a seeded scenario.
   Verify `x_request_id`, decision, evidence, payment intent, payment ID, and ledger sync ID.
5. Use `POST /api/v1/reviews/{workflowRunId}/approve`.
   This completes the review-gated flow and creates the payment and ledger sync outcome.
6. Switch the header to `X-Profile-ID: actual_user`.
   Check `GET /api/v1/integrations/realtime` and verify live-ready connector names and statuses.

## Suggested Demo Script

- Start with `demo_user` and seed the data.
- Show the green path first with Tata Power.
- Show the review queue next with the high amount bill.
- Show the unknown vendor case to explain anomaly handling.
- End on `actual_user` to explain how Setu BBPS, TallyPrime or Zoho Books, and Gmail or Microsoft 365 will switch to live credentials later.

