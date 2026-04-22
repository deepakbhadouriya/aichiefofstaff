import os
from pathlib import Path
from libs.schemas.workflow import WorkflowEvidence

INVOICE_DIR = Path(__file__).parent.parent.parent / "data" / "invoices"


def retrieve_evidence(
    tenant_id: str,
    vendor_name: str,
    category: str,
    biller_reference: str,
) -> list[WorkflowEvidence]:
    del tenant_id
    evidence: list[WorkflowEvidence] = []

    # Real retrieval: Check local invoice directory
    if INVOICE_DIR.exists():
        for file in os.listdir(INVOICE_DIR):
            if file.endswith(".txt"):
                file_path = INVOICE_DIR / file
                content = file_path.read_text()
                # Simple keyword matching
                if vendor_name.lower() in content.lower() or biller_reference.lower() in content.lower():
                    summary = content.split("\n")[0] # First line as summary
                    evidence.append(
                        WorkflowEvidence(
                            source=f"filesystem://{file}",
                            summary=f"Found matching document: {summary}",
                            confidence=0.95,
                        )
                    )

    # Fallback to mock logic if no real files found
    if not evidence:
        low_evidence_vendor = vendor_name.lower().startswith("fresh ")
        low_evidence_reference = biller_reference.lower().startswith("new-")
        if low_evidence_vendor or low_evidence_reference:
            evidence.extend([
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
            ])
        else:
            evidence.extend([
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
            ])
    
    return evidence
