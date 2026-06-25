from uuid import UUID
from fastapi import HTTPException
from typing import Optional, List, Dict, Any

from src.shared.core.repository.chit_group_repository import ChitGroupRepository
from src.shared.core.repository.chit_membership_repository import ChitMembershipRepository
from src.shared.core.repository.chit_group_activity_log_repository import ChitGroupActivityLogRepository
from src.shared.core.repository.member_repository import MemberRepository

from src.api.models.models import User, ChitGroup, ChitMembership
from src.api.schemas.chit_group_schema import BulkMembershipAllocateRequest

class ChitMembershipService:
    def __init__(self, db_object):
        self.db = db_object
        self.chit_repo = ChitGroupRepository(db_object)
        self.membership_repo = ChitMembershipRepository(db_object)
        self.activity_repo = ChitGroupActivityLogRepository(db_object)
        self.member_repo = MemberRepository(db_object)

    async def bulk_allocate_equal_shares(
        self,
        db,
        chit_group_id: UUID,
        request: BulkMembershipAllocateRequest,
        current_user: User
    ) -> dict:
        if current_user.role != "ORGANIZER" or not current_user.organizer_id:
            raise HTTPException(status_code=403, detail="Only organizers can allocate shares")

        organizer_id = current_user.organizer_id

        # At least one member must be selected
        if not request.member_ids:
            raise HTTPException(status_code=400, detail="At least one member must be selected")

        # De-duplicate member_ids
        unique_member_ids = list(dict.fromkeys(request.member_ids))

        # Start atomic transaction
        async with self.db.transaction():
            # Lock the chit group row
            chit_group = await self.membership_repo.get_chit_group_for_update(chit_group_id)
            if not chit_group:
                raise HTTPException(status_code=404, detail="Chit group not found")

            # Validate organizer ownership
            if chit_group.organizer_id != organizer_id:
                raise HTTPException(status_code=403, detail="Only the owner organizer can allocate members")

            # Validate chit status
            if chit_group.status in ("COMPLETED", "CANCELLED", "CLOSED"):
                raise HTTPException(status_code=409, detail=f"Cannot allocate shares when chit group is in {chit_group.status} status")
            if chit_group.status != "DRAFT":
                raise HTTPException(status_code=409, detail="Shares can only be allocated when the chit group is in DRAFT status")

            # Fetch selected members in one query
            members = await self.member_repo.get_members_by_ids_and_organizer(unique_member_ids, organizer_id)
            found_member_ids = {m.id for m in members}

            # If any member id in request is not found or belongs to another organizer
            if len(found_member_ids) < len(unique_member_ids):
                raise HTTPException(status_code=404, detail="One or more members not found")

            # Validate all selected members are ACTIVE
            for m in members:
                if not m.is_active:
                    raise HTTPException(status_code=400, detail=f"Member {m.full_name} is inactive and cannot be allocated shares")

            # Fetch existing memberships for selected members with row locks
            existing_memberships = await self.membership_repo.get_existing_memberships_for_update(chit_group_id, unique_member_ids)
            existing_map = {m.member_id: m for m in existing_memberships}

            # Calculate current allocated shares
            current_allocated_shares = await self.membership_repo.get_total_allocated_shares(chit_group_id)

            # Calculate requested shares
            requested_shares = len(unique_member_ids) * request.share_count_per_member
            available_shares = chit_group.total_shares - current_allocated_shares

            # Validate requested shares <= available shares
            if requested_shares > available_shares:
                raise HTTPException(status_code=409, detail=f"Requested shares ({requested_shares}) exceed available shares ({available_shares})")

            # Partition into created vs updated memberships
            new_memberships_data = []
            existing_membership_ids_to_update = []

            for member_id in unique_member_ids:
                if member_id in existing_map:
                    existing_membership_ids_to_update.append(existing_map[member_id].id)
                else:
                    new_memberships_data.append({
                        "organizer_id": organizer_id,
                        "chit_group_id": chit_group_id,
                        "member_id": member_id,
                        "share_count": request.share_count_per_member,
                        "remarks": request.remarks
                    })

            # Bulk insert new memberships
            created_memberships = []
            if new_memberships_data:
                created_memberships = await self.membership_repo.bulk_create_memberships(new_memberships_data, current_user.id)

            # Bulk update existing memberships
            updated_memberships = []
            if existing_membership_ids_to_update:
                updated_memberships = await self.membership_repo.bulk_increment_membership_shares(
                    existing_membership_ids_to_update,
                    organizer_id,
                    request.share_count_per_member,
                    request.remarks,
                    current_user.id
                )

            # Update chit group share counts
            new_allocated = current_allocated_shares + requested_shares
            new_available = chit_group.total_shares - new_allocated
            await self.chit_repo.update_share_counts(
                chit_group_id,
                organizer_id,
                new_allocated,
                new_available,
                current_user.id
            )

            # Create bulk activity log
            await self.activity_repo.create_log(
                organizer_id=organizer_id,
                chit_group_id=chit_group_id,
                action_type="BULK_MEMBERS_ALLOCATED",
                new_values={
                    "member_ids": [str(m_id) for m_id in unique_member_ids],
                    "share_count_per_member": request.share_count_per_member,
                    "shares_added": requested_shares,
                    "created_membership_count": len(created_memberships),
                    "updated_membership_count": len(updated_memberships),
                    "total_allocated_shares_after": new_allocated,
                    "available_shares_after": new_available
                },
                remarks=f"Bulk allocated {request.share_count_per_member} shares each to {len(unique_member_ids)} members (Total: {requested_shares} shares added)",
                performed_by_user_id=current_user.id
            )

        return {
            "message": "Members allocated successfully",
            "chit_group_id": chit_group_id,
            "selected_member_count": len(unique_member_ids),
            "share_count_per_member": request.share_count_per_member,
            "shares_added": requested_shares,
            "total_allocated_shares": new_allocated,
            "available_shares": new_available,
            "created_membership_count": len(created_memberships),
            "updated_membership_count": len(updated_memberships),
            "memberships": created_memberships + updated_memberships
        }
