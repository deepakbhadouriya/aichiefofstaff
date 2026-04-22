from fastapi import APIRouter, Header
from typing import Optional
from libs.schemas.crm import CRMSnapshot
from services.crm.service import get_crm_snapshot

router = APIRouter(tags=["crm"])

@router.get("/crm/snapshot", response_model=CRMSnapshot)
def get_snapshot(x_profile_id: Optional[str] = Header(None)) -> CRMSnapshot:
    return get_crm_snapshot(x_profile_id or "demo_user")
