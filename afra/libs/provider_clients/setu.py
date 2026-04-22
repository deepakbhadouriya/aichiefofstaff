from dataclasses import dataclass


@dataclass
class SetuBill:
    vendor_name: str
    biller_reference: str
    amount_minor: int
    currency: str = "INR"
    status: str = "outstanding"


class SetuClient:
    """Mock provider client until BBPS credentials and contracts are available."""

    def fetch_bill(
        self,
        vendor_name: str,
        biller_reference: str,
        amount_minor_hint: int | None = None,
    ) -> SetuBill:
        return SetuBill(
            vendor_name=vendor_name,
            biller_reference=biller_reference,
            amount_minor=amount_minor_hint or 420000,
        )

