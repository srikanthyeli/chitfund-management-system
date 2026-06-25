import asyncpg
from uuid import UUID
from src.api.models.models import User
from src.api.schemas.chit_collection_schema import (
    CollectionSummaryResponse, PaymentCollectionRequest, 
    PaymentReversalRequest
)
from src.shared.core.services.chit_collection_service import ChitCollectionService

class ChitCollectionController:
    def __init__(self, db_object: asyncpg.Connection):
        self.db_object = db_object
        self.service = ChitCollectionService(db_object)

    async def get_active_collections(self, current_user: User):
        return await self.service.get_active_collections(current_user.organizer_id)

    async def get_collection_summary(self, current_user: User, chit_group_id: UUID, auction_id: UUID):
        result = await self.service.get_collection_summary(current_user.organizer_id, auction_id)
        return CollectionSummaryResponse(
            summary=result["summary"],
            dues=result["dues"]
        )

    async def collect_payment(self, current_user: User, due_id: UUID, request: PaymentCollectionRequest):
        return await self.service.collect_payment(due_id, current_user.organizer_id, current_user.id, request)

    async def get_payment_history(self, current_user: User, due_id: UUID):
        return await self.service.get_payment_history(due_id, current_user.organizer_id)

    async def reverse_payment(self, current_user: User, receipt_id: UUID, request: PaymentReversalRequest):
        return await self.service.reverse_payment(receipt_id, current_user.organizer_id, current_user.id, request)

    async def get_member_passbook(self, current_user: User, member_id: UUID):
        return await self.service.get_member_passbook(member_id, current_user.organizer_id)
