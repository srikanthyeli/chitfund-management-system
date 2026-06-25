from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, select, and_, or_, desc

from src.api.models.models import (
    ChitGroup, MonthlyMemberDue, ChitPaymentReceipt, 
    ChitWinnerPayout, ChitMonthFinancialClosure, Member
)

class ReportsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_collections_report(
        self,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 20,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ):
        stmt = (
            select(
                ChitPaymentReceipt.id.label('receipt_id'),
                ChitPaymentReceipt.payment_date,
                ChitPaymentReceipt.receipt_number,
                ChitGroup.chit_name.label('chit_group_name'),
                MonthlyMemberDue.month_number,
                Member.full_name.label('member_name'),
                MonthlyMemberDue.share_count.label('number_of_shares'),
                MonthlyMemberDue.net_payable_amount.label('expected_amount'),
                ChitPaymentReceipt.payment_amount.label('paid_amount'),
                MonthlyMemberDue.remaining_amount.label('pending_amount'),
                ChitPaymentReceipt.payment_method.label('payment_mode'),
                ChitPaymentReceipt.transaction_reference,
                ChitPaymentReceipt.status
            )
            .join(MonthlyMemberDue, MonthlyMemberDue.id == ChitPaymentReceipt.monthly_member_due_id)
            .join(ChitGroup, ChitGroup.id == ChitPaymentReceipt.chit_group_id)
            .join(Member, Member.id == ChitPaymentReceipt.member_id)
            .where(ChitPaymentReceipt.organizer_id == tenant_id)
        )
        
        if date_from:
            stmt = stmt.where(ChitPaymentReceipt.payment_date >= date_from)
        if date_to:
            stmt = stmt.where(ChitPaymentReceipt.payment_date <= date_to)

        total = self.db.scalar(select(func.count()).select_from(stmt.subquery()))
        items = self.db.execute(stmt.order_by(desc(ChitPaymentReceipt.payment_date)).offset(skip).limit(limit)).all()
        
        return items, total

    # Add other report functions (payouts, overdues, etc.) similarly...
