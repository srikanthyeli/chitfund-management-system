from uuid import UUID
from fastapi import HTTPException
from src.api.models.models import User
from src.shared.core.repository.chit_month_financial_closure_repository import ChitMonthFinancialClosureRepository
from src.shared.core.repository.chit_winner_payout_repository import ChitWinnerPayoutRepository
from src.shared.core.repository.chit_group_activity_log_repository import ChitGroupActivityLogRepository
from src.shared.core.properties.constants import PayoutStatus, ClosureStatus, ActivityAction

class ChitFinancialClosureService:
    def __init__(self, db_object):
        self.db = db_object

    async def close_month(self, current_user: User, chit_group_id: UUID, month_number: int, remarks: str) -> dict:
        organizer_id = current_user.organizer_id
        async with self.db.transaction():
            closure_repo = ChitMonthFinancialClosureRepository(self.db)
            
            closure = await closure_repo.get_closure_by_group_and_month(chit_group_id, month_number, organizer_id)
            if not closure:
                raise HTTPException(status_code=404, detail="Financial closure record not found")
            
            if closure["closure_status"] == ClosureStatus.CLOSED.value:
                raise HTTPException(status_code=400, detail="Month is already closed")
                
            if closure["closure_status"] != "READY_FOR_CLOSURE":
                raise HTTPException(status_code=400, detail="Month is not ready for closure. Ensure payout is completed.")

            payout_repo = ChitWinnerPayoutRepository(self.db)
            payout = await payout_repo.get_active_payout_by_group_and_month(chit_group_id, month_number, organizer_id)
            if not payout or payout["status"] not in [PayoutStatus.PAID.value, PayoutStatus.WINNER_CONFIRMED.value, PayoutStatus.COMPLETED.value]:
                raise HTTPException(status_code=400, detail="Winner payout must be paid or confirmed before closing the month")

            updated_closure = await closure_repo.close_month(closure["id"], organizer_id, current_user.id, remarks)

            activity_repo = ChitGroupActivityLogRepository(self.db)
            await activity_repo.create_log(
                organizer_id=organizer_id,
                chit_group_id=chit_group_id,
                action_type=ActivityAction.MONTH_CLOSED.value,
                new_values={"month_number": month_number, "remarks": remarks},
                remarks=f"Month {month_number} financially closed",
                performed_by_user_id=current_user.id
            )

            return updated_closure

    async def get_financial_summary(self, current_user: User, chit_group_id: UUID) -> dict:
        organizer_id = current_user.organizer_id
        closure_repo = ChitMonthFinancialClosureRepository(self.db)
        
        summary = await closure_repo.get_financial_summary(chit_group_id, organizer_id)
        monthly_summaries = await closure_repo.get_monthly_summaries(chit_group_id, organizer_id)

        return {
            "chit_group_id": str(chit_group_id),
            "total_expected_collection": summary["total_expected_collection"],
            "total_actual_collection": summary["total_actual_collection"],
            "total_pending_collection": summary["total_pending_collection"],
            "total_winner_payouts": summary["total_winner_payouts"],
            "total_maintenance_collected": summary["total_maintenance_collected"],
            "total_organizer_contribution": summary["total_organizer_contribution"],
            "total_shortfall": summary["total_shortfall"],
            "completed_months": summary["completed_months"],
            "monthly_summaries": monthly_summaries
        }
