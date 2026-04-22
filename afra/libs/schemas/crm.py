from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ContactView(BaseModel):
    id: str
    name: str
    email: str
    role: str
    company: str
    priority: str  # High, Mid, Low
    last_interaction_at: datetime
    status: str  # Active, Cooling, Stale
    summary: str

class InteractionView(BaseModel):
    id: str
    contact_id: str
    type: str  # Email, SMS, Meeting
    timestamp: datetime
    summary: str
    sentiment: str

class CRMSnapshot(BaseModel):
    contacts: list[ContactView]
    recent_interactions: list[InteractionView]
    nudges: list[str]
