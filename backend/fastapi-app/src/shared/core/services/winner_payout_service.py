from uuid import UUID
from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException
import urllib.parse

from src.api.models.models import User
from src.shared.core.repository.chit_auction_repository import ChitAuctionRepository
from src.shared.core.repository.chit_group_repository import ChitGroupRepository
from src.shared.core.repository.monthly_member_due_repository import MonthlyMemberDueRepository
from src.shared.core.repository.chit_winner_payout_repository import ChitWinnerPayoutRepository, ChitWinnerPayoutActivityLogRepository
from src.shared.core.repository.payment_receipt_sequence_repository import PaymentReceiptSequenceRepository
from src.shared.core.repository.organizer_repository import OrganizerRepository
from src.api.schemas.winner_payout_schema import (
    WinnerPayoutCreateRequest,
    WinnerPayoutUpdateRequest,
    WinnerPayoutInitiatePaymentRequest,
    WinnerPayoutMarkPaidRequest,
    WinnerPayoutConfirmReceivedRequest,
    WinnerPayoutCancelRequest,
    WinnerPayoutReverseRequest,
    WinnerPayoutShareResponse
)
from src.shared.core.properties.constants import PayoutStatus, AuctionStatus, UserRole, ActivityAction

class WinnerPayoutService:
    def __init__(self, db_object):
        self.db = db_object

    async def _get_auction_and_validate(self, auction_id: UUID, organizer_id: UUID):
        auction_repo = ChitAuctionRepository(self.db)
        auction = await auction_repo.get_auction_by_id(auction_id, organizer_id)
        if not auction:
            raise HTTPException(status_code=404, detail="Auction not found")
        if auction["status"] not in {AuctionStatus.CLOSED.value, AuctionStatus.FINALIZED.value}:
            raise HTTPException(status_code=400, detail="Auction must be finalized to process payout")
        if not auction["winner_membership_id"]:
            raise HTTPException(status_code=400, detail="No winner assigned to this auction")
        return auction

    async def create_draft(self, current_user: User, request: WinnerPayoutCreateRequest) -> dict:
        organizer_id = current_user.organizer_id
        
        async with self.db.transaction():
            payout_repo = ChitWinnerPayoutRepository(self.db)
            
            auction = await self._get_auction_and_validate(request.auction_id, organizer_id)
            chit_group_id = auction["chit_group_id"]
            month_number = auction["auction_month_number"]

            active_payout = await payout_repo.get_active_payout_by_group_and_month(chit_group_id, month_number, organizer_id)
            if active_payout:
                raise HTTPException(status_code=400, detail="An active payout already exists for this month")

            gross = Decimal(str(auction["gross_chit_amount"]))
            discount = Decimal(str(auction["total_discount_amount"]))
            maintenance = Decimal(str(auction["maintenance_charge"]))
            payout_amount = gross - discount - maintenance

            payout_data = {
                "organizer_id": organizer_id,
                "chit_group_id": chit_group_id,
                "chit_auction_id": auction["id"],
                "winner_membership_id": auction["winner_membership_id"],
                "winner_member_id": auction["winner_member_id"],
                "month_number": month_number,
                "gross_chit_amount": gross,
                "winning_bid_discount_amount": discount,
                "maintenance_charge_amount": maintenance,
                "payout_amount": payout_amount,
                "payout_date": request.due_date or datetime.utcnow().date(),
                "remarks": request.payment_notes,
                "status": PayoutStatus.DRAFT.value
            }

            payout = await payout_repo.create_payout(payout_data, current_user.id)

            log_repo = ChitWinnerPayoutActivityLogRepository(self.db)
            await log_repo.create_log(
                organizer_id=organizer_id,
                winner_payout_id=payout["id"],
                action_type=ActivityAction.PAYOUT_DRAFT_CREATED.value,
                performed_by_user_id=current_user.id,
                new_values={"status": PayoutStatus.DRAFT.value}
            )
            return payout

    async def list_payouts(self, current_user: User, limit: int = 50, offset: int = 0) -> list:
        payout_repo = ChitWinnerPayoutRepository(self.db)
        return await payout_repo.list_payouts(current_user.organizer_id, limit, offset)

    async def get_payout(self, current_user: User, payout_id: UUID) -> dict:
        payout_repo = ChitWinnerPayoutRepository(self.db)
        payout = await payout_repo.get_payout_by_id(payout_id, current_user.organizer_id)
        if not payout:
            raise HTTPException(status_code=404, detail="Payout not found")
        return payout

    async def get_payout_public(self, payout_id: UUID) -> dict:
        payout_repo = ChitWinnerPayoutRepository(self.db)
        payout = await payout_repo.get_payout_public(payout_id)
        if not payout:
            raise HTTPException(status_code=404, detail="Payout not found")
        return payout

    async def update_draft(self, current_user: User, payout_id: UUID, request: WinnerPayoutUpdateRequest) -> dict:
        organizer_id = current_user.organizer_id
        async with self.db.transaction():
            payout_repo = ChitWinnerPayoutRepository(self.db)
            payout = await payout_repo.get_payout_for_update(payout_id, organizer_id)
            if not payout:
                raise HTTPException(status_code=404, detail="Payout not found")
            if payout["status"] not in [PayoutStatus.DRAFT.value, "PENDING_PAYMENT"]:
                raise HTTPException(status_code=400, detail="Cannot update payout in this status")

            updates = {}
            if request.due_date is not None:
                updates["payout_date"] = request.due_date
            if request.payment_notes is not None:
                updates["remarks"] = request.payment_notes

            updated_payout = await payout_repo.update_payout(payout_id, organizer_id, updates, current_user.id)

            log_repo = ChitWinnerPayoutActivityLogRepository(self.db)
            await log_repo.create_log(
                organizer_id=organizer_id,
                winner_payout_id=payout_id,
                action_type=ActivityAction.PAYOUT_INITIATED.value,
                performed_by_user_id=current_user.id,
                old_values={"payout_date": str(payout["payout_date"]), "remarks": payout["remarks"]},
                new_values={"payout_date": str(updates.get("payout_date", payout["payout_date"])), "remarks": updates.get("remarks", payout["remarks"])}
            )
            return updated_payout

    async def initiate_payment(self, current_user: User, payout_id: UUID, request: WinnerPayoutInitiatePaymentRequest) -> dict:
        organizer_id = current_user.organizer_id
        async with self.db.transaction():
            payout_repo = ChitWinnerPayoutRepository(self.db)
            payout = await payout_repo.get_payout_for_update(payout_id, organizer_id)
            if not payout:
                raise HTTPException(status_code=404, detail="Payout not found")
            if payout["status"] != PayoutStatus.DRAFT.value:
                raise HTTPException(status_code=400, detail="Only DRAFT payouts can be initiated")

            updates = {"status": "PENDING_PAYMENT"}
            if request.payment_notes:
                updates["remarks"] = request.payment_notes

            updated_payout = await payout_repo.update_payout(payout_id, organizer_id, updates, current_user.id)

            log_repo = ChitWinnerPayoutActivityLogRepository(self.db)
            await log_repo.create_log(
                organizer_id=organizer_id,
                winner_payout_id=payout_id,
                action_type=ActivityAction.PAYOUT_INITIATED.value,
                performed_by_user_id=current_user.id,
                new_values={"status": "PENDING_PAYMENT"}
            )
            return updated_payout

    async def mark_paid(self, current_user: User, payout_id: UUID, request: WinnerPayoutMarkPaidRequest, base_url: str) -> dict:
        organizer_id = current_user.organizer_id
        async with self.db.transaction():
            payout_repo = ChitWinnerPayoutRepository(self.db)
            payout = await payout_repo.get_payout_for_update(payout_id, organizer_id)
            if not payout:
                raise HTTPException(status_code=404, detail="Payout not found")
            
            if payout["status"] == PayoutStatus.PAID.value:
                # Idempotent response
                return await payout_repo.get_payout_by_id(payout_id, organizer_id)
                
            if payout["status"] not in [PayoutStatus.DRAFT.value, "PENDING_PAYMENT"]:
                raise HTTPException(status_code=400, detail="Cannot mark as paid from current status")

            if Decimal(str(payout["payout_amount"])) <= 0:
                raise HTTPException(status_code=400, detail="Payout amount must be > 0")

            if request.payment_mode in ["UPI", "BANK_TRANSFER", "CHEQUE"] and not request.transaction_reference:
                raise HTTPException(status_code=400, detail="Transaction reference is required for this payment mode")

            # Receipt sequence
            org_repo = OrganizerRepository(self.db)
            org = await org_repo.get_organizer_by_id(organizer_id)
            now = datetime.utcnow()
            year_month = now.strftime("%Y%m")
            prefix = f"PO-{org.organizer_code}-{year_month}"
            
            seq_repo = PaymentReceiptSequenceRepository(self.db)
            seq_num = await seq_repo.get_next_sequence(organizer_id, prefix)
            receipt_number = f"{prefix}-{str(seq_num).zfill(6)}"

            receipt_url = f"{base_url}/api/v1/winner-payouts/{payout_id}/receipt"

            updates = {
                "status": PayoutStatus.PAID.value,
                "payment_method": request.payment_mode,
                "transaction_reference": request.transaction_reference,
                "payout_date": request.paid_at.date(), # Store the timestamp as date if needed, or adjust model to timestamptz. Model has payout_date as Date. Wait, request specifies paid_at. Let's just use it as payout_date.
                "payout_receipt_number": receipt_number,
                "proof_file_url": request.proof_file_url,
                "receipt_html_url": receipt_url
            }
            if request.payment_notes:
                updates["remarks"] = request.payment_notes

            updated_payout = await payout_repo.update_payout(payout_id, organizer_id, updates, current_user.id)

            log_repo = ChitWinnerPayoutActivityLogRepository(self.db)
            await log_repo.create_log(
                organizer_id=organizer_id,
                winner_payout_id=payout_id,
                action_type=ActivityAction.PAYOUT_MARKED_PAID.value,
                performed_by_user_id=current_user.id,
                new_values={"status": PayoutStatus.PAID.value, "receipt_number": receipt_number}
            )
            await log_repo.create_log(
                organizer_id=organizer_id,
                winner_payout_id=payout_id,
                action_type=ActivityAction.PAYOUT_MARKED_PAID.value,
                performed_by_user_id=current_user.id,
                new_values={"receipt_url": receipt_url}
            )

            return updated_payout

    async def share_receipt(self, current_user: User, payout_id: UUID, base_url: str) -> WinnerPayoutShareResponse:
        organizer_id = current_user.organizer_id
        payout_repo = ChitWinnerPayoutRepository(self.db)
        payout = await payout_repo.get_payout_by_id(payout_id, organizer_id)
        
        if not payout:
            raise HTTPException(status_code=404, detail="Payout not found")
        if payout["status"] not in [PayoutStatus.PAID.value, PayoutStatus.WINNER_CONFIRMED.value, PayoutStatus.COMPLETED.value]:
            raise HTTPException(status_code=400, detail="Can only share paid or confirmed payouts")

        receipt_url = f"{base_url}/organizer/winner-payouts/{payout_id}/receipt" # Frontend URL or Backend URL, depending on setup. Let's return backend API url for html.
        
        cg_repo = ChitGroupRepository(self.db)
        cg = await cg_repo.get_chit_group_by_id_and_organizer(payout["chit_group_id"], organizer_id)

        msg = (
            f"Hello {payout['winner_name']},\n\n"
            f"Your winner payout has been completed.\n\n"
            f"Chit Group: {cg.chit_name}\n"
            f"Month: {payout['month_number']}\n"
            f"Net Payout: ₹{payout['payout_amount']}\n"
            f"Payment Mode: {payout['payment_method']}\n"
            f"Transaction Ref: {payout['transaction_reference'] or 'N/A'}\n\n"
            f"Receipt No: {payout['payout_receipt_number']}\n"
            f"Receipt: {receipt_url}"
        )

        encoded_msg = urllib.parse.quote(msg)
        mobile = payout['winner_phone']
        if not mobile.startswith("91") and len(mobile) == 10:
            mobile = "91" + mobile
        whatsapp_share_url = f"https://wa.me/{mobile}?text={encoded_msg}"

        log_repo = ChitWinnerPayoutActivityLogRepository(self.db)
        await log_repo.create_log(
            organizer_id=organizer_id,
            winner_payout_id=payout_id,
            action_type=ActivityAction.PAYOUT_CONFIRMED.value,
            performed_by_user_id=current_user.id,
            remarks="Shared via WhatsApp"
        )

        return WinnerPayoutShareResponse(
            receipt_number=payout["payout_receipt_number"],
            receipt_url=receipt_url,
            receipt_image_url=payout.get("receipt_image_url"),
            whatsapp_message=msg,
            whatsapp_share_url=whatsapp_share_url
        )

    async def confirm_received(self, current_user: User, payout_id: UUID, request: WinnerPayoutConfirmReceivedRequest) -> dict:
        # In this MVP, typically member logs in, but to support backend endpoint we use current_user.
        organizer_id = current_user.organizer_id
        async with self.db.transaction():
            payout_repo = ChitWinnerPayoutRepository(self.db)
            payout = await payout_repo.get_payout_for_update(payout_id, organizer_id)
            if not payout:
                raise HTTPException(status_code=404, detail="Payout not found")
            if payout["status"] not in [PayoutStatus.PAID.value, PayoutStatus.COMPLETED.value]:
                raise HTTPException(status_code=400, detail="Only PAID or COMPLETED payouts can be confirmed")
            
            if current_user.role == UserRole.ORGANIZER.value:
                raise HTTPException(status_code=403, detail="Organizers cannot confirm receipt on behalf of members")

            updates = {
                "status": PayoutStatus.WINNER_CONFIRMED.value,
                "winner_confirmed_at": datetime.utcnow(),
                "winner_confirmation_note": request.confirmation_note
            }

            updated_payout = await payout_repo.update_payout(payout_id, organizer_id, updates, current_user.id)

            log_repo = ChitWinnerPayoutActivityLogRepository(self.db)
            await log_repo.create_log(
                organizer_id=organizer_id,
                winner_payout_id=payout_id,
                action_type=ActivityAction.PAYOUT_CONFIRMED.value,
                performed_by_user_id=current_user.id,
                new_values={"status": PayoutStatus.WINNER_CONFIRMED.value}
            )
            return updated_payout

    async def cancel_payout(self, current_user: User, payout_id: UUID, request: WinnerPayoutCancelRequest) -> dict:
        organizer_id = current_user.organizer_id
        async with self.db.transaction():
            payout_repo = ChitWinnerPayoutRepository(self.db)
            payout = await payout_repo.get_payout_for_update(payout_id, organizer_id)
            if not payout:
                raise HTTPException(status_code=404, detail="Payout not found")
            if payout["status"] not in [PayoutStatus.DRAFT.value, "PENDING_PAYMENT"]:
                raise HTTPException(status_code=400, detail="Only Draft or Pending payouts can be cancelled")

            updates = {
                "status": PayoutStatus.CANCELLED.value,
                "reversal_reason": request.reason
            }

            updated_payout = await payout_repo.update_payout(payout_id, organizer_id, updates, current_user.id)

            log_repo = ChitWinnerPayoutActivityLogRepository(self.db)
            await log_repo.create_log(
                organizer_id=organizer_id,
                winner_payout_id=payout_id,
                action_type=ActivityAction.PAYOUT_CANCELLED.value,
                performed_by_user_id=current_user.id,
                new_values={"status": PayoutStatus.CANCELLED.value, "reason": request.reason}
            )
            return updated_payout

    async def reverse_payout(self, current_user: User, payout_id: UUID, request: WinnerPayoutReverseRequest) -> dict:
        organizer_id = current_user.organizer_id
        async with self.db.transaction():
            payout_repo = ChitWinnerPayoutRepository(self.db)
            payout = await payout_repo.get_payout_for_update(payout_id, organizer_id)
            if not payout:
                raise HTTPException(status_code=404, detail="Payout not found")
            if payout["status"] not in [PayoutStatus.PAID.value, PayoutStatus.COMPLETED.value]:
                raise HTTPException(status_code=400, detail="Only PAID or COMPLETED payouts can be reversed")

            updated_payout = await payout_repo.reverse_payout(payout_id, organizer_id, request.reason, current_user.id)

            log_repo = ChitWinnerPayoutActivityLogRepository(self.db)
            await log_repo.create_log(
                organizer_id=organizer_id,
                winner_payout_id=payout_id,
                action_type=ActivityAction.PAYOUT_REVERSED.value,
                performed_by_user_id=current_user.id,
                new_values={"status": PayoutStatus.REVERSED.value, "reason": request.reason, "reference": request.reversal_reference}
            )
            return updated_payout
