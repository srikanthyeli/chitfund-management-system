from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from fastapi import HTTPException
from typing import Optional, List, Dict, Any

from src.shared.core.repository.chit_group_repository import ChitGroupRepository
from src.shared.core.repository.chit_membership_repository import ChitMembershipRepository
from src.shared.core.repository.chit_group_activity_log_repository import ChitGroupActivityLogRepository
from src.shared.core.repository.member_repository import MemberRepository

from src.api.models.models import User, ChitGroup, ChitMembership
from src.api.schemas.chit_group_schema import (
    ChitGroupCreateRequest, ChitGroupUpdateRequest,
    ChitMembershipCreateRequest, ChitMembershipUpdateRequest,
    ChitStatusChangeRequest
)

class ChitGroupService:
    def __init__(self, db_object):
        self.db = db_object
        self.chit_repo = ChitGroupRepository(db_object)
        self.membership_repo = ChitMembershipRepository(db_object)
        self.activity_repo = ChitGroupActivityLogRepository(db_object)
        self.member_repo = MemberRepository(db_object)

    async def create_chit_group(self, current_user: User, request: ChitGroupCreateRequest) -> ChitGroup:
        if current_user.role != "ORGANIZER" or not current_user.organizer_id:
            raise HTTPException(status_code=403, detail="Only organizers can create chit groups")

        organizer_id = current_user.organizer_id

        # Validate unique chit name within organizer scope
        existing = await self.chit_repo.get_chit_group_by_name_and_organizer(request.chit_name, organizer_id)
        if existing:
            raise HTTPException(status_code=409, detail="A chit group with this name already exists")

        # Prepare create data
        data = request.dict()
        data["organizer_id"] = organizer_id

        async with self.db.transaction():
            chit = await self.chit_repo.create_chit_group(data, current_user.id)
            
            # Log CHIT_CREATED
            await self.activity_repo.create_log(
                organizer_id=organizer_id,
                chit_group_id=chit.id,
                action_type="CHIT_CREATED",
                new_values={
                    "chit_name": chit.chit_name,
                    "chit_code": chit.chit_code,
                    "total_chit_value": str(chit.total_chit_value),
                    "monthly_installment_per_share": str(chit.monthly_installment_per_share),
                    "total_shares": chit.total_shares,
                    "duration_months": chit.duration_months,
                    "maintenance_charge": str(chit.maintenance_charge),
                    "maintenance_charge_type": chit.maintenance_charge_type,
                    "start_date": str(chit.start_date),
                    "installment_due_day": chit.installment_due_day,
                },
                remarks="Chit group created in DRAFT status",
                performed_by_user_id=current_user.id
            )
        return chit

    async def list_chit_groups(
        self,
        current_user: User,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        status: Optional[str] = None,
        start_date_from: Optional[date] = None,
        start_date_to: Optional[date] = None,
        sort_by: str = 'start_date',
        sort_order: str = 'desc'
    ):
        if current_user.role != "ORGANIZER" or not current_user.organizer_id:
            raise HTTPException(status_code=403, detail="Only organizers can view chit groups list")

        organizer_id = current_user.organizer_id
        
        if page_size > 100:
            page_size = 100
        if page_size < 1:
            page_size = 20
        if page < 1:
            page = 1

        skip = (page - 1) * page_size
        
        items, total = await self.chit_repo.list_chit_groups(
            organizer_id=organizer_id,
            skip=skip,
            limit=page_size,
            search=search,
            status=status,
            start_date_from=start_date_from,
            start_date_to=start_date_to,
            sort_by=sort_by,
            sort_order=sort_order
        )

        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages
        }

    async def get_chit_group_detail(self, current_user: User, chit_group_id: UUID) -> dict:
        if current_user.role != "ORGANIZER" or not current_user.organizer_id:
            raise HTTPException(status_code=403, detail="Only organizers can view chit group details")

        organizer_id = current_user.organizer_id
        
        chit = await self.chit_repo.get_chit_group_by_id_and_organizer(chit_group_id, organizer_id)
        if not chit:
            raise HTTPException(status_code=404, detail="Chit group not found")

        memberships_raw = await self.membership_repo.list_memberships_by_chit_group(chit_group_id, organizer_id)

        memberships_mapped = []
        for m in memberships_raw:
            memberships_mapped.append({
                "membership_id": m["membership_id"],
                "member_id": m["member_id"],
                "member_code": m["member_code"],
                "full_name": m["full_name"],
                "mobile": m["mobile"],
                "village": m["village"],
                "share_count": m["share_count"],
                "membership_status": m["membership_status"]
            })

        monthly_pool = chit.monthly_installment_per_share * chit.total_shares
        member_count = len(memberships_mapped)

        return {
            "id": chit.id,
            "organizer_id": chit.organizer_id,
            "chit_code": chit.chit_code,
            "chit_name": chit.chit_name,
            "description": chit.description,
            "total_chit_value": chit.total_chit_value,
            "monthly_installment_per_share": chit.monthly_installment_per_share,
            "total_shares": chit.total_shares,
            "duration_months": chit.duration_months,
            "maintenance_charge": chit.maintenance_charge,
            "maintenance_charge_type": chit.maintenance_charge_type,
            "start_date": chit.start_date,
            "installment_due_day": chit.installment_due_day,
            "status": chit.status,
            "allocated_shares": chit.allocated_shares,
            "available_shares": chit.available_shares,
            "member_count": member_count,
            "monthly_pool": monthly_pool,
            "memberships": memberships_mapped,
            "created_at": chit.created_at,
            "updated_at": chit.updated_at
        }

    async def update_chit_group(self, current_user: User, chit_group_id: UUID, request: ChitGroupUpdateRequest) -> ChitGroup:
        if current_user.role != "ORGANIZER" or not current_user.organizer_id:
            raise HTTPException(status_code=403, detail="Only organizers can update chit groups")

        organizer_id = current_user.organizer_id

        chit = await self.chit_repo.get_chit_group_by_id_and_organizer(chit_group_id, organizer_id)
        if not chit:
            raise HTTPException(status_code=404, detail="Chit group not found")

        if chit.status != "DRAFT":
            raise HTTPException(status_code=400, detail="Chit group can only be updated in DRAFT status")

        update_data = request.dict(exclude_unset=True)
        if not update_data:
            return chit

        merged = {
            "total_shares": update_data.get("total_shares", chit.total_shares),
            "duration_months": update_data.get("duration_months", chit.duration_months),
            "total_chit_value": update_data.get("total_chit_value", chit.total_chit_value),
            "monthly_installment_per_share": update_data.get("monthly_installment_per_share", chit.monthly_installment_per_share),
            "maintenance_charge": update_data.get("maintenance_charge", chit.maintenance_charge),
            "maintenance_charge_type": update_data.get("maintenance_charge_type", chit.maintenance_charge_type),
        }

        if merged["total_shares"] < chit.allocated_shares:
            raise HTTPException(status_code=400, detail=f"Total shares cannot be reduced below currently allocated shares ({chit.allocated_shares})")

        if merged["duration_months"] != merged["total_shares"]:
            raise HTTPException(status_code=400, detail="Duration in months must equal total shares")

        expected_value = Decimal(str(merged["monthly_installment_per_share"])) * merged["total_shares"]
        if Decimal(str(merged["total_chit_value"])) != expected_value:
            raise HTTPException(status_code=400, detail="total_chit_value must equal monthly_installment_per_share * total_shares")

        if merged["maintenance_charge_type"] == 'PERCENTAGE':
            if merged["maintenance_charge"] < 0 or merged["maintenance_charge"] > 100:
                raise HTTPException(status_code=400, detail="Percentage maintenance charge must be between 0 and 100")

        new_total_shares = merged["total_shares"]
        update_data["available_shares"] = new_total_shares - chit.allocated_shares

        # Capture changes for activity logging
        old_values = {}
        new_values = {}
        for field, new_val in update_data.items():
            old_val = getattr(chit, field, None)
            if old_val != new_val:
                old_values[field] = str(old_val) if isinstance(old_val, (Decimal, date, datetime)) else old_val
                new_values[field] = str(new_val) if isinstance(new_val, (Decimal, date, datetime)) else new_val

        async with self.db.transaction():
            updated_chit = await self.chit_repo.update_chit_group(chit_group_id, organizer_id, update_data, current_user.id)
            
            # Log CHIT_UPDATED
            await self.activity_repo.create_log(
                organizer_id=organizer_id,
                chit_group_id=chit_group_id,
                action_type="CHIT_UPDATED",
                old_values=old_values,
                new_values=new_values,
                remarks="Chit group details updated",
                performed_by_user_id=current_user.id
            )

        return updated_chit

    async def allocate_member_shares(self, current_user: User, chit_group_id: UUID, request: ChitMembershipCreateRequest) -> ChitMembership:
        if current_user.role != "ORGANIZER" or not current_user.organizer_id:
            raise HTTPException(status_code=403, detail="Only organizers can allocate shares")

        organizer_id = current_user.organizer_id

        member = await self.member_repo.get_member_by_id_and_organizer(request.member_id, organizer_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        if not member.is_active:
            raise HTTPException(status_code=400, detail="Inactive members cannot be added to a chit")

        async with self.db.transaction():
            chit_lock = await self.membership_repo.lock_chit_group_for_share_update(chit_group_id)
            if not chit_lock:
                raise HTTPException(status_code=404, detail="Chit group not found")

            if chit_lock["status"] != "DRAFT":
                raise HTTPException(status_code=400, detail="Shares can only be allocated when the chit group is in DRAFT status")

            existing = await self.membership_repo.get_membership_by_chit_and_member(chit_group_id, request.member_id, organizer_id)
            if existing:
                raise HTTPException(
                    status_code=409, 
                    detail="This member is already part of this chit group. Please update their share count instead."
                )

            available_shares = chit_lock["available_shares"]
            if request.share_count > available_shares:
                raise HTTPException(status_code=409, detail="Requested shares exceed available shares")

            membership_data = request.dict()
            membership_data["organizer_id"] = organizer_id
            membership_data["chit_group_id"] = chit_group_id
            membership = await self.membership_repo.create_membership(membership_data, current_user.id)

            new_allocated = chit_lock["allocated_shares"] + request.share_count
            new_available = chit_lock["total_shares"] - new_allocated
            await self.chit_repo.update_share_counts(chit_group_id, organizer_id, new_allocated, new_available, current_user.id)

            await self.activity_repo.create_log(
                organizer_id=organizer_id,
                chit_group_id=chit_group_id,
                membership_id=membership.id,
                action_type="MEMBER_SHARE_ALLOCATED",
                new_values={
                    "member_id": str(request.member_id),
                    "share_count": request.share_count,
                    "remarks": request.remarks
                },
                remarks=f"Allocated {request.share_count} share(s) to member {member.full_name}",
                performed_by_user_id=current_user.id
            )

        return membership

    async def update_member_shares(self, current_user: User, chit_group_id: UUID, membership_id: UUID, request: ChitMembershipUpdateRequest) -> ChitMembership:
        if current_user.role != "ORGANIZER" or not current_user.organizer_id:
            raise HTTPException(status_code=403, detail="Only organizers can update shares")

        organizer_id = current_user.organizer_id

        async with self.db.transaction():
            chit_lock = await self.membership_repo.lock_chit_group_for_share_update(chit_group_id)
            if not chit_lock:
                raise HTTPException(status_code=404, detail="Chit group not found")

            if chit_lock["status"] != "DRAFT":
                raise HTTPException(status_code=400, detail="Shares can only be updated when the chit group is in DRAFT status")

            membership = await self.membership_repo.get_membership_by_id_and_organizer(membership_id, organizer_id)
            if not membership or membership.chit_group_id != chit_group_id:
                raise HTTPException(status_code=404, detail="Membership not found")

            old_share_count = membership.share_count
            diff = request.share_count - old_share_count

            if diff > 0 and diff > chit_lock["available_shares"]:
                raise HTTPException(status_code=409, detail="Requested shares exceed available shares")

            updated_membership = await self.membership_repo.update_membership_share_count(
                membership_id, organizer_id, request.share_count, request.remarks, current_user.id
            )

            new_allocated = chit_lock["allocated_shares"] + diff
            new_available = chit_lock["total_shares"] - new_allocated
            await self.chit_repo.update_share_counts(chit_group_id, organizer_id, new_allocated, new_available, current_user.id)

            member = await self.member_repo.get_member_by_id_and_organizer(membership.member_id, organizer_id)
            await self.activity_repo.create_log(
                organizer_id=organizer_id,
                chit_group_id=chit_group_id,
                membership_id=membership_id,
                action_type="MEMBER_SHARE_UPDATED",
                old_values={"share_count": old_share_count},
                new_values={"share_count": request.share_count},
                remarks=f"Updated share count from {old_share_count} to {request.share_count} for member {member.full_name if member else ''}",
                performed_by_user_id=current_user.id
            )

        return updated_membership

    async def remove_member_from_chit(self, current_user: User, chit_group_id: UUID, membership_id: UUID, remarks: Optional[str]):
        if current_user.role != "ORGANIZER" or not current_user.organizer_id:
            raise HTTPException(status_code=403, detail="Only organizers can remove members")

        organizer_id = current_user.organizer_id

        async with self.db.transaction():
            chit_lock = await self.membership_repo.lock_chit_group_for_share_update(chit_group_id)
            if not chit_lock:
                raise HTTPException(status_code=404, detail="Chit group not found")

            if chit_lock["status"] != "DRAFT":
                raise HTTPException(status_code=400, detail="Members can only be removed when the chit group is in DRAFT status")

            membership = await self.membership_repo.get_membership_by_id_and_organizer(membership_id, organizer_id)
            if not membership or membership.chit_group_id != chit_group_id:
                raise HTTPException(status_code=404, detail="Membership not found")

            removed_membership = await self.membership_repo.soft_remove_membership(membership_id, organizer_id, remarks, current_user.id)

            new_allocated = chit_lock["allocated_shares"] - membership.share_count
            new_available = chit_lock["total_shares"] - new_allocated
            await self.chit_repo.update_share_counts(chit_group_id, organizer_id, new_allocated, new_available, current_user.id)

            member = await self.member_repo.get_member_by_id_and_organizer(membership.member_id, organizer_id)
            await self.activity_repo.create_log(
                organizer_id=organizer_id,
                chit_group_id=chit_group_id,
                membership_id=membership_id,
                action_type="MEMBER_REMOVED",
                old_values={"status": "ACTIVE", "is_deleted": False},
                new_values={"status": "REMOVED", "is_deleted": True},
                remarks=remarks or f"Removed member {member.full_name if member else ''} from chit",
                performed_by_user_id=current_user.id
            )

        return removed_membership

    async def change_chit_status(self, current_user: User, chit_group_id: UUID, request: ChitStatusChangeRequest) -> ChitGroup:
        if current_user.role != "ORGANIZER" or not current_user.organizer_id:
            raise HTTPException(status_code=403, detail="Only organizers can change chit status")

        organizer_id = current_user.organizer_id
        new_status = request.status
        remarks = request.remarks

        allowed_statuses = {"DRAFT", "READY_TO_START", "ACTIVE", "CANCELLED"}
        if new_status not in allowed_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status: {new_status}")

        async with self.db.transaction():
            chit = await self.chit_repo.get_chit_group_by_id_and_organizer(chit_group_id, organizer_id)
            if not chit:
                raise HTTPException(status_code=404, detail="Chit group not found")

            old_status = chit.status
            if old_status == new_status:
                return chit

            # Status Transitions logic
            if old_status == "DRAFT" and new_status == "READY_TO_START":
                if chit.allocated_shares != chit.total_shares:
                    raise HTTPException(status_code=400, detail="Cannot mark chit as Ready to Start until all shares are allocated")
            
            elif old_status == "READY_TO_START" and new_status == "DRAFT":
                pass

            elif old_status == "READY_TO_START" and new_status == "ACTIVE":
                if chit.allocated_shares != chit.total_shares:
                    raise HTTPException(status_code=400, detail="Cannot activate chit group until all shares are allocated")

            elif old_status in ("DRAFT", "READY_TO_START") and new_status == "CANCELLED":
                if not remarks:
                    raise HTTPException(status_code=400, detail="Remarks are required to cancel a chit group")

            else:
                raise HTTPException(status_code=400, detail=f"Transition from {old_status} to {new_status} is not allowed")

            updated_chit = await self.chit_repo.update_chit_group_status(chit_group_id, organizer_id, new_status, current_user.id)

            action_map = {
                "READY_TO_START": "CHIT_READY_TO_START",
                "ACTIVE": "CHIT_ACTIVATED",
                "CANCELLED": "CHIT_CANCELLED",
                "DRAFT": "CHIT_STATUS_CHANGED"
            }
            action_type = action_map.get(new_status, "CHIT_STATUS_CHANGED")

            await self.activity_repo.create_log(
                organizer_id=organizer_id,
                chit_group_id=chit_group_id,
                action_type=action_type,
                old_values={"status": old_status},
                new_values={"status": new_status},
                remarks=remarks or f"Status changed from {old_status} to {new_status}",
                performed_by_user_id=current_user.id
            )

        return updated_chit

    async def get_chit_group_activity(self, current_user: User, chit_group_id: UUID, page: int = 1, page_size: int = 20):
        if current_user.role != "ORGANIZER" or not current_user.organizer_id:
            raise HTTPException(status_code=403, detail="Only organizers can view chit activity")

        organizer_id = current_user.organizer_id
        chit = await self.chit_repo.get_chit_group_by_id_and_organizer(chit_group_id, organizer_id)
        if not chit:
            raise HTTPException(status_code=404, detail="Chit group not found")

        skip = (page - 1) * page_size
        items, total = await self.activity_repo.get_chit_group_activity_logs(chit_group_id, organizer_id, skip, page_size)
        return items

    async def get_chit_group_summary(self, current_user: User) -> dict:
        if current_user.role != "ORGANIZER" or not current_user.organizer_id:
            raise HTTPException(status_code=403, detail="Only organizers can view summaries")

        return await self.chit_repo.get_chit_group_summary(current_user.organizer_id)

    async def get_available_members(self, current_user: User, chit_group_id: UUID) -> List[Any]:
        if current_user.role != "ORGANIZER" or not current_user.organizer_id:
            raise HTTPException(status_code=403, detail="Only organizers can view available members")

        organizer_id = current_user.organizer_id
        
        query = """
            SELECT 
                m.id, 
                m.member_code, 
                m.full_name, 
                m.mobile, 
                m.village, 
                m.is_active,
                COALESCE(cm.share_count, 0) as existing_shares
            FROM members m
            LEFT JOIN chit_memberships cm ON cm.member_id = m.id 
                AND cm.chit_group_id = $2 
                AND cm.status = 'ACTIVE' 
                AND cm.is_deleted = FALSE
            WHERE m.organizer_id = $1 
              AND m.is_active = TRUE 
              AND m.is_deleted = FALSE
            ORDER BY m.full_name ASC
        """
        rows = await self.db.fetch(query, organizer_id, chit_group_id)
        return [dict(row) for row in rows]








