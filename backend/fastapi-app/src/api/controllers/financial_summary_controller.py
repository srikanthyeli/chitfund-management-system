from fastapi import Depends, HTTPException
from uuid import UUID
from datetime import date
from typing import Optional

from src.shared.core.services.financial_summary_service import FinancialSummaryService
from src.shared.core.repository.financial_summary_repository import FinancialSummaryRepository
from src.api.schemas.financial_summary_schemas import FinancialSummaryResponse
from src.shared.core.database import get_db_session

class FinancialSummaryController:
    @staticmethod
    async def get_dashboard_overview(
        tenant_id: UUID,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        chit_group_id: Optional[UUID] = None,
        db = Depends(get_db_session)
    ) -> FinancialSummaryResponse:
        repo = FinancialSummaryRepository(db)
        service = FinancialSummaryService(repo)
        
        result = await service.get_dashboard_summary(
            tenant_id=tenant_id,
            date_from=date_from,
            date_to=date_to,
            chit_group_id=chit_group_id
        )
        
        return FinancialSummaryResponse(**result)
