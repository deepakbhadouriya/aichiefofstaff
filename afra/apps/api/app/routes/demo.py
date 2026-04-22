from fastapi import APIRouter, Depends

from apps.api.app.dependencies import get_request_context
from libs.schemas.demo import DemoScenario, DemoSeedResult
from services.demo.service import demo_scenarios, seed_demo_data

router = APIRouter(tags=["demo"])


@router.get("/demo/scenarios", response_model=list[DemoScenario])
def get_demo_scenarios() -> list[DemoScenario]:
    return demo_scenarios()


@router.post("/demo/seed", response_model=DemoSeedResult)
def post_demo_seed(context: dict[str, str] = Depends(get_request_context)) -> DemoSeedResult:
    return seed_demo_data(context["tenant_id"], context["profile_id"])

