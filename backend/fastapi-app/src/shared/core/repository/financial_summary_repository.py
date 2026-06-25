from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date
from decimal import Decimal

class FinancialSummaryRepository:
    def __init__(self, db_object):
        self.db_object = db_object

    async def get_dashboard_overview(
        self, 
        tenant_id: UUID, 
        date_from: date, 
        date_to: date,
        chit_group_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        
        # Base where clauses for specific chit group vs all
        cg_where = "organizer_id = $1"
        args_base = [tenant_id]
        
        if chit_group_id:
            cg_where += " AND chit_group_id = $2"
            args_base.append(chit_group_id)

        # 1. Collections & Pending
        stmt_dues = f"""
            SELECT 
                COALESCE(SUM(m.net_payable_amount), 0) as total_expected,
                COALESCE(SUM(m.total_paid_amount), 0) as total_collected,
                COALESCE(SUM(m.remaining_amount), 0) as total_pending
            FROM monthly_member_dues m
            WHERE m.{cg_where}
              AND m.due_date >= $3
              AND m.due_date <= $4
              AND m.payment_status != 'WAIVED'
        """
        args_dues = args_base + [date_from, date_to]
        if not chit_group_id:
            stmt_dues = stmt_dues.replace("m.chit_group_id = $2", "1=1") # hacky way to clean if chit_group_id not used

        dues_row = await self.db_object.fetchrow(stmt_dues, *args_dues)

        # 2. Overdue amount
        stmt_overdue = f"""
            SELECT COALESCE(SUM(remaining_amount), 0) as total_overdue
            FROM monthly_member_dues
            WHERE {cg_where}
              AND payment_status IN ('PENDING', 'PARTIALLY_PAID')
              AND (grace_period_end_date < CURRENT_DATE OR (grace_period_end_date IS NULL AND due_date < CURRENT_DATE))
        """
        overdue_row = await self.db_object.fetchrow(stmt_overdue, *args_base)

        # 3. Payouts (Paid and Pending)
        stmt_payouts = f"""
            SELECT 
                COALESCE(SUM(CASE WHEN status IN ('PAID', 'WINNER_CONFIRMED') THEN payout_amount ELSE 0 END), 0) as payouts_paid,
                COALESCE(SUM(CASE WHEN status IN ('DRAFT', 'PENDING_PAYMENT') THEN payout_amount ELSE 0 END), 0) as payouts_pending
            FROM chit_winner_payouts
            WHERE {cg_where}
              AND payout_date >= $3
              AND payout_date <= $4
        """
        payouts_row = await self.db_object.fetchrow(stmt_payouts, *args_dues)

        # 4. Organizer Commission & Maintenance
        stmt_commission = f"""
            SELECT 
                COALESCE(SUM(organizer_contribution_amount), 0) as commission,
                COALESCE(SUM(maintenance_charge_amount), 0) as maintenance,
                COALESCE(SUM(dividend_pool_amount), 0) as dividends
            FROM chit_month_financial_closures
            WHERE {cg_where}
        """
        comm_row = await self.db_object.fetchrow(stmt_commission, *args_base)

        return {
            'total_expected': Decimal(str(dues_row['total_expected'])),
            'total_collected': Decimal(str(dues_row['total_collected'])),
            'total_pending': Decimal(str(dues_row['total_pending'])),
            'total_overdue': Decimal(str(overdue_row['total_overdue'])),
            'payouts_paid': Decimal(str(payouts_row['payouts_paid'])),
            'payouts_pending': Decimal(str(payouts_row['payouts_pending'])),
            'commission': Decimal(str(comm_row['commission'])),
            'maintenance': Decimal(str(comm_row['maintenance'])),
            'dividends': Decimal(str(comm_row['dividends']))
        }

    async def get_chit_group_health(
        self,
        tenant_id: UUID
    ) -> List[Dict[str, Any]]:
        stmt = """
            SELECT 
                cg.id, cg.chit_name, cg.chit_code,
                COALESCE(SUM(m.net_payable_amount), 0) as expected,
                COALESCE(SUM(m.total_paid_amount), 0) as collected
            FROM chit_groups cg
            LEFT JOIN monthly_member_dues m ON m.chit_group_id = cg.id
            WHERE cg.organizer_id = $1 AND cg.status != 'CLOSED'
            GROUP BY cg.id, cg.chit_name, cg.chit_code
        """
        rows = await self.db_object.fetch(stmt, tenant_id)
        return [dict(r) for r in rows]
