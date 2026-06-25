import asyncpg
from uuid import UUID
from datetime import datetime
from src.api.models.models import User
from src.api.schemas.member_portal_schema import (
    MemberDashboardResponse, MemberDashboardStats, UpcomingDueResponse, 
    RecentPaymentResponse, RecentAuctionResponse, WinnerPayoutPreviewResponse,
    ChitSummaryResponse, NotificationListResponse, ProfileUpdateResponse, NotificationResponse
)
from src.shared.common.exceptions import AppError

class MemberPortalController:
    def __init__(self, db_object: asyncpg.Connection):
        self.db = db_object

    async def get_dashboard(self, current_user: User) -> MemberDashboardResponse:
        member_id = current_user.member_id
        organizer_id = current_user.organizer_id
        
        # Stats
        active_chits_query = """
            SELECT COUNT(DISTINCT cg.id) 
            FROM chit_groups cg
            JOIN chit_memberships cm ON cg.id = cm.chit_group_id
            WHERE cm.member_id = $1 AND cg.status = 'ACTIVE' AND cg.is_deleted = FALSE AND cm.is_deleted = FALSE
        """
        active_chits = await self.db.fetchval(active_chits_query, member_id) or 0
        
        shares_held_query = """
            SELECT SUM(share_count)
            FROM chit_memberships
            WHERE member_id = $1 AND status = 'ACTIVE' AND is_deleted = FALSE
        """
        shares_held = await self.db.fetchval(shares_held_query, member_id) or 0
        
        # Dues
        dues_query = """
            SELECT SUM(remaining_amount) 
            FROM monthly_member_dues 
            WHERE member_id = $1 AND payment_status IN ('PENDING', 'PARTIALLY_PAID', 'OVERDUE')
        """
        pending_overdue_amount = await self.db.fetchval(dues_query, member_id) or 0
        
        # Payments this month
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        payments_query = """
            SELECT SUM(payment_amount) 
            FROM chit_payment_receipts 
            WHERE member_id = $1 AND status = 'SUCCESS' AND payment_date >= $2
        """
        payments_this_month = await self.db.fetchval(payments_query, member_id, current_month_start) or 0
        
        # Total Dividends
        # Dividends are bonus_per_share * share_count
        dividends_query = """
            SELECT SUM(total_bonus_amount)
            FROM monthly_member_dues
            WHERE member_id = $1
        """
        total_dividends = await self.db.fetchval(dividends_query, member_id) or 0

        stats = MemberDashboardStats(
            active_chit_groups=active_chits,
            total_shares_held=shares_held,
            current_month_due=0, # Simplifying for now, can be calculated
            pending_overdue_amount=float(pending_overdue_amount),
            payments_made_this_month=float(payments_this_month),
            total_dividends_earned=float(total_dividends)
        )

        # Upcoming dues
        upcoming_dues_query = """
            SELECT d.chit_group_id, cg.chit_name, d.month_number, d.due_date, d.remaining_amount, d.payment_status
            FROM monthly_member_dues d
            JOIN chit_groups cg ON d.chit_group_id = cg.id
            WHERE d.member_id = $1 AND d.payment_status IN ('PENDING', 'PARTIALLY_PAID', 'OVERDUE')
            ORDER BY d.due_date ASC NULLS LAST
            LIMIT 5
        """
        dues_rows = await self.db.fetch(upcoming_dues_query, member_id)
        upcoming_dues = [
            UpcomingDueResponse(
                chit_group_id=row['chit_group_id'],
                chit_group_name=row['chit_name'],
                month_number=row['month_number'],
                due_date=row['due_date'],
                amount_due=float(row['remaining_amount']),
                status=row['payment_status']
            ) for row in dues_rows
        ]

        # Recent Payments
        recent_payments_query = """
            SELECT r.id, r.receipt_number, cg.chit_name, r.payment_amount, r.payment_date, r.status
            FROM chit_payment_receipts r
            JOIN chit_groups cg ON r.chit_group_id = cg.id
            WHERE r.member_id = $1
            ORDER BY r.payment_date DESC
            LIMIT 5
        """
        payments_rows = await self.db.fetch(recent_payments_query, member_id)
        recent_payments = [
            RecentPaymentResponse(
                receipt_id=row['id'],
                receipt_number=row['receipt_number'],
                chit_group_name=row['chit_name'],
                amount=float(row['payment_amount']),
                payment_date=row['payment_date'],
                status=row['status']
            ) for row in payments_rows
        ]

        # Recent Auctions
        auctions_query = """
            SELECT a.id, cg.chit_name, a.auction_month_number, m.full_name as winner_name, a.total_discount_amount, a.bonus_per_share, a.auction_date
            FROM chit_auctions a
            JOIN chit_groups cg ON a.chit_group_id = cg.id
            JOIN chit_memberships cm ON cg.id = cm.chit_group_id
            LEFT JOIN members m ON a.winner_member_id = m.id
            WHERE cm.member_id = $1 AND a.status = 'FINALIZED'
            ORDER BY a.auction_date DESC
            LIMIT 5
        """
        auctions_rows = await self.db.fetch(auctions_query, member_id)
        recent_auctions = [
            RecentAuctionResponse(
                auction_id=row['id'],
                chit_group_name=row['chit_name'],
                month_number=row['auction_month_number'],
                winner_name=row['winner_name'],
                winning_discount=float(row['total_discount_amount'] or 0),
                dividend_per_share=float(row['bonus_per_share'] or 0),
                auction_date=row['auction_date']
            ) for row in auctions_rows
        ]

        # Winner Payouts
        payouts_query = """
            SELECT id, status, payout_amount
            FROM chit_winner_payouts
            WHERE winner_member_id = $1
            ORDER BY payout_date DESC
            LIMIT 3
        """
        payouts_rows = await self.db.fetch(payouts_query, member_id)
        winner_payouts = [
            WinnerPayoutPreviewResponse(
                payout_id=row['id'],
                status=row['status'],
                net_payout_amount=float(row['payout_amount'])
            ) for row in payouts_rows
        ]

        return MemberDashboardResponse(
            stats=stats,
            upcoming_dues=upcoming_dues,
            recent_payments=recent_payments,
            recent_auctions=recent_auctions,
            winner_payouts=winner_payouts
        )

    async def list_chits(self, current_user: User) -> list[ChitSummaryResponse]:
        member_id = current_user.member_id
        query = """
            SELECT cg.id, cg.chit_name, cg.chit_code, o.name as organizer_name, cg.start_date, cg.duration_months,
                   (SELECT COUNT(*) FROM chit_auctions WHERE chit_group_id = cg.id AND status = 'FINALIZED') as current_month,
                   cg.status, cm.share_count, cg.monthly_installment_per_share, 
                   (cm.share_count * cg.monthly_installment_per_share) as total_payable
            FROM chit_groups cg
            JOIN chit_memberships cm ON cg.id = cm.chit_group_id
            JOIN organizers o ON cg.organizer_id = o.id
            WHERE cm.member_id = $1 AND cg.is_deleted = FALSE AND cm.is_deleted = FALSE
        """
        rows = await self.db.fetch(query, member_id)
        return [
            ChitSummaryResponse(
                chit_group_id=row['id'],
                chit_group_name=row['chit_name'],
                chit_code=row['chit_code'],
                organizer_name=row['organizer_name'],
                start_date=row['start_date'],
                duration_months=row['duration_months'],
                current_month=row['current_month'],
                status=row['status'],
                shares_held=row['share_count'],
                monthly_installment_per_share=float(row['monthly_installment_per_share']),
                total_monthly_payable=float(row['total_payable']),
                next_due_date=None,
                current_payment_status="UNKNOWN"
            ) for row in rows
        ]
        
    async def get_notifications(self, current_user: User, page: int = 1, page_size: int = 20) -> NotificationListResponse:
        offset = (page - 1) * page_size
        
        count_query = "SELECT COUNT(*) FROM notifications WHERE user_id = $1"
        total = await self.db.fetchval(count_query, current_user.id)
        
        query = """
            SELECT id, notification_type, title, message, reference_type, reference_id, is_read, created_at
            FROM notifications
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
        """
        rows = await self.db.fetch(query, current_user.id, page_size, offset)
        items = [NotificationResponse(**dict(r)) for r in rows]
        
        return NotificationListResponse(items=items, total=total, page=page, page_size=page_size)
