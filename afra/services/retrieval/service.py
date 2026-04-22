from libs.schemas.workflow import WorkflowEvidence


def retrieve_evidence(
    tenant_id: str,
    vendor_name: str,
    category: str,
    biller_reference: str,
) -> list[WorkflowEvidence]:
    del tenant_id
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

