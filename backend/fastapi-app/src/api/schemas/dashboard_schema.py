from pydantic import BaseModel

class DashboardSummaryResponse(BaseModel):
    organizer_name: str
    active_chits: int
    total_members: int
    collections_due_today: int
    collections_received_today: int
    pending_amount: float
    auctions_today: int
