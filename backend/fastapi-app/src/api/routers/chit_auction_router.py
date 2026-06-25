import asyncpg
from fastapi import APIRouter, Depends, Path as FastAPIPath
from uuid import UUID
from typing import List

from src.api.schemas.chit_auction_schema import (
    CreateAuctionRequest, SubmitBidRequest,
    AuctionResponse, AuctionDetailResponse, AuctionListResponse,
    BidResponse, MonthlyDueResponse,
)
from src.api.controllers.chit_auction_controller import ChitAuctionController
from src.shared.core.database import get_db_session
from src.api.dependencies.auth_dependency import get_current_organizer, get_current_user
from src.api.dependencies.auth_decorator import authorize
from src.api.models.models import User

router = APIRouter(tags=["chit-auctions"])


# ─── Auction endpoints scoped under a chit group ─────────────────────────────

@router.post("/api/v1/chit-groups/{chit_group_id}/auctions", status_code=201)
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def create_auction(
    chit_group_id: UUID = FastAPIPath(...),
    request: CreateAuctionRequest = ...,
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session),
):
    controller = ChitAuctionController(db)
    return await controller.create_auction(current_user, chit_group_id, request)


@router.get("/api/v1/chit-groups/{chit_group_id}/auctions")
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def list_auctions(
    chit_group_id: UUID = FastAPIPath(...),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session),
):
    controller = ChitAuctionController(db)
    return await controller.list_auctions(current_user, chit_group_id)


# ─── Auction-level endpoints ──────────────────────────────────────────────────

@router.get("/api/v1/chit-auctions/{auction_id}")
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def get_auction_detail(
    auction_id: UUID = FastAPIPath(...),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session),
):
    controller = ChitAuctionController(db)
    return await controller.get_auction_detail(current_user, auction_id)


@router.post("/api/v1/chit-auctions/{auction_id}/bids", status_code=201)
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def submit_bid(
    auction_id: UUID = FastAPIPath(...),
    request: SubmitBidRequest = ...,
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session),
):
    controller = ChitAuctionController(db)
    return await controller.submit_bid(current_user, auction_id, request)


@router.post("/api/v1/chit-auctions/{auction_id}/finalize", status_code=200)
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def finalize_auction(
    auction_id: UUID = FastAPIPath(...),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session),
):
    controller = ChitAuctionController(db)
    return await controller.finalize_auction(current_user, auction_id)


@router.get("/api/v1/chit-auctions/{auction_id}/dues")
@authorize(allowed_roles=["ORGANIZER", "ADMIN"])
async def list_dues(
    auction_id: UUID = FastAPIPath(...),
    current_user: User = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db_session),
):
    controller = ChitAuctionController(db)
    return await controller.list_dues(current_user, auction_id)
