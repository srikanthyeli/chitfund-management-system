from uuid import UUID
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException
from typing import Optional, List

from src.shared.core.repository.chit_auction_repository import ChitAuctionRepository
from src.shared.core.repository.chit_auction_bid_repository import ChitAuctionBidRepository
from src.shared.core.repository.monthly_member_due_repository import MonthlyMemberDueRepository
from src.shared.core.repository.chit_group_repository import ChitGroupRepository
from src.shared.core.repository.chit_membership_repository import ChitMembershipRepository
from src.shared.core.repository.chit_group_activity_log_repository import ChitGroupActivityLogRepository
from src.api.schemas.chit_auction_schema import CreateAuctionRequest, SubmitBidRequest
from src.api.models.models import User


def _round_money(value: Decimal) -> Decimal:
    """Round to 2 decimal places using ROUND_HALF_UP (standard financial rounding)."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class ChitAuctionService:
    def __init__(self, db_object):
        self.db = db_object
        self.auction_repo = ChitAuctionRepository(db_object)
        self.bid_repo = ChitAuctionBidRepository(db_object)
        self.due_repo = MonthlyMemberDueRepository(db_object)
        self.chit_repo = ChitGroupRepository(db_object)
        self.membership_repo = ChitMembershipRepository(db_object)
        self.activity_repo = ChitGroupActivityLogRepository(db_object)

    def _require_organizer(self, current_user: User):
        if current_user.role != "ORGANIZER" or not current_user.organizer_id:
            raise HTTPException(status_code=403, detail="Only organizers can perform this action")

    # ─── Create Auction ───────────────────────────────────────────────────────

    async def create_auction(self, current_user: User, chit_group_id: UUID, request: CreateAuctionRequest) -> dict:
        self._require_organizer(current_user)
        organizer_id = current_user.organizer_id

        # Validate chit group
        chit = await self.chit_repo.get_chit_group_by_id_and_organizer(chit_group_id, organizer_id)
        if not chit:
            raise HTTPException(status_code=404, detail="Chit group not found")
        if chit.status != "ACTIVE":
            raise HTTPException(status_code=400, detail=f"Auctions can only be created for ACTIVE chit groups. Current status: {chit.status}")

        # Validate month number range
        if request.auction_month_number > chit.duration_months:
            raise HTTPException(
                status_code=400,
                detail=f"Month number {request.auction_month_number} exceeds chit duration of {chit.duration_months} months"
            )

        # Uniqueness check
        existing = await self.auction_repo.get_auction_by_chit_and_month(chit_group_id, request.auction_month_number)
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"An auction already exists for month {request.auction_month_number} of this chit group"
            )

        # Derive gross chit amount from DB — never trust frontend
        gross_chit_amount = _round_money(
            Decimal(str(chit.monthly_installment_per_share)) * chit.total_shares
        )
        maintenance_charge = _round_money(Decimal(str(request.maintenance_charge)))
        maximum_bid_discount = _round_money(gross_chit_amount - maintenance_charge)

        if maximum_bid_discount <= Decimal("0"):
            raise HTTPException(status_code=400, detail="Maintenance charge cannot exceed or equal gross chit amount")

        data = {
            "organizer_id": organizer_id,
            "chit_group_id": chit_group_id,
            "auction_month_number": request.auction_month_number,
            "auction_date": request.auction_date,
            "gross_chit_amount": gross_chit_amount,
            "maintenance_charge": maintenance_charge,
            "maximum_bid_discount": maximum_bid_discount,
            "notes": request.notes,
        }

        async with self.db.transaction():
            auction = await self.auction_repo.create_auction(data, current_user.id)
            await self.activity_repo.create_log(
                organizer_id=organizer_id,
                chit_group_id=chit_group_id,
                action_type="AUCTION_CREATED",
                new_values={
                    "auction_id": str(auction["id"]),
                    "month_number": request.auction_month_number,
                    "auction_date": str(request.auction_date),
                    "gross_chit_amount": str(gross_chit_amount),
                    "maintenance_charge": str(maintenance_charge),
                    "maximum_bid_discount": str(maximum_bid_discount),
                },
                remarks=f"Auction created for month {request.auction_month_number}",
                performed_by_user_id=current_user.id,
            )

        return auction

    # ─── List Auctions ────────────────────────────────────────────────────────

    async def list_auctions(self, current_user: User, chit_group_id: UUID) -> dict:
        self._require_organizer(current_user)
        organizer_id = current_user.organizer_id

        chit = await self.chit_repo.get_chit_group_by_id_and_organizer(chit_group_id, organizer_id)
        if not chit:
            raise HTTPException(status_code=404, detail="Chit group not found")

        items = await self.auction_repo.list_auctions_by_chit_group(chit_group_id, organizer_id)
        return {"items": items, "total": len(items)}

    # ─── Get Auction Detail ───────────────────────────────────────────────────

    async def get_auction_detail(self, current_user: User, auction_id: UUID) -> dict:
        self._require_organizer(current_user)
        organizer_id = current_user.organizer_id

        auction = await self.auction_repo.get_auction_by_id(auction_id, organizer_id)
        if not auction:
            raise HTTPException(status_code=404, detail="Auction not found")

        # Fetch all bids with member info
        all_bids = await self.bid_repo.list_bids_for_auction(auction_id)

        # Mark highest bid
        highest_discount = None
        if all_bids:
            highest_discount = max(b["bid_discount_amount"] for b in all_bids if b["status"] == "ACTIVE")

        bids_enriched = []
        for b in all_bids:
            b_copy = dict(b)
            b_copy["is_highest"] = (
                b["status"] == "ACTIVE" and
                highest_discount is not None and
                b["bid_discount_amount"] == highest_discount
            )
            bids_enriched.append(b_copy)

        # Eligible members (active memberships that haven't won before)
        memberships = await self.membership_repo.list_active_memberships_with_members(
            auction["chit_group_id"], organizer_id
        )
        eligible = [m for m in memberships if not m["has_won_auction"]]

        # Winner info if finalized
        winner = None
        if auction["status"] == "FINALIZED" and auction.get("winner_membership_id"):
            # Find winner name from memberships
            winner_membership = next(
                (m for m in memberships if str(m["membership_id"]) == str(auction["winner_membership_id"])), None
            )
            if winner_membership:
                winner = {
                    "membership_id": auction["winner_membership_id"],
                    "member_id": auction["winner_member_id"],
                    "member_name": winner_membership["full_name"],
                    "member_code": winner_membership["member_code"],
                    "winning_discount": auction["total_discount_amount"],
                    "winner_payout_amount": auction["winner_payout_amount"],
                    "bonus_per_share": auction["bonus_per_share"],
                }

        return {
            **auction,
            "bids": bids_enriched,
            "eligible_members": eligible,
            "winner": winner,
        }

    # ─── Submit Bid ───────────────────────────────────────────────────────────

    async def submit_bid(self, current_user: User, auction_id: UUID, request: SubmitBidRequest) -> dict:
        self._require_organizer(current_user)
        organizer_id = current_user.organizer_id

        # Fetch auction (with organizer scope)
        auction = await self.auction_repo.get_auction_by_id(auction_id, organizer_id)
        if not auction:
            raise HTTPException(status_code=404, detail="Auction not found")
        if auction["status"] != "OPEN":
            raise HTTPException(status_code=400, detail=f"Auction is not open for bids. Status: {auction['status']}")

        # Validate membership belongs to this organizer and chit group
        membership = await self.membership_repo.get_membership_by_id_and_organizer(
            request.membership_id, organizer_id
        )
        if not membership:
            raise HTTPException(status_code=404, detail="Membership not found")
        if str(membership.chit_group_id) != str(auction["chit_group_id"]):
            raise HTTPException(status_code=400, detail="Membership does not belong to this chit group")
        if membership.status != "ACTIVE":
            raise HTTPException(status_code=400, detail="Only active memberships can bid")

        # Winner exclusion rule
        if membership.has_won_auction:
            raise HTTPException(
                status_code=400,
                detail=f"This member has already won month {membership.won_month_number} and cannot bid again"
            )

        # Validate bid amount
        bid_amount = _round_money(Decimal(str(request.bid_discount_amount)))
        max_allowed = _round_money(Decimal(str(auction["maximum_bid_discount"])))
        if bid_amount <= Decimal("0"):
            raise HTTPException(status_code=400, detail="Bid discount amount must be greater than zero")
        if bid_amount > max_allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Bid discount {bid_amount} exceeds maximum allowed {max_allowed}"
            )

        # Duplicate bid check
        existing_bid = await self.bid_repo.get_bid_by_auction_and_membership(auction_id, request.membership_id)
        if existing_bid:
            raise HTTPException(status_code=409, detail="This membership has already placed a bid in this auction")

        bid_data = {
            "organizer_id": organizer_id,
            "chit_auction_id": auction_id,
            "chit_group_id": auction["chit_group_id"],
            "membership_id": request.membership_id,
            "member_id": membership.member_id,
            "bid_discount_amount": bid_amount,
            "remarks": request.remarks,
        }

        async with self.db.transaction():
            bid = await self.bid_repo.create_bid(bid_data, current_user.id)
            await self.activity_repo.create_log(
                organizer_id=organizer_id,
                chit_group_id=auction["chit_group_id"],
                membership_id=request.membership_id,
                action_type="AUCTION_BID_SUBMITTED",
                new_values={
                    "auction_id": str(auction_id),
                    "bid_id": str(bid["id"]),
                    "bid_discount_amount": str(bid_amount),
                    "membership_id": str(request.membership_id),
                },
                remarks=f"Bid of ₹{bid_amount} submitted for month {auction['auction_month_number']}",
                performed_by_user_id=current_user.id,
            )

        return bid

    # ─── Finalize Auction ─────────────────────────────────────────────────────

    async def finalize_auction(self, current_user: User, auction_id: UUID) -> dict:
        self._require_organizer(current_user)
        organizer_id = current_user.organizer_id

        # Quick pre-check (no lock) to fail fast
        auction_check = await self.auction_repo.get_auction_by_id(auction_id, organizer_id)
        if not auction_check:
            raise HTTPException(status_code=404, detail="Auction not found")
        if auction_check["status"] != "OPEN":
            raise HTTPException(status_code=400, detail=f"Auction cannot be finalized. Status: {auction_check['status']}")

        chit_group_id = auction_check["chit_group_id"]

        async with self.db.transaction():
            # 1. Lock auction row — NOWAIT raises immediately on concurrent finalize
            try:
                auction = await self.auction_repo.lock_auction_for_finalize(auction_id)
            except Exception:
                raise HTTPException(status_code=409, detail="Auction is currently being processed by another request")

            if not auction:
                raise HTTPException(status_code=404, detail="Auction not found")

            # 2. Re-validate status inside transaction
            if auction["status"] != "OPEN":
                raise HTTPException(status_code=400, detail=f"Auction already {auction['status']}")

            # 3. Fetch and lock active bids
            try:
                bids = await self.bid_repo.lock_active_bids_for_auction(auction_id)
            except Exception:
                raise HTTPException(status_code=409, detail="Bid rows are locked by another process")

            if not bids:
                raise HTTPException(status_code=400, detail="Cannot finalize: no active bids in this auction")

            # 4. Select winner — highest discount, tie-break by earliest bid_time
            winner_bid = bids[0]  # Already ordered by bid_discount_amount DESC, bid_time ASC

            # 5. Fetch all active memberships for dues generation
            memberships = await self.membership_repo.list_active_memberships_with_members(
                chit_group_id, organizer_id
            )
            if not memberships:
                raise HTTPException(status_code=400, detail="No active memberships found in this chit group")

            # 6. Calculate amounts
            gross = _round_money(Decimal(str(auction["gross_chit_amount"])))
            maintenance = _round_money(Decimal(str(auction["maintenance_charge"])))
            winning_discount = _round_money(Decimal(str(winner_bid["bid_discount_amount"])))

            winner_payout = _round_money(gross - maintenance - winning_discount)
            if winner_payout < Decimal("0"):
                raise HTTPException(status_code=400, detail="Winner payout would be negative — invalid bid configuration")

            total_active_shares = sum(m["share_count"] for m in memberships)
            bonus_per_share = _round_money(winning_discount / Decimal(total_active_shares))

            # 7. Update auction to FINALIZED
            finalized_auction = await self.auction_repo.finalize_auction(
                auction_id=auction_id,
                winner_membership_id=winner_bid["membership_id"],
                winner_member_id=winner_bid["member_id"],
                total_discount_amount=winning_discount,
                winner_payout_amount=winner_payout,
                bonus_per_share=bonus_per_share,
                finalized_by=current_user.id,
            )

            # 8. Mark winner membership — prevents future bidding
            await self.membership_repo.mark_winner(
                membership_id=winner_bid["membership_id"],
                auction_id=auction_id,
                month_number=auction["auction_month_number"],
                updated_by=current_user.id,
            )

            # 9. Generate monthly dues for ALL active memberships
            chit = await self.chit_repo.get_chit_group_by_id_and_organizer(chit_group_id, organizer_id)
            month_installment = _round_money(Decimal(str(chit.monthly_installment_per_share)))
            dues_data = []
            for m in memberships:
                share_count = m["share_count"]
                gross_inst = _round_money(month_installment * share_count)
                total_bonus = _round_money(bonus_per_share * Decimal(share_count))
                net_payable = _round_money(gross_inst - total_bonus)
                dues_data.append({
                    "organizer_id": organizer_id,
                    "chit_group_id": chit_group_id,
                    "chit_auction_id": auction_id,
                    "membership_id": m["membership_id"],
                    "member_id": m["member_id"],
                    "month_number": auction["auction_month_number"],
                    "share_count": share_count,
                    "gross_installment_amount": gross_inst,
                    "bonus_per_share": bonus_per_share,
                    "total_bonus_amount": total_bonus,
                    "net_payable_amount": net_payable,
                    "due_date": None,
                    "remarks": None,
                })
            await self.due_repo.bulk_create_dues(dues_data, current_user.id)

            # 10. Find winner member name for log
            winner_membership_info = next(
                (m for m in memberships if str(m["membership_id"]) == str(winner_bid["membership_id"])), {}
            )

            # 11. Activity log
            await self.activity_repo.create_log(
                organizer_id=organizer_id,
                chit_group_id=chit_group_id,
                action_type="AUCTION_FINALIZED",
                new_values={
                    "auction_id": str(auction_id),
                    "month_number": auction["auction_month_number"],
                    "winner_member_id": str(winner_bid["member_id"]),
                    "winner_membership_id": str(winner_bid["membership_id"]),
                    "winner_name": winner_membership_info.get("full_name", ""),
                    "winning_discount_amount": str(winning_discount),
                    "gross_chit_amount": str(gross),
                    "maintenance_charge": str(maintenance),
                    "winner_payout_amount": str(winner_payout),
                    "bonus_per_share": str(bonus_per_share),
                    "total_active_shares": total_active_shares,
                },
                remarks=f"Auction month {auction['auction_month_number']} finalized. Winner: {winner_membership_info.get('full_name', 'Unknown')}",
                performed_by_user_id=current_user.id,
            )
            await self.activity_repo.create_log(
                organizer_id=organizer_id,
                chit_group_id=chit_group_id,
                membership_id=winner_bid["membership_id"],
                action_type="AUCTION_WINNER_DECLARED",
                new_values={
                    "auction_id": str(auction_id),
                    "month_number": auction["auction_month_number"],
                    "winning_discount": str(winning_discount),
                    "winner_payout": str(winner_payout),
                },
                performed_by_user_id=current_user.id,
            )
            await self.activity_repo.create_log(
                organizer_id=organizer_id,
                chit_group_id=chit_group_id,
                action_type="MONTHLY_DUES_GENERATED",
                new_values={
                    "auction_id": str(auction_id),
                    "month_number": auction["auction_month_number"],
                    "total_members": len(dues_data),
                    "bonus_per_share": str(bonus_per_share),
                },
                performed_by_user_id=current_user.id,
            )

        return finalized_auction

    # ─── List Dues ────────────────────────────────────────────────────────────

    async def list_dues(self, current_user: User, auction_id: UUID) -> List[dict]:
        self._require_organizer(current_user)
        organizer_id = current_user.organizer_id

        auction = await self.auction_repo.get_auction_by_id(auction_id, organizer_id)
        if not auction:
            raise HTTPException(status_code=404, detail="Auction not found")

        return await self.due_repo.list_dues_by_auction(auction_id, organizer_id)
