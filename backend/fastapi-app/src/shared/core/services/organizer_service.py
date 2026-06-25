import asyncpg
from uuid import UUID
from fastapi import HTTPException
import string
import secrets

from src.shared.core.repository.organizer_repository import OrganizerRepository
from src.shared.core.repository.user_repository import UserRepository
from src.shared.core.repository.user_session_repository import UserSessionRepository
from src.shared.core.repository.login_audit_repository import LoginAuditRepository
from src.shared.common.helpers.password_helper import hash_password
from src.api.schemas.organizer_schema import OrganizerCreateRequest, OrganizerUpdateRequest, OrganizerStatusRequest

class OrganizerService:
    def __init__(self, db_object: asyncpg.Connection):
        self.db = db_object
        self.organizer_repo = OrganizerRepository(db_object)
        self.user_repo = UserRepository(db_object)
        self.session_repo = UserSessionRepository(db_object)
        self.audit_repo = LoginAuditRepository(db_object)

    def _generate_temp_password(self, mobile: str):
        return f"user@{mobile}"

    async def create_organizer(self, data: OrganizerCreateRequest, admin_user_id: UUID):
        existing_org_by_mobile = await self.organizer_repo.get_organizer_by_mobile(data.mobile)
        if existing_org_by_mobile:
            raise HTTPException(status_code=400, detail="Organizer with this mobile already exists")
            
        if data.email:
            existing_org_by_email = await self.organizer_repo.get_organizer_by_email(data.email)
            if existing_org_by_email:
                raise HTTPException(status_code=400, detail="Organizer with this email already exists")

        existing_user_by_mobile = await self.user_repo.get_user_by_mobile(data.mobile)
        if existing_user_by_mobile:
            raise HTTPException(status_code=400, detail="User with this mobile already exists")

        temp_password = self._generate_temp_password(data.mobile)
        hashed_password = hash_password(temp_password)

        org = await self.organizer_repo.create_organizer(data.dict(), admin_user_id)
        
        user_data = {
            "organizer_id": org.id,
            "mobile": org.mobile,
            "password_hash": hashed_password,
            "role": "ORGANIZER",
            "is_active": True,
            "must_change_password": True
        }
        await self.user_repo.create_user(user_data)
        
        await self.audit_repo.create_log("ORGANIZER_CREATED", user_id=admin_user_id, remarks=f"Created organizer {org.organizer_code}")

        return {
            "id": org.id,
            "organizer_code": org.organizer_code,
            "name": org.name,
            "mobile": org.mobile,
            "login_mobile": org.mobile,
            "temporary_password": temp_password
        }

    async def get_all_organizers(self, skip: int = 0, limit: int = 100):
        items, total = await self.organizer_repo.get_all_organizers(skip, limit)
        return {"items": items, "total": total}

    async def get_organizer(self, organizer_id: UUID):
        org = await self.organizer_repo.get_organizer_by_id(organizer_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organizer not found")
        return org

    async def update_organizer(self, organizer_id: UUID, data: OrganizerUpdateRequest, admin_user_id: UUID):
        org = await self.organizer_repo.get_organizer_by_id(organizer_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organizer not found")
            
        update_data = data.dict(exclude_unset=True)
        if "mobile" in update_data and update_data["mobile"] != org.mobile:
            raise HTTPException(status_code=400, detail="Cannot update organizer mobile number")
            
        if "email" in update_data and update_data["email"] != org.email:
            existing = await self.organizer_repo.get_organizer_by_email(update_data["email"])
            if existing:
                raise HTTPException(status_code=400, detail="Email already in use")

        updated_org = await self.organizer_repo.update_organizer(organizer_id, update_data, admin_user_id)
        await self.audit_repo.create_log("ORGANIZER_UPDATED", user_id=admin_user_id, remarks=f"Updated organizer {org.organizer_code}")
        return updated_org

    async def update_status(self, organizer_id: UUID, data: OrganizerStatusRequest, admin_user_id: UUID):
        org = await self.organizer_repo.get_organizer_by_id(organizer_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organizer not found")

        await self.organizer_repo.update_organizer_status(organizer_id, data.is_active, admin_user_id)
        
        user = await self.user_repo.get_user_by_mobile(org.mobile)
        if user:
            await self.user_repo.update_user_status(user.id, data.is_active)
            if not data.is_active:
                await self.session_repo.deactivate_all_sessions_for_user(user.id)
                
        event = "ORGANIZER_ACTIVATED" if data.is_active else "ORGANIZER_DEACTIVATED"
        await self.audit_repo.create_log(event, user_id=admin_user_id, remarks=f"Changed status for organizer {org.organizer_code}")
        return {"success": True}
