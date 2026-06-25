import asyncpg
from uuid import UUID
from fastapi import Request
from fastapi.responses import HTMLResponse
import os
from jinja2 import Template

from src.api.models.models import User
from src.shared.core.services.winner_payout_service import WinnerPayoutService
from src.shared.core.services.chit_financial_closure_service import ChitFinancialClosureService
from src.shared.core.repository.organizer_repository import OrganizerRepository
from pydantic import BaseModel

from src.api.schemas.winner_payout_schema import (
    WinnerPayoutCreateRequest,
    WinnerPayoutUpdateRequest,
    WinnerPayoutInitiatePaymentRequest,
    WinnerPayoutMarkPaidRequest,
    WinnerPayoutConfirmReceivedRequest,
    WinnerPayoutCancelRequest,
    WinnerPayoutReverseRequest
)

class CloseMonthRequest(BaseModel):
    remarks: str = None

class WinnerPayoutController:
    def __init__(self, db_object: asyncpg.Connection):
        self.db = db_object
        self.payout_service = WinnerPayoutService(db_object)
        self.closure_service = ChitFinancialClosureService(db_object)

    async def create_draft(self, current_user: User, request: WinnerPayoutCreateRequest):
        return await self.payout_service.create_draft(current_user, request)

    async def list_payouts(self, current_user: User, limit: int = 50, offset: int = 0):
        payouts = await self.payout_service.list_payouts(current_user, limit, offset)
        return {"items": payouts, "total": len(payouts)}

    async def get_payout(self, current_user: User, payout_id: UUID):
        return await self.payout_service.get_payout(current_user, payout_id)

    async def update_draft(self, current_user: User, payout_id: UUID, request: WinnerPayoutUpdateRequest):
        return await self.payout_service.update_draft(current_user, payout_id, request)

    async def initiate_payment(self, current_user: User, payout_id: UUID, request: WinnerPayoutInitiatePaymentRequest):
        return await self.payout_service.initiate_payment(current_user, payout_id, request)

    async def mark_paid(self, req: Request, current_user: User, payout_id: UUID, request: WinnerPayoutMarkPaidRequest):
        base_url = str(req.base_url).rstrip("/")
        return await self.payout_service.mark_paid(current_user, payout_id, request, base_url)

    async def share_receipt(self, req: Request, current_user: User, payout_id: UUID):
        base_url = str(req.base_url).rstrip("/")
        return await self.payout_service.share_receipt(current_user, payout_id, base_url)

    async def confirm_received(self, current_user: User, payout_id: UUID, request: WinnerPayoutConfirmReceivedRequest):
        return await self.payout_service.confirm_received(current_user, payout_id, request)

    async def cancel_payout(self, current_user: User, payout_id: UUID, request: WinnerPayoutCancelRequest):
        return await self.payout_service.cancel_payout(current_user, payout_id, request)

    async def reverse_payout(self, current_user: User, payout_id: UUID, request: WinnerPayoutReverseRequest):
        return await self.payout_service.reverse_payout(current_user, payout_id, request)

    async def get_receipt(self, payout_id: UUID):
        payout = await self.payout_service.get_payout_public(payout_id)
        org_repo = OrganizerRepository(self.db)
        org = await org_repo.get_organizer_by_id(payout["organizer_id"])
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        html_path = os.path.join(base_dir, "shared", "templates", "receipts", "winner_payout_receipt.html")
        css_path = os.path.join(base_dir, "shared", "templates", "receipts", "winner_payout_receipt.css")
        
        with open(html_path, "r") as f:
            html_content = f.read()
        with open(css_path, "r") as f:
            css_content = f.read()
            
        template = Template(html_content)
        rendered = template.render(
            payout=payout,
            organizer=org,
            css_content=css_content
        )
        return HTMLResponse(content=rendered, status_code=200)

    async def close_month(self, current_user: User, chit_group_id: UUID, month_number: int, request: CloseMonthRequest):
        return await self.closure_service.close_month(current_user, chit_group_id, month_number, request.remarks)

    async def get_financial_summary(self, current_user: User, chit_group_id: UUID):
        return await self.closure_service.get_financial_summary(current_user, chit_group_id)
