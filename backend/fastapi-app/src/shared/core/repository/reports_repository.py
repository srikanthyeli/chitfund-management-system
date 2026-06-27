from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal

class ReportsRepository:
    def __init__(self, db_object):
        self.db_object = db_object

    async def get_dashboard_metrics(self, tenant_id: UUID) -> Dict[str, Any]:
        metrics = {}
        
        # 1. Chit Groups
        q_groups = """
            SELECT 
                COUNT(*) as total_chit_groups,
                SUM(CASE WHEN status IN ('OPEN', 'ACTIVE') THEN 1 ELSE 0 END) as active_chit_groups,
                SUM(CASE WHEN status = 'CLOSED' THEN 1 ELSE 0 END) as completed_chit_groups,
                COALESCE(SUM(total_shares), 0) as total_shares,
                COALESCE(SUM(allocated_shares), 0) as allocated_shares,
                COALESCE(SUM(available_shares), 0) as available_shares
            FROM chit_groups
            WHERE organizer_id = $1 AND is_deleted = FALSE
        """
        row_groups = await self.db_object.fetchrow(q_groups, tenant_id)
        metrics.update(dict(row_groups))
        
        # 2. Members
        q_members = """
            SELECT 
                COUNT(*) as total_members,
                SUM(CASE WHEN is_active = TRUE THEN 1 ELSE 0 END) as active_members
            FROM members
            WHERE organizer_id = $1 AND is_deleted = FALSE
        """
        row_members = await self.db_object.fetchrow(q_members, tenant_id)
        metrics.update(dict(row_members))
        metrics['replacement_members'] = 0 # Not tracked directly yet
        
        # 3. Collections
        q_colls = """
            SELECT
                COALESCE(SUM(payment_amount), 0) as total_collections,
                COALESCE(SUM(CASE WHEN DATE(payment_date) = CURRENT_DATE THEN payment_amount ELSE 0 END), 0) as todays_collections,
                COALESCE(SUM(CASE WHEN date_trunc('month', payment_date) = date_trunc('month', CURRENT_DATE) THEN payment_amount ELSE 0 END), 0) as current_month_collections
            FROM chit_payment_receipts
            WHERE organizer_id = $1 AND status = 'SUCCESS'
        """
        row_colls = await self.db_object.fetchrow(q_colls, tenant_id)
        metrics.update(dict(row_colls))

        # 4. Pending & Overdue
        q_pending = """
            SELECT 
                COALESCE(SUM(remaining_amount), 0) as pending_collections,
                COALESCE(SUM(CASE WHEN (grace_period_end_date < CURRENT_DATE OR (grace_period_end_date IS NULL AND due_date < CURRENT_DATE)) THEN remaining_amount ELSE 0 END), 0) as overdue_collections,
                COALESCE(SUM(net_payable_amount), 0) as total_expected
            FROM monthly_member_dues
            WHERE organizer_id = $1 AND payment_status IN ('PENDING', 'PARTIALLY_PAID', 'OVERDUE')
        """
        row_pending = await self.db_object.fetchrow(q_pending, tenant_id)
        metrics['pending_collections'] = row_pending['pending_collections']
        metrics['overdue_collections'] = row_pending['overdue_collections']
        
        expected = row_pending['total_expected'] + metrics['total_collections']
        metrics['collection_percentage'] = float(metrics['total_collections'] / expected * 100) if expected > 0 else 0.0

        # 5. Payouts and Organizer
        q_payouts = """
            SELECT 
                COALESCE(SUM(gross_chit_amount), 0) as total_auction_amount,
                COALESCE(SUM(payout_amount), 0) as total_winner_payouts
            FROM chit_winner_payouts
            WHERE organizer_id = $1 AND status IN ('PAID', 'WINNER_CONFIRMED')
        """
        row_payouts = await self.db_object.fetchrow(q_payouts, tenant_id)
        metrics.update(dict(row_payouts))

        q_org = """
            SELECT 
                COALESCE(SUM(dividend_pool_amount), 0) as total_dividends,
                COALESCE(SUM(maintenance_charge_amount), 0) as total_maintenance_charges,
                COALESCE(SUM(maintenance_charge_amount + (winning_bid_discount_amount - dividend_pool_amount)), 0) as organizer_earnings
            FROM chit_month_financial_closures
            WHERE organizer_id = $1
        """
        row_org = await self.db_object.fetchrow(q_org, tenant_id)
        metrics.update(dict(row_org))
        
        metrics['total_outstanding'] = metrics['pending_collections']
        metrics['net_cash_flow'] = metrics['total_collections'] + metrics['total_maintenance_charges'] - metrics['total_winner_payouts'] - metrics['total_dividends']

        # Chart Data
        metrics['monthly_collection_trend'] = []
        metrics['monthly_payout_trend'] = []
        metrics['payment_mode_distribution'] = []
        metrics['collection_success_percentage'] = []
        metrics['monthly_revenue'] = []

        return metrics

    async def get_collections_report(
        self, tenant_id: UUID, skip: int, limit: int,
        date_from: Optional[date], date_to: Optional[date],
        month: Optional[int], year: Optional[int],
        member_id: Optional[UUID], chit_group_id: Optional[UUID]
    ) -> Tuple[List[Dict], int]:
        
        base_where = "r.organizer_id = $1 AND r.status = 'SUCCESS'"
        params = [tenant_id]
        param_idx = 2
        
        if date_from:
            base_where += f" AND DATE(r.payment_date) >= ${param_idx}"
            params.append(date_from)
            param_idx += 1
        if date_to:
            base_where += f" AND DATE(r.payment_date) <= ${param_idx}"
            params.append(date_to)
            param_idx += 1
        if month:
            base_where += f" AND EXTRACT(MONTH FROM r.payment_date) = ${param_idx}"
            params.append(month)
            param_idx += 1
        if year:
            base_where += f" AND EXTRACT(YEAR FROM r.payment_date) = ${param_idx}"
            params.append(year)
            param_idx += 1
        if member_id:
            base_where += f" AND r.member_id = ${param_idx}"
            params.append(member_id)
            param_idx += 1
        if chit_group_id:
            base_where += f" AND r.chit_group_id = ${param_idx}"
            params.append(chit_group_id)
            param_idx += 1

        count_q = f"SELECT COUNT(*) FROM chit_payment_receipts r WHERE {base_where}"
        total = await self.db_object.fetchval(count_q, *params)
        
        if limit > 0:
            limit_clause = f"LIMIT {limit} OFFSET {skip}"
        else:
            limit_clause = ""

        q = f"""
            SELECT 
                r.id as receipt_id, r.receipt_number, m.full_name as member_name, 
                r.member_id, cg.chit_name as chit_group_name, d.share_count as shares,
                d.month_number, r.payment_amount as amount, r.payment_method as payment_mode,
                r.status, u.mobile as collected_by, r.payment_date, r.transaction_reference
            FROM chit_payment_receipts r
            JOIN members m ON m.id = r.member_id
            JOIN chit_groups cg ON cg.id = r.chit_group_id
            JOIN monthly_member_dues d ON d.id = r.monthly_member_due_id
            LEFT JOIN users u ON u.id = r.collected_by_user_id
            WHERE {base_where}
            ORDER BY r.payment_date DESC
            {limit_clause}
        """
        rows = await self.db_object.fetch(q, *params)
        return [dict(r) for r in rows], total

    async def get_pending_collections_report(self, tenant_id: UUID, skip: int, limit: int) -> Tuple[List[Dict], int]:
        base_where = "d.organizer_id = $1 AND d.payment_status IN ('PENDING', 'PARTIALLY_PAID', 'OVERDUE')"
        params = [tenant_id]

        count_q = f"SELECT COUNT(*) FROM monthly_member_dues d WHERE {base_where}"
        total = await self.db_object.fetchval(count_q, *params)

        if limit > 0:
            limit_clause = f"LIMIT {limit} OFFSET {skip}"
        else:
            limit_clause = ""

        q = f"""
            SELECT 
                d.id as due_id, m.full_name as member_name, m.mobile, d.share_count as shares,
                cg.chit_name as chit_group_name, d.month_number, d.net_payable_amount as expected_amount,
                d.total_paid_amount as paid_amount, d.remaining_amount as pending_amount,
                GREATEST(0, (CURRENT_DATE - COALESCE(d.grace_period_end_date, d.due_date))::integer) as overdue_days,
                d.grace_period_end_date as grace_period_end
            FROM monthly_member_dues d
            JOIN members m ON m.id = d.member_id
            JOIN chit_groups cg ON cg.id = d.chit_group_id
            WHERE {base_where}
            ORDER BY overdue_days DESC, d.due_date ASC
            {limit_clause}
        """
        rows = await self.db_object.fetch(q, *params)
        return [dict(r) for r in rows], total

    async def get_auction_report(self, tenant_id: UUID, skip: int, limit: int) -> Tuple[List[Dict], int]:
        base_where = "a.organizer_id = $1"
        params = [tenant_id]

        count_q = f"SELECT COUNT(*) FROM chit_auctions a WHERE {base_where}"
        total = await self.db_object.fetchval(count_q, *params)

        if limit > 0:
            limit_clause = f"LIMIT {limit} OFFSET {skip}"
        else:
            limit_clause = ""

        q = f"""
            SELECT 
                a.id as auction_id, a.auction_month_number as auction_month, cg.chit_name as chit_group_name,
                m.full_name as winner_name, a.gross_chit_amount as gross_amount, a.total_discount_amount as discount_amount,
                (a.total_discount_amount - a.maintenance_charge) / cg.total_shares as dividend_per_share,
                a.auction_date, a.status, COALESCE(wp.status, 'NO_PAYOUT') as payout_status
            FROM chit_auctions a
            JOIN chit_groups cg ON cg.id = a.chit_group_id
            LEFT JOIN members m ON m.id = a.winner_member_id
            LEFT JOIN chit_winner_payouts wp ON wp.chit_auction_id = a.id
            WHERE {base_where}
            ORDER BY a.auction_date DESC
            {limit_clause}
        """
        rows = await self.db_object.fetch(q, *params)
        return [dict(r) for r in rows], total

    async def get_winner_payout_report(self, tenant_id: UUID, skip: int, limit: int) -> Tuple[List[Dict], int]:
        base_where = "wp.organizer_id = $1"
        params = [tenant_id]

        count_q = f"SELECT COUNT(*) FROM chit_winner_payouts wp WHERE {base_where}"
        total = await self.db_object.fetchval(count_q, *params)

        if limit > 0:
            limit_clause = f"LIMIT {limit} OFFSET {skip}"
        else:
            limit_clause = ""

        q = f"""
            SELECT 
                wp.id as payout_id, m.full_name as winner_name, cg.chit_name as chit_group_name,
                wp.month_number, wp.gross_chit_amount as gross_amount,
                (wp.winning_bid_discount_amount + wp.maintenance_charge_amount) as deductions,
                wp.payout_amount as net_amount, wp.status as payment_status, wp.payment_method as payment_mode,
                wp.transaction_reference, wp.payout_receipt_number as receipt_number,
                CASE WHEN wp.winner_confirmed_at IS NOT NULL THEN 'CONFIRMED' ELSE 'PENDING' END as confirmation_status,
                wp.payout_date
            FROM chit_winner_payouts wp
            JOIN members m ON m.id = wp.winner_member_id
            JOIN chit_groups cg ON cg.id = wp.chit_group_id
            WHERE {base_where}
            ORDER BY wp.payout_date DESC
            {limit_clause}
        """
        rows = await self.db_object.fetch(q, *params)
        return [dict(r) for r in rows], total

    async def get_member_financial_report(self, tenant_id: UUID, skip: int, limit: int) -> Tuple[List[Dict], int]:
        base_where = "m.organizer_id = $1 AND m.is_deleted = FALSE"
        params = [tenant_id]

        count_q = f"SELECT COUNT(*) FROM members m WHERE {base_where}"
        total = await self.db_object.fetchval(count_q, *params)

        if limit > 0:
            limit_clause = f"LIMIT {limit} OFFSET {skip}"
        else:
            limit_clause = ""

        q = f"""
            SELECT 
                m.id as member_id, m.full_name as member_name, m.mobile,
                COALESCE((SELECT SUM(payment_amount) FROM chit_payment_receipts WHERE member_id = m.id AND status = 'SUCCESS'), 0) as total_paid,
                COALESCE((SELECT SUM(remaining_amount) FROM monthly_member_dues WHERE member_id = m.id AND payment_status IN ('PENDING', 'PARTIALLY_PAID', 'OVERDUE')), 0) as pending_amount,
                (SELECT COUNT(*) FROM monthly_member_dues WHERE member_id = m.id AND payment_status = 'OVERDUE') as late_payments_count,
                COALESCE((SELECT SUM(total_bonus_amount) FROM monthly_member_dues WHERE member_id = m.id), 0) as total_dividend_earned,
                COALESCE((SELECT SUM(payout_amount) FROM chit_winner_payouts WHERE winner_member_id = m.id AND status IN ('PAID', 'WINNER_CONFIRMED')), 0) as total_winner_amount,
                (COALESCE((SELECT SUM(payment_amount) FROM chit_payment_receipts WHERE member_id = m.id AND status = 'SUCCESS'), 0) - COALESCE((SELECT SUM(net_payable_amount) FROM monthly_member_dues WHERE member_id = m.id), 0)) as current_balance
            FROM members m
            WHERE {base_where}
            ORDER BY m.full_name ASC
            {limit_clause}
        """
        rows = await self.db_object.fetch(q, *params)
        return [dict(r) for r in rows], total

    async def get_organizer_financial_report(self, tenant_id: UUID, skip: int, limit: int) -> Tuple[List[Dict], int]:
        # Aggregate by month
        q = f"""
            WITH months AS (
                SELECT DISTINCT to_char(payment_date, 'YYYY-MM') as month_str
                FROM chit_payment_receipts WHERE organizer_id = $1
                UNION
                SELECT DISTINCT to_char(created_at, 'YYYY-MM') as month_str
                FROM chit_month_financial_closures WHERE organizer_id = $1
            )
            SELECT 
                m.month_str as month,
                COALESCE((SELECT SUM(payment_amount) FROM chit_payment_receipts WHERE organizer_id = $1 AND to_char(payment_date, 'YYYY-MM') = m.month_str AND status = 'SUCCESS'), 0) as collections_received,
                COALESCE((SELECT SUM(maintenance_charge_amount) FROM chit_month_financial_closures WHERE organizer_id = $1 AND to_char(created_at, 'YYYY-MM') = m.month_str), 0) as maintenance_income,
                COALESCE((SELECT SUM(winning_bid_discount_amount - dividend_pool_amount) FROM chit_month_financial_closures WHERE organizer_id = $1 AND to_char(created_at, 'YYYY-MM') = m.month_str), 0) as commission_income,
                COALESCE((SELECT SUM(remaining_amount) FROM monthly_member_dues WHERE organizer_id = $1 AND to_char(due_date, 'YYYY-MM') = m.month_str AND payment_status IN ('PENDING', 'OVERDUE')), 0) as total_outstanding,
                (
                  COALESCE((SELECT SUM(payment_amount) FROM chit_payment_receipts WHERE organizer_id = $1 AND to_char(payment_date, 'YYYY-MM') = m.month_str AND status = 'SUCCESS'), 0) +
                  COALESCE((SELECT SUM(maintenance_charge_amount) FROM chit_month_financial_closures WHERE organizer_id = $1 AND to_char(created_at, 'YYYY-MM') = m.month_str), 0) -
                  COALESCE((SELECT SUM(payout_amount) FROM chit_winner_payouts WHERE organizer_id = $1 AND to_char(payout_date, 'YYYY-MM') = m.month_str AND status IN ('PAID', 'WINNER_CONFIRMED')), 0)
                ) as net_cash_flow
            FROM months m
            ORDER BY m.month_str DESC
        """
        rows = await self.db_object.fetch(q, tenant_id)
        total = len(rows)
        # Apply pagination manually here since it's a CTE/UNION approach
        if limit > 0:
            paginated_rows = rows[skip:skip+limit]
        else:
            paginated_rows = rows
        return [dict(r) for r in paginated_rows], total

    async def get_chit_performance_report(self, tenant_id: UUID, skip: int, limit: int) -> Tuple[List[Dict], int]:
        base_where = "cg.organizer_id = $1 AND cg.is_deleted = FALSE"
        params = [tenant_id]

        count_q = f"SELECT COUNT(*) FROM chit_groups cg WHERE {base_where}"
        total = await self.db_object.fetchval(count_q, *params)

        if limit > 0:
            limit_clause = f"LIMIT {limit} OFFSET {skip}"
        else:
            limit_clause = ""

        q = f"""
            SELECT 
                cg.id as chit_group_id, cg.chit_name as chit_group_name, cg.status,
                CASE WHEN cg.duration_months > 0 THEN (COALESCE((SELECT COUNT(*) FROM chit_auctions WHERE chit_group_id = cg.id AND status = 'FINALIZED'), 0)::float / cg.duration_months) * 100 ELSE 0 END as completion_percentage,
                (SELECT COUNT(*) FROM chit_memberships WHERE chit_group_id = cg.id AND status = 'ACTIVE') as total_members,
                COALESCE((SELECT SUM(payment_amount) FROM chit_payment_receipts WHERE chit_group_id = cg.id AND status = 'SUCCESS'), 0) as total_collections,
                COALESCE((SELECT SUM(remaining_amount) FROM monthly_member_dues WHERE chit_group_id = cg.id AND payment_status IN ('PENDING', 'PARTIALLY_PAID', 'OVERDUE')), 0) as total_pending,
                (SELECT COUNT(*) FROM chit_auctions WHERE chit_group_id = cg.id) as auction_count,
                CASE 
                    WHEN COALESCE((SELECT SUM(remaining_amount) FROM monthly_member_dues WHERE chit_group_id = cg.id AND payment_status IN ('PENDING', 'PARTIALLY_PAID', 'OVERDUE')), 0) > cg.total_chit_value * 0.2 THEN 'High'
                    WHEN COALESCE((SELECT SUM(remaining_amount) FROM monthly_member_dues WHERE chit_group_id = cg.id AND payment_status IN ('PENDING', 'PARTIALLY_PAID', 'OVERDUE')), 0) > cg.total_chit_value * 0.1 THEN 'Medium'
                    ELSE 'Low'
                END as risk_score
            FROM chit_groups cg
            WHERE {base_where}
            ORDER BY cg.created_at DESC
            {limit_clause}
        """
        rows = await self.db_object.fetch(q, *params)
        return [dict(r) for r in rows], total
