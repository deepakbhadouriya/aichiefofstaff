from libs.schemas.policy import PaymentPolicyCreate, PaymentPolicyView

_POLICIES: dict[str, list[PaymentPolicyView]] = {
    "demo-tenant": [
        PaymentPolicyView(
            id="pol-electricity-001",
            tenant_id="demo-tenant",
            category="electricity",
            vendor_name="Tata Power",
            max_amount_minor=1000000,
            currency="INR",
            requires_hitl_above_minor=500000,
            status="active",
        )
    ]
}


def list_policies(tenant_id: str) -> list[PaymentPolicyView]:
    return _POLICIES.get(tenant_id, [])


def upsert_policy(tenant_id: str, payload: PaymentPolicyCreate) -> PaymentPolicyView:
    policy = PaymentPolicyView(
        id=f"pol-{payload.vendor_name.lower().replace(' ', '-')}",
        tenant_id=tenant_id,
        **payload.model_dump(),
    )
    bucket = _POLICIES.setdefault(tenant_id, [])
    bucket.append(policy)
    return policy


def choose_policy_for_vendor(tenant_id: str, vendor_name: str) -> PaymentPolicyView:
    policies = list_policies(tenant_id)
    for policy in policies:
        if policy.vendor_name.lower() == vendor_name.lower():
            return policy
    return PaymentPolicyView(
        id="pol-default",
        tenant_id=tenant_id,
        category="generic",
        vendor_name=vendor_name,
        max_amount_minor=250000,
        currency="INR",
        requires_hitl_above_minor=100000,
        status="draft",
    )

