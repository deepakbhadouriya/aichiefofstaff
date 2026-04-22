# Architecture Overview

This scaffold follows the MVP blueprint:

- FastAPI handles the operator and integration-facing API
- `libs/langgraph_flows` holds deterministic workflow state transitions
- `services/payments` wraps payment-provider interaction
- `services/retrieval` supplies hybrid-search evidence
- `services/policy` owns payment rule evaluation inputs
- `services/audit` exposes review and workflow drill-down placeholders

The current code uses in-memory fixtures to keep the repo runnable before database migrations and provider contracts are introduced.

