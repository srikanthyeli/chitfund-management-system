import asyncpg
from fastapi import APIRouter, Depends, Path as FastAPIPath
from uuid import UUID
from typing import List

from src.api.controllers.chit_collection_controller import ChitCollectionController
from src.api.schemas.chit_collection_schema import (
    CollectionSummaryResponse, PaymentCollectionRequest, 
    PaymentReceiptResponse, PaymentReversalRequest, MemberPassbookResponse
)
from src.shared.core.database import get_db_session
from src.api.dependencies.auth_dependency import get_current_user
from src.api.dependencies.auth_decorator import authorize
from src.api.models.models import User

router = APIRouter(prefix="/api/v1", tags=["Collections"])

@router.get("/collections/active")
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def get_active_collections(
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ChitCollectionController(db)
    return await controller.get_active_collections(current_user)

@router.get("/chit-groups/{chit_group_id}/auctions/{auction_id}/collections", response_model=CollectionSummaryResponse)
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def get_collection_summary(
    chit_group_id: UUID = FastAPIPath(...),
    auction_id: UUID = FastAPIPath(...),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ChitCollectionController(db)
    return await controller.get_collection_summary(current_user, chit_group_id, auction_id)

@router.post("/monthly-member-dues/{due_id}/payments")
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def collect_payment(
    request: PaymentCollectionRequest,
    due_id: UUID = FastAPIPath(...),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ChitCollectionController(db)
    return await controller.collect_payment(current_user, due_id, request)

@router.get("/monthly-member-dues/{due_id}/payments")
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def get_payment_history(
    due_id: UUID = FastAPIPath(...),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ChitCollectionController(db)
    return await controller.get_payment_history(current_user, due_id)

@router.post("/chit-payment-receipts/{receipt_id}/reverse")
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def reverse_payment(
    request: PaymentReversalRequest,
    receipt_id: UUID = FastAPIPath(...),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ChitCollectionController(db)
    return await controller.reverse_payment(current_user, receipt_id, request)

@router.get("/members/{member_id}/passbook", response_model=MemberPassbookResponse)
@authorize(allowed_roles=["ORGANIZER", "ADMIN", "MEMBER"])
async def get_member_passbook(
    member_id: UUID = FastAPIPath(...),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session)
):
    controller = ChitCollectionController(db)
    return await controller.get_member_passbook(current_user, member_id)
