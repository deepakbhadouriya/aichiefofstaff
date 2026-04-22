from libs.schemas.workflow import WorkflowEvidence


def retrieve_evidence(
    tenant_id: str,
    vendor_name: str,
    category: str,
    biller_reference: str,
) -> list[WorkflowEvidence]:
    del tenant_id
    low_evidence_vendor = vendor_name.lower().startswith("fresh ")
    low_evidence_reference = biller_reference.lower().startswith("new-")
    if low_evidence_vendor or low_evidence_reference:
        return [
            WorkflowEvidence(
                source="vendor_master",
                summary=f"Only weak metadata was found for {vendor_name}; no strong historical match exists yet.",
                confidence=0.42,
            ),
            WorkflowEvidence(
                source="email_lookup",
                summary=f"Recent inbound reference {biller_reference} appears new and is awaiting vendor onboarding checks.",
                confidence=0.38,
            ),
        ]
    return [
        WorkflowEvidence(
            source="historical_payment_log",
            summary=f"Previous {category} payments found for {vendor_name} with matching account reference.",
            confidence=0.92,
        ),
        WorkflowEvidence(
            source="vendor_master",
            summary=f"Biller reference {biller_reference} matched approved vendor metadata.",
            confidence=0.89,
        ),
    ]
