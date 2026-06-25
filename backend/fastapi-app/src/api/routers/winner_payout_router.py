import asyncpg
from fastapi import APIRouter, Depends, Path as FastAPIPath, Request
from uuid import UUID

from src.api.controllers.winner_payout_controller import WinnerPayoutController, CloseMonthRequest
from src.api.schemas.winner_payout_schema import (
    WinnerPayoutCreateRequest,
    WinnerPayoutUpdateRequest,
    WinnerPayoutInitiatePaymentRequest,
    WinnerPayoutMarkPaidRequest,
    WinnerPayoutConfirmReceivedRequest,
    WinnerPayoutCancelRequest,
    WinnerPayoutReverseRequest
)
from src.shared.core.database import get_db_session
from src.api.dependencies.auth_dependency import get_current_user
from src.api.dependencies.auth_decorator import authorize
from src.api.models.models import User

router = APIRouter(prefix="/api/v1", tags=["Winner Payout & Financial Closure"])

# --- Phase 6.1 Winner Payout Endpoints ---

@router.post("/winner-payouts")
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def create_payout_draft(
    request: WinnerPayoutCreateRequest,
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = WinnerPayoutController(db)
    return await controller.create_draft(current_user, request)

@router.get("/winner-payouts")
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def list_payouts(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = WinnerPayoutController(db)
    return await controller.list_payouts(current_user, limit, offset)

@router.get("/winner-payouts/{payout_id}")
@authorize(allowed_roles=["ORGANIZER", "ADMIN", "MEMBER"])
async def get_payout(
    payout_id: UUID = FastAPIPath(...),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = WinnerPayoutController(db)
    return await controller.get_payout(current_user, payout_id)

@router.get("/winner-payouts/{payout_id}/receipt")
async def get_receipt(
    payout_id: UUID = FastAPIPath(...),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = WinnerPayoutController(db)
    return await controller.get_receipt(payout_id)

@router.put("/winner-payouts/{payout_id}")
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def update_payout_draft(
    request: WinnerPayoutUpdateRequest,
    payout_id: UUID = FastAPIPath(...),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = WinnerPayoutController(db)
    return await controller.update_draft(current_user, payout_id, request)

@router.post("/winner-payouts/{payout_id}/initiate-payment")
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def initiate_payment(
    request: WinnerPayoutInitiatePaymentRequest,
    payout_id: UUID = FastAPIPath(...),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = WinnerPayoutController(db)
    return await controller.initiate_payment(current_user, payout_id, request)

@router.post("/winner-payouts/{payout_id}/mark-paid")
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def mark_paid(
    req: Request,
    request: WinnerPayoutMarkPaidRequest,
    payout_id: UUID = FastAPIPath(...),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = WinnerPayoutController(db)
    return await controller.mark_paid(req, current_user, payout_id, request)

@router.post("/winner-payouts/{payout_id}/share")
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def share_receipt(
    req: Request,
    payout_id: UUID = FastAPIPath(...),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = WinnerPayoutController(db)
    return await controller.share_receipt(req, current_user, payout_id)

@router.post("/winner-payouts/{payout_id}/confirm-received")
@authorize(allowed_roles=["MEMBER", "ORGANIZER"]) # Organizer included for testing MVP
async def confirm_received(
    request: WinnerPayoutConfirmReceivedRequest,
    payout_id: UUID = FastAPIPath(...),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = WinnerPayoutController(db)
    return await controller.confirm_received(current_user, payout_id, request)

@router.post("/winner-payouts/{payout_id}/cancel")
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def cancel_payout(
    request: WinnerPayoutCancelRequest,
    payout_id: UUID = FastAPIPath(...),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = WinnerPayoutController(db)
    return await controller.cancel_payout(current_user, payout_id, request)

@router.post("/winner-payouts/{payout_id}/reverse")
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def reverse_payout(
    request: WinnerPayoutReverseRequest,
    payout_id: UUID = FastAPIPath(...),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = WinnerPayoutController(db)
    return await controller.reverse_payout(current_user, payout_id, request)


# --- Existing Financial Closure Endpoints ---

@router.post("/chit-groups/{chit_group_id}/months/{month_number}/financial-close")
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def close_month(
    request: CloseMonthRequest,
    chit_group_id: UUID = FastAPIPath(...),
    month_number: int = FastAPIPath(...),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = WinnerPayoutController(db)
    return await controller.close_month(current_user, chit_group_id, month_number, request)

@router.get("/chit-groups/{chit_group_id}/financial-summary")
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def get_financial_summary(
    chit_group_id: UUID = FastAPIPath(...),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = WinnerPayoutController(db)
    return await controller.get_financial_summary(current_user, chit_group_id)
