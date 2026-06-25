import re
from uuid import UUID
from fastapi import HTTPException
from typing import Optional

from src.shared.core.repository.member_repository import MemberRepository
from src.shared.core.repository.member_activity_log_repository import MemberActivityLogRepository
from src.shared.core.repository.user_repository import UserRepository
from src.shared.common.helpers.password_helper import hash_password
from src.api.models.models import User
from src.api.schemas.member_schema import (
    MemberCreateRequest, MemberUpdateRequest, MemberStatusRequest, MemberMobileUpdateRequest
)

def normalize_and_validate_indian_mobile(mobile: str) -> str:
    if not mobile:
        raise HTTPException(status_code=400, detail="Mobile number is required")
    # Strip whitespace, dashes, parentheses
    cleaned = re.sub(r'[\s\-()]', '', mobile)
    # Validate format: matches optional +91/91/0 followed by 10 digits starting with 6-9
    match = re.match(r'^(?:\+91|91|0)?([6-9]\d{9})$', cleaned)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid Indian mobile number format")
    return match.group(1)

class MemberService:
    def __init__(self, db_object):
        self.db = db_object
        self.member_repo = MemberRepository(db_object)
        self.activity_repo = MemberActivityLogRepository(db_object)
        self.user_repo = UserRepository(db_object)

    async def create_member(self, current_user: User, request: MemberCreateRequest):
        if current_user.role != "ORGANIZER" or not current_user.organizer_id:
            raise HTTPException(status_code=403, detail="Only organizers can create members")

        organizer_id = current_user.organizer_id
        
        # Normalize and validate mobile
        normalized_mobile = normalize_and_validate_indian_mobile(request.mobile)
        
        # Normalize alternate mobile if provided
        normalized_alt_mobile = None
        if request.alternate_mobile:
            normalized_alt_mobile = normalize_and_validate_indian_mobile(request.alternate_mobile)

        # Validate Aadhaar last 4
        if request.aadhaar_last4 and not re.match(r'^\d{4}$', request.aadhaar_last4):
            raise HTTPException(status_code=400, detail="Aadhaar last 4 must be exactly 4 digits")

        # Check duplicate mobile inside organizer scope
        existing = await self.member_repo.get_member_by_mobile_and_organizer(normalized_mobile, organizer_id)
        if existing:
            raise HTTPException(status_code=409, detail="A member with this mobile number already exists")

        # Prepare create dict
        member_data = request.dict()
        member_data["mobile"] = normalized_mobile
        member_data["alternate_mobile"] = normalized_alt_mobile
        member_data["organizer_id"] = organizer_id

        # Use transaction to ensure code generation is safe against race conditions
        async with self.db.transaction():
            member = await self.member_repo.create_member(member_data, current_user.id)
            
            # Log MEMBER_CREATED
            new_log_values = {
                "full_name": member.full_name,
                "mobile": member.mobile,
                "email": member.email,
                "address": member.address,
                "village": member.village,
                "mandal": member.mandal,
                "district": member.district,
                "state": member.state,
                "pincode": member.pincode,
                "aadhaar_last4": member.aadhaar_last4,
                "notes": member.notes
            }
            await self.activity_repo.create_log(
                organizer_id=organizer_id,
                member_id=member.id,
                action_type="MEMBER_CREATED",
                old_values=None,
                new_values=new_log_values,
                remarks="Member registered",
                performed_by=current_user.id
            )
            
            # Auto-provision User account for Member
            hashed_pw = hash_password("Member@123")
            user_data = {
                "organizer_id": organizer_id,
                "member_id": member.id,
                "mobile": member.mobile,
                "password_hash": hashed_pw,
                "role": "MEMBER",
                "is_active": True,
                "must_change_password": True
            }
            # Ignore if user already exists (e.g. from previous manual seeding)
            existing_user = await self.user_repo.get_user_by_mobile(member.mobile)
            if not existing_user:
                await self.user_repo.create_user(user_data)

        return member

    async def list_members(
        self,
        current_user: User,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        sort_by: str = 'created_at',
        sort_order: str = 'desc'
    ):
        if current_user.role != "ORGANIZER" or not current_user.organizer_id:
            raise HTTPException(status_code=403, detail="Only organizers can view members list")

        organizer_id = current_user.organizer_id
        
        # Enforce maximum page size
        if page_size > 100:
            page_size = 100
        if page_size < 1:
            page_size = 20
        if page < 1:
            page = 1

        skip = (page - 1) * page_size
        
        items, total = await self.member_repo.list_members(
            organizer_id=organizer_id,
            skip=skip,
            limit=page_size,
            search=search,
            is_active=is_active,
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

    async def get_member(self, current_user: User, member_id: UUID):
        if current_user.role != "ORGANIZER" or not current_user.organizer_id:
            raise HTTPException(status_code=403, detail="Only organizers can view member details")

        member = await self.member_repo.get_member_by_id_and_organizer(member_id, current_user.organizer_id)
        if not member:
            # Return 404 instead of 403 to prevent record enumeration
            raise HTTPException(status_code=404, detail="Member not found")
        return member

    async def update_member(self, current_user: User, member_id: UUID, request: MemberUpdateRequest):
        if current_user.role != "ORGANIZER" or not current_user.organizer_id:
            raise HTTPException(status_code=403, detail="Only organizers can update members")

        organizer_id = current_user.organizer_id

        # Lock the row for update via repository
        member = await self.member_repo.get_member_by_id_and_organizer(member_id, organizer_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        # Validate Aadhaar last 4 if provided
        if request.aadhaar_last4 and not re.match(r'^\d{4}$', request.aadhaar_last4):
            raise HTTPException(status_code=400, detail="Aadhaar last 4 must be exactly 4 digits")

        # Alternate mobile validation
        normalized_alt_mobile = None
        if request.alternate_mobile:
            normalized_alt_mobile = normalize_and_validate_indian_mobile(request.alternate_mobile)

        update_data = request.dict(exclude_unset=True)
        if "alternate_mobile" in update_data:
            update_data["alternate_mobile"] = normalized_alt_mobile

        # Compare changes
        old_values = {}
        new_values = {}
        for field, new_val in update_data.items():
            old_val = getattr(member, field, None)
            if old_val != new_val:
                old_values[field] = old_val
                new_values[field] = new_val

        if not new_values:
            return member # No actual changes

        async with self.db.transaction():
            updated_member = await self.member_repo.update_member(member_id, organizer_id, update_data, current_user.id)
            
            # Log MEMBER_UPDATED
            await self.activity_repo.create_log(
                organizer_id=organizer_id,
                member_id=member_id,
                action_type="MEMBER_UPDATED",
                old_values=old_values,
                new_values=new_values,
                remarks="Member profile updated",
                performed_by=current_user.id
            )

        return updated_member

    async def update_member_mobile(self, current_user: User, member_id: UUID, request: MemberMobileUpdateRequest):
        if current_user.role != "ORGANIZER" or not current_user.organizer_id:
            raise HTTPException(status_code=403, detail="Only organizers can change member mobile")

        organizer_id = current_user.organizer_id
        
        member = await self.member_repo.get_member_by_id_and_organizer(member_id, organizer_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        # Validate confirmation
        if request.new_mobile != request.confirm_new_mobile:
            raise HTTPException(status_code=400, detail="New mobile and confirmation mobile do not match")

        # Normalize and validate new mobile
        normalized_new_mobile = normalize_and_validate_indian_mobile(request.new_mobile)
        normalized_old_mobile = normalize_and_validate_indian_mobile(request.old_mobile)

        # Check if old mobile matches member's current mobile
        if member.mobile != normalized_old_mobile:
            raise HTTPException(status_code=400, detail="Old mobile number does not match current member mobile")

        if member.mobile == normalized_new_mobile:
            return member # Mobile is already set to the new value, no change needed

        # Check duplicate new mobile within organizer
        existing = await self.member_repo.get_member_by_mobile_and_organizer(normalized_new_mobile, organizer_id)
        if existing:
            raise HTTPException(status_code=409, detail="A member with this mobile number already exists")

        async with self.db.transaction():
            updated_member = await self.member_repo.update_member_mobile(member_id, organizer_id, normalized_new_mobile, current_user.id)
            
            # Log MEMBER_UPDATED with old/new mobile
            await self.activity_repo.create_log(
                organizer_id=organizer_id,
                member_id=member_id,
                action_type="MEMBER_UPDATED",
                old_values={"mobile": member.mobile},
                new_values={"mobile": normalized_new_mobile},
                remarks="Member mobile number changed",
                performed_by=current_user.id
            )

        return updated_member

    async def update_member_status(self, current_user: User, member_id: UUID, request: MemberStatusRequest):
        if current_user.role != "ORGANIZER" or not current_user.organizer_id:
            raise HTTPException(status_code=403, detail="Only organizers can update member status")

        organizer_id = current_user.organizer_id
        
        member = await self.member_repo.get_member_by_id_and_organizer(member_id, organizer_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        if member.is_active == request.is_active:
            return member # No status change

        async with self.db.transaction():
            updated_member = await self.member_repo.update_member_status(member_id, organizer_id, request.is_active, current_user.id)
            
            action = "MEMBER_ACTIVATED" if request.is_active else "MEMBER_DEACTIVATED"
            remarks = request.remarks or ("Member activated" if request.is_active else "Member deactivated")
            
            await self.activity_repo.create_log(
                organizer_id=organizer_id,
                member_id=member_id,
                action_type=action,
                old_values={"is_active": member.is_active},
                new_values={"is_active": request.is_active},
                remarks=remarks,
                performed_by=current_user.id
            )

        return updated_member

    async def get_member_activity(self, current_user: User, member_id: UUID, page: int = 1, page_size: int = 20):
        if current_user.role != "ORGANIZER" or not current_user.organizer_id:
            raise HTTPException(status_code=403, detail="Only organizers can view activity history")

        member = await self.member_repo.get_member_by_id_and_organizer(member_id, current_user.organizer_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        skip = (page - 1) * page_size
        items, total = await self.activity_repo.get_member_activity_logs(member_id, current_user.organizer_id, skip, page_size)
        return items

    async def get_member_summary(self, current_user: User):
        if current_user.role != "ORGANIZER" or not current_user.organizer_id:
            raise HTTPException(status_code=403, detail="Only organizers can view member summary")

        return await self.member_repo.get_member_summary(current_user.organizer_id)
