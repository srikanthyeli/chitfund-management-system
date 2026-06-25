from uuid import UUID
import uuid
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class ChitMonthFinancialClosureRepository:
    def __init__(self, db_object):
        self.db = db_object

    async def get_closure_by_group_and_month(self, chit_group_id: UUID, month_number: int, organizer_id: UUID) -> Optional[dict]:
        query = """
            SELECT * FROM chit_month_financial_closures
            WHERE chit_group_id = $1 AND month_number = $2 AND organizer_id = $3
        """
        row = await self.db.fetchrow(query, chit_group_id, month_number, organizer_id)
        return dict(row) if row else None

    async def get_closure_for_update(self, closure_id: UUID, organizer_id: UUID) -> Optional[dict]:
        query = """
            SELECT * FROM chit_month_financial_closures
            WHERE id = $1 AND organizer_id = $2
            FOR UPDATE
        """
        row = await self.db.fetchrow(query, closure_id, organizer_id)
        return dict(row) if row else None

    async def create_closure(self, data: dict, created_by: UUID) -> dict:
        now = datetime.utcnow()
        closure_id = uuid.uuid4()
        query = """
            INSERT INTO chit_month_financial_closures (
                id, organizer_id, chit_group_id, chit_auction_id, month_number,
                total_shares, active_member_count,
                gross_chit_amount, winning_bid_discount_amount, maintenance_charge_amount,
                dividend_pool_amount, dividend_per_share,
                expected_collection_amount, actual_collection_amount, pending_collection_amount,
                winner_payout_amount, organizer_contribution_amount,
                net_cash_position, shortfall_amount, surplus_amount,
                closure_status, remarks,
                created_at, created_by, is_deleted, version
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24, FALSE, 1
            ) RETURNING *
        """
        row = await self.db.fetchrow(
            query,
            closure_id,
            data["organizer_id"],
            data["chit_group_id"],
            data["chit_auction_id"],
            data["month_number"],
            data["total_shares"],
            data["active_member_count"],
            Decimal(str(data["gross_chit_amount"])),
            Decimal(str(data["winning_bid_discount_amount"])),
            Decimal(str(data["maintenance_charge_amount"])),
            Decimal(str(data["dividend_pool_amount"])),
            Decimal(str(data["dividend_per_share"])),
            Decimal(str(data["expected_collection_amount"])),
            Decimal(str(data["actual_collection_amount"])),
            Decimal(str(data["pending_collection_amount"])),
            Decimal(str(data["winner_payout_amount"])),
            Decimal(str(data["organizer_contribution_amount"])),
            Decimal(str(data["net_cash_position"])),
            Decimal(str(data["shortfall_amount"])),
            Decimal(str(data["surplus_amount"])),
            data["closure_status"],
            data.get("remarks"),
            now,
            created_by
        )
        return dict(row)

    async def update_closure(self, closure_id: UUID, data: dict, updated_by: UUID) -> dict:
        now = datetime.utcnow()
        
        # Build dynamic update query
        set_clauses = []
        values = []
        idx = 1
        
        for key, value in data.items():
            if value is not None and isinstance(value, (int, float, str)):
                # Cast to Decimal for numeric fields to ensure type matching in asyncpg
                if key in ["gross_chit_amount", "winning_bid_discount_amount", "maintenance_charge_amount", 
                           "dividend_pool_amount", "dividend_per_share", "expected_collection_amount", 
                           "actual_collection_amount", "pending_collection_amount", "winner_payout_amount", 
                           "organizer_contribution_amount", "net_cash_position", "shortfall_amount", "surplus_amount"]:
                    values.append(Decimal(str(value)))
                else:
                    values.append(value)
                set_clauses.append(f"{key} = ${idx}")
                idx += 1
                
        set_clauses.append(f"updated_at = ${idx}")
        values.append(now)
        idx += 1
        
        set_clauses.append(f"updated_by = ${idx}")
        values.append(updated_by)
        idx += 1
        
        set_clauses.append(f"version = version + 1")
        
        query = f"""
            UPDATE chit_month_financial_closures
            SET {', '.join(set_clauses)}
            WHERE id = ${idx}
            RETURNING *
        """
        values.append(closure_id)
        
        row = await self.db.fetchrow(query, *values)
        return dict(row)

    async def get_financial_summary(self, chit_group_id: UUID, organizer_id: UUID) -> dict:
        query = """
            SELECT
                COUNT(id) AS completed_months,
                COALESCE(SUM(expected_collection_amount), 0) AS total_expected_collection,
                COALESCE(SUM(actual_collection_amount), 0) AS total_actual_collection,
                COALESCE(SUM(pending_collection_amount), 0) AS total_pending_collection,
                COALESCE(SUM(winner_payout_amount), 0) AS total_winner_payouts,
                COALESCE(SUM(maintenance_charge_amount), 0) AS total_maintenance_collected,
                COALESCE(SUM(organizer_contribution_amount), 0) AS total_organizer_contribution,
                COALESCE(SUM(shortfall_amount), 0) AS total_shortfall
            FROM chit_month_financial_closures
            WHERE chit_group_id = $1 AND organizer_id = $2 AND is_deleted = FALSE
        """
        row = await self.db.fetchrow(query, chit_group_id, organizer_id)
        return dict(row)

    async def get_monthly_summaries(self, chit_group_id: UUID, organizer_id: UUID) -> List[dict]:
        query = """
            SELECT 
                a.id as auction_id,
                a.auction_month_number as month_number,
                COALESCE(c.id, gen_random_uuid()) as id,
                COALESCE(c.closure_status, 'OPEN') as closure_status,
                COALESCE(c.actual_collection_amount, 0) as actual_collection_amount,
                COALESCE(c.winner_payout_amount, 0) as winner_payout_amount
            FROM chit_auctions a
            LEFT JOIN chit_month_financial_closures c 
                ON a.id = c.chit_auction_id AND c.is_deleted = FALSE
            WHERE a.chit_group_id = $1 
              AND a.organizer_id = $2 
              AND a.status = 'FINALIZED'
            ORDER BY a.auction_month_number ASC
        """
        rows = await self.db.fetch(query, chit_group_id, organizer_id)
        return [dict(row) for row in rows]

    async def close_month(self, closure_id: UUID, organizer_id: UUID, closed_by: UUID, remarks: str) -> Optional[dict]:
        now = datetime.utcnow()
        query = """
            UPDATE chit_month_financial_closures
            SET closure_status = 'CLOSED', closed_at = $1, closed_by_user_id = $2,
                remarks = $3, updated_at = $1, updated_by = $2, version = version + 1
            WHERE id = $4 AND organizer_id = $5 AND closure_status = 'READY_FOR_CLOSURE'
            RETURNING *
        """
        row = await self.db.fetchrow(query, now, closed_by, remarks, closure_id, organizer_id)
        return dict(row) if row else None
