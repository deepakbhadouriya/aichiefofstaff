from datetime import datetime

from pydantic import BaseModel


class PaymentRecord(BaseModel):
    id: str
    tenant_id: str
    vendor_name: str
    amount_minor: int
    currency: str
    status: str
    provider: str
    created_at: datetime

