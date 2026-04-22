from datetime import timedelta
from libs.schemas.crm import ContactView, InteractionView, CRMSnapshot
from libs.time import utc_now

def get_crm_snapshot(profile_id: str) -> CRMSnapshot:
    now = utc_now()
    
    # Seeded contacts for the executive
    contacts = [
        ContactView(
            id="c1",
            name="Vikram Singh",
            email="vikram@tata-power.com",
            role="Account Manager",
            company="Tata Power",
            priority="High",
            last_interaction_at=now - timedelta(days=2),
            status="Active",
            summary="Managing industrial power tariff negotiation."
        ),
        ContactView(
            id="c2",
            name="Sarah Johnson",
            email="sarah@global-bank.com",
            role="Relationship Manager",
            company="Global Bank",
            priority="High",
            last_interaction_at=now - timedelta(days=20),
            status="Stale",
            summary="Reviewing credit line expansion for Q3."
        ),
        ContactView(
            id="c3",
            name="Amit Patel",
            email="amit@airtel.com",
            role="B2B Lead",
            company="Airtel Business",
            priority="Mid",
            last_interaction_at=now - timedelta(days=5),
            status="Cooling",
            summary="Discussing fiber-optic upgrade for the main office."
        )
    ]
    
    interactions = [
        InteractionView(
            id="i1",
            contact_id="c1",
            type="Email",
            timestamp=now - timedelta(days=2),
            summary="Sent updated consumption forecast for April.",
            sentiment="Positive"
        ),
        InteractionView(
            id="i2",
            contact_id="c3",
            type="Meeting",
            timestamp=now - timedelta(days=5),
            summary="Initial discussion on bandwidth requirements.",
            sentiment="Neutral"
        )
    ]
    
    nudges = [
        "You haven't spoken to Sarah (Global Bank) in 20 days. Her credit line review is due next week.",
        "Airtel upgrade proposal is waiting for your signature since Tuesday."
    ]
    
    return CRMSnapshot(
        contacts=contacts,
        recent_interactions=interactions,
        nudges=nudges
    )
