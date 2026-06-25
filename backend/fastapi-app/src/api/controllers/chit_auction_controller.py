import asyncpg
from uuid import UUID
from src.shared.core.services.chit_auction_service import ChitAuctionService
from src.api.schemas.chit_auction_schema import CreateAuctionRequest, SubmitBidRequest
from src.api.models.models import User


class ChitAuctionController:
    def __init__(self, db_object: asyncpg.Connection):
        self.service = ChitAuctionService(db_object)

    async def create_auction(self, current_user: User, chit_group_id: UUID, request: CreateAuctionRequest):
        return await self.service.create_auction(current_user, chit_group_id, request)

    async def list_auctions(self, current_user: User, chit_group_id: UUID):
        return await self.service.list_auctions(current_user, chit_group_id)

    async def get_auction_detail(self, current_user: User, auction_id: UUID):
        return await self.service.get_auction_detail(current_user, auction_id)

    async def submit_bid(self, current_user: User, auction_id: UUID, request: SubmitBidRequest):
        return await self.service.submit_bid(current_user, auction_id, request)

    async def finalize_auction(self, current_user: User, auction_id: UUID):
        return await self.service.finalize_auction(current_user, auction_id)

    async def list_dues(self, current_user: User, auction_id: UUID):
        return await self.service.list_dues(current_user, auction_id)
