from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.app.routes import (
    crm,
    demo,
    health,
    integrations,
    onboarding,
    policies,
    profiles,
    reviews,
    transactions,
    workflows,
)
from libs.db.settings import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Autonomous Financial Reconciliation Agent MVP API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3100",
        "http://localhost:3100",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(onboarding.router, prefix="/api/v1")
app.include_router(crm.router, prefix="/api/v1")
app.include_router(demo.router, prefix="/api/v1")
app.include_router(profiles.router, prefix="/api/v1")
app.include_router(integrations.router, prefix="/api/v1")
app.include_router(policies.router, prefix="/api/v1")
app.include_router(reviews.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")
app.include_router(workflows.router, prefix="/api/v1")
