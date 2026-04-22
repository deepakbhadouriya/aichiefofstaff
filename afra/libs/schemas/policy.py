from pydantic import BaseModel, Field


class PaymentPolicyCreate(BaseModel):
    category: str = Field(examples=["electricity"])
    vendor_name: str = Field(examples=["Tata Power"])
    max_amount_minor: int = Field(ge=1, examples=[1000000])
    currency: str = Field(default="INR")
    requires_hitl_above_minor: int = Field(ge=1, examples=[500000])


class PaymentPolicyView(PaymentPolicyCreate):
    id: str
    tenant_id: str
    status: str = "active"

