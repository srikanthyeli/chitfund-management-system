from uuid import UUID
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime

from fastapi import HTTPException
from src.shared.core.repository.monthly_member_due_repository import MonthlyMemberDueRepository
from src.shared.core.repository.chit_payment_receipt_repository import ChitPaymentReceiptRepository
from src.shared.core.repository.payment_receipt_sequence_repository import PaymentReceiptSequenceRepository
from src.shared.core.repository.organizer_repository import OrganizerRepository
from src.api.schemas.chit_collection_schema import PaymentCollectionRequest, PaymentReversalRequest

class ChitCollectionService:
    def __init__(self, conn):
        # conn is a raw asyncpg Connection (same as every other service in this codebase)
        self.conn = conn

    async def get_active_collections(self, organizer_id: UUID) -> List[dict]:
        due_repo = MonthlyMemberDueRepository(self.conn)
        return await due_repo.get_active_collections_summary(organizer_id)

    async def get_collection_summary(self, organizer_id: UUID, auction_id: UUID) -> dict:
        due_repo = MonthlyMemberDueRepository(self.conn)
        dues = await due_repo.list_dues_by_auction(auction_id, organizer_id)

        if not dues:
            return {
                "summary": {
                    "total_memberships": 0, "total_net_payable": Decimal("0.00"),
                    "total_collected": Decimal("0.00"), "total_remaining": Decimal("0.00"),
                    "paid_count": 0, "partial_count": 0, "pending_count": 0, "overdue_count": 0
                },
                "dues": []
            }

        summary = {
            "total_memberships": len(dues),
            "total_net_payable": sum(d["net_payable_amount"] for d in dues),
            "total_collected": sum(d["total_paid_amount"] for d in dues),
            "total_remaining": sum(d["remaining_amount"] for d in dues),
            "paid_count": sum(1 for d in dues if d["payment_status"] == "PAID"),
            "partial_count": sum(1 for d in dues if d["payment_status"] == "PARTIALLY_PAID"),
            "pending_count": sum(1 for d in dues if d["payment_status"] == "PENDING"),
            "overdue_count": sum(1 for d in dues if d["payment_status"] == "OVERDUE"),
        }

        return {"summary": summary, "dues": dues}

    async def collect_payment(self, due_id: UUID, organizer_id: UUID, user_id: UUID, request: PaymentCollectionRequest) -> dict:
        async with self.conn.transaction():
            receipt_repo = ChitPaymentReceiptRepository(self.conn)

            # Idempotency check
            existing_receipt = await receipt_repo.get_receipt_by_client_request_id(request.client_request_id, organizer_id)
            if existing_receipt:
                due_repo = MonthlyMemberDueRepository(self.conn)
                due = await due_repo.get_due_for_update(existing_receipt["monthly_member_due_id"], organizer_id)
                return {"message": "Payment already recorded (idempotent)", "receipt": dict(existing_receipt), "due": dict(due) if due else None}

            due_repo = MonthlyMemberDueRepository(self.conn)
            due = await due_repo.get_due_for_update(due_id, organizer_id)

            if not due:
                raise HTTPException(status_code=404, detail="Due not found")

            if due["payment_status"] == "PAID":
                raise HTTPException(status_code=409, detail="Due is already fully paid")

            if Decimal(str(request.payment_amount)) > due["remaining_amount"]:
                raise HTTPException(status_code=400, detail="Payment amount cannot exceed remaining amount")

            # Generate Receipt Number
            org_repo = OrganizerRepository(self.conn)
            org = await org_repo.get_organizer_by_id(organizer_id)
            if not org:
                raise HTTPException(status_code=404, detail="Organizer not found")

            now = datetime.utcnow()
            year_month = now.strftime("%Y%m")
            prefix = f"CF-{org.organizer_code}-{year_month}"

            seq_repo = PaymentReceiptSequenceRepository(self.conn)
            seq_num = await seq_repo.get_next_sequence(organizer_id, prefix)
            receipt_number = f"{prefix}-{str(seq_num).zfill(6)}"

            # Create Receipt
            receipt_data = {
                "organizer_id": organizer_id,
                "chit_group_id": due["chit_group_id"],
                "chit_auction_id": due["chit_auction_id"],
                "monthly_member_due_id": due_id,
                "membership_id": due["membership_id"],
                "member_id": due["member_id"],
                "receipt_number": receipt_number,
                "payment_date": request.payment_date,
                "payment_amount": Decimal(str(request.payment_amount)),
                "payment_method": request.payment_method,
                "transaction_reference": request.transaction_reference,
                "remarks": request.remarks,
                "client_request_id": request.client_request_id
            }

            receipt = await receipt_repo.create_receipt(receipt_data, user_id)

            # Update Due balance
            total_paid = due["total_paid_amount"] + Decimal(str(request.payment_amount))
            remaining = due["remaining_amount"] - Decimal(str(request.payment_amount))
            status = "PAID" if remaining <= 0 else "PARTIALLY_PAID"

            updated_due = await due_repo.update_due_payment(
                due_id, organizer_id, total_paid, remaining, status, now, user_id
            )

            return {"message": "Payment collected successfully", "receipt": dict(receipt), "due": dict(updated_due)}

    async def get_payment_history(self, due_id: UUID, organizer_id: UUID) -> List[dict]:
        receipt_repo = ChitPaymentReceiptRepository(self.conn)
        return await receipt_repo.list_receipts_by_due(due_id, organizer_id)

    async def reverse_payment(self, receipt_id: UUID, organizer_id: UUID, user_id: UUID, request: PaymentReversalRequest) -> dict:
        async with self.conn.transaction():
            receipt_repo = ChitPaymentReceiptRepository(self.conn)
            receipt = await receipt_repo.get_receipt_for_update(receipt_id, organizer_id)

            if not receipt:
                raise HTTPException(status_code=404, detail="Receipt not found")

            if receipt["status"] != "SUCCESS":
                raise HTTPException(status_code=400, detail=f"Cannot reverse a receipt with status {receipt['status']}")

            due_repo = MonthlyMemberDueRepository(self.conn)
            due = await due_repo.get_due_for_update(receipt["monthly_member_due_id"], organizer_id)

            if not due:
                raise HTTPException(status_code=404, detail="Due not found")

            reversed_receipt = await receipt_repo.reverse_receipt(receipt_id, organizer_id, request.reversal_reason, user_id)

            total_paid = due["total_paid_amount"] - receipt["payment_amount"]
            remaining = due["remaining_amount"] + receipt["payment_amount"]
            status = "PENDING" if total_paid <= 0 else "PARTIALLY_PAID"

            updated_due = await due_repo.update_due_payment(
                due["id"], organizer_id, total_paid, remaining, status, datetime.utcnow(), user_id
            )

            return {"message": "Payment reversed successfully", "receipt": dict(reversed_receipt), "due": dict(updated_due)}

    async def get_member_passbook(self, member_id: UUID, organizer_id: UUID) -> dict:
        due_repo = MonthlyMemberDueRepository(self.conn)
        receipt_repo = ChitPaymentReceiptRepository(self.conn)

        dues = await due_repo.get_member_passbook_dues(member_id, organizer_id)

        entries = []
        for d in dues:
            receipts = await receipt_repo.list_receipts_by_due(d["id"], organizer_id)
            entries.append({
                "chit_name": d["chit_name"],
                "month_number": d["auction_month_number"],
                "auction_date": str(d["auction_date"]),
                "share_count": d["share_count"],
                "gross_installment": str(d["gross_installment_amount"]),
                "total_bonus": str(d["total_bonus_amount"]),
                "net_payable": str(d["net_payable_amount"]),
                "total_paid": str(d["total_paid_amount"]),
                "remaining": str(d["remaining_amount"]),
                "payment_status": d["payment_status"],
                "receipt_numbers": [r["receipt_number"] for r in receipts if r["status"] == "SUCCESS"]
            })

        return {
            "member_id": str(member_id),
            "member_name": "Member",
            "entries": entries
        }
