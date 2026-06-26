from fastapi import APIRouter, Depends, Query

from uuid import UUID
from datetime import date
from typing import Optional

from src.api.controllers.financial_summary_controller import FinancialSummaryController
from src.api.dependencies.auth_decorator import authorize
from src.api.schemas.financial_summary_schemas import FinancialSummaryResponse
from src.shared.core.database import get_db_session

router = APIRouter(prefix="/api/v1/organizer/financial-summary", tags=["Financial Summary"])

@router.get("/overview", response_model=FinancialSummaryResponse)
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def get_dashboard_overview(
    request,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    chit_group_id: Optional[UUID] = None,
    db = Depends(get_db_session)
):
    tenant_id = request.state.user.organizer_id
    if request.state.user.role == "ADMIN" and request.query_params.get("organizer_id"):
        tenant_id = UUID(request.query_params.get("organizer_id"))
        
    return await FinancialSummaryController.get_dashboard_overview(
        tenant_id=tenant_id,
        date_from=date_from,
        date_to=date_to,
        chit_group_id=chit_group_id,
        db=db
    )
