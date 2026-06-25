import asyncpg
from fastapi import APIRouter, Depends
from src.api.schemas.dashboard_schema import DashboardSummaryResponse
from src.shared.core.services.dashboard_service import DashboardService
from src.shared.core.database import get_db_session
from src.api.dependencies.auth_dependency import get_current_organizer
from src.api.models.models import User

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    organizer: User = Depends(get_current_organizer),
    db: asyncpg.Connection = Depends(get_db_session)
):
    service = DashboardService(db)
    return await service.get_summary(organizer)
