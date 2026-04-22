from fastapi import FastAPI

from apps.api.app.routes import demo, health, integrations, policies, profiles, reviews, transactions, workflows
from libs.db.settings import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Autonomous Financial Reconciliation Agent MVP API",
)

app.include_router(health.router)
app.include_router(demo.router, prefix="/api/v1")
app.include_router(profiles.router, prefix="/api/v1")
app.include_router(integrations.router, prefix="/api/v1")
app.include_router(policies.router, prefix="/api/v1")
app.include_router(reviews.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")
app.include_router(workflows.router, prefix="/api/v1")
