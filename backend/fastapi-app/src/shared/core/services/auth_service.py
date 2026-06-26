import asyncpg
import uuid
from uuid import UUID
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException

from src.shared.core.repository.user_repository import UserRepository
from src.shared.core.repository.organizer_repository import OrganizerRepository
from src.shared.core.repository.user_session_repository import UserSessionRepository
from src.shared.core.repository.login_audit_repository import LoginAuditRepository
from src.shared.core.repository.member_repository import MemberRepository

from src.shared.common.helpers.password_helper import verify_password
from src.shared.common.helpers.jwt_helper import create_access_token, create_refresh_token, decode_token
from src.api.schemas.auth_schema import LoginRequest, ForceLoginRequest, RefreshTokenRequest
from src.shared.core.properties.app_properties import settings
from src.api.models.models import User

class AuthService:
    def __init__(self, db_object: asyncpg.Connection):
        self.db = db_object
        self.user_repo = UserRepository(db_object)
        self.organizer_repo = OrganizerRepository(db_object)
        self.session_repo = UserSessionRepository(db_object)
        self.audit_repo = LoginAuditRepository(db_object)
        self.member_repo = MemberRepository(db_object)

    async def _validate_user_credentials(self, mobile: str, password: str) -> User:
        user = await self.user_repo.get_user_by_mobile(mobile)
        if not user:
            await self.audit_repo.create_log("LOGIN_FAILED", mobile=mobile, remarks="User not found")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not verify_password(password, user.password_hash):
            await self.audit_repo.create_log("LOGIN_FAILED", user_id=user.id, mobile=mobile, remarks="Invalid password")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not user.is_active:
            await self.audit_repo.create_log("LOGIN_FAILED", user_id=user.id, mobile=mobile, remarks="User is inactive")
            raise HTTPException(status_code=403, detail="User is inactive")



        if user.role == "ORGANIZER" and user.organizer_id:
            org = await self.organizer_repo.get_organizer_by_id(user.organizer_id)
            if not org or not org.is_active:
                await self.audit_repo.create_log("LOGIN_FAILED", user_id=user.id, mobile=mobile, remarks="Organizer is inactive")
                raise HTTPException(status_code=403, detail="Organizer account is inactive")

        return user

    async def login(self, data: LoginRequest):
        user = await self._validate_user_credentials(data.mobile, data.password)

        active_session = await self.session_repo.get_active_session_by_user_id(user.id)
        if active_session:
            raise HTTPException(
                status_code=409,
                detail={"success": False, "code": "FORCE_LOGIN_REQUIRED", "message": "This account is active on another phone."}
            )

        return await self._create_session_and_tokens(user, data.device_id, data.device_name, "LOGIN_SUCCESS")

    async def force_login(self, data: ForceLoginRequest):
        user = await self._validate_user_credentials(data.mobile, data.password)
        
        await self.session_repo.deactivate_all_sessions_for_user(user.id)
        return await self._create_session_and_tokens(user, data.device_id, data.device_name, "FORCE_LOGIN")

    async def _create_session_and_tokens(self, user: User, device_id: str, device_name: str, event_type: str):
        now = datetime.utcnow()
        access_exp = now + timedelta(minutes=settings.jwt.access_token_expiry)
        refresh_exp = now + timedelta(days=settings.jwt.refresh_token_expiry)

        session_id = str(uuid.uuid4()) # Temporary id to include in token before DB insertion, wait DB handles UUID creation.
        # Actually we need DB session id inside token, so we generate here or pass to repo
        
        refresh_payload = {
            "user_id": str(user.id),
            "session_id": session_id,
            "token_type": "refresh"
        }
        refresh_token = create_refresh_token(refresh_payload)

        # Create session in DB with the generated token
        session = await self.session_repo.create_session(
            user.id, device_id, device_name, None, refresh_token, access_exp, refresh_exp
        )

        access_payload = {
            "user_id": str(user.id),
            "organizer_id": str(user.organizer_id) if user.organizer_id else None,
            "role": user.role,
            "session_id": str(session.id),
            "token_type": "access"
        }
        access_token = create_access_token(access_payload)

        # Update last login
        await self.user_repo.update_last_login(user.id)
        
        # Log event
        await self.audit_repo.create_log(event_type, user_id=user.id, mobile=user.mobile, device_id=device_id)

        # Get name based on role
        name = "Platform Admin"
        if user.role == "MEMBER" and user.member_id:
            member = await self.member_repo.get_member_by_id_and_organizer(user.member_id, user.organizer_id)
            if member: name = member.full_name
        elif user.organizer_id:
            org = await self.organizer_repo.get_organizer_by_id(user.organizer_id)
            if org: name = org.name

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "mobile": user.mobile,
                "role": user.role,
                "organizer_id": user.organizer_id,
                "name": name,
                "must_change_password": user.must_change_password
            }
        }

    async def refresh_token(self, data: RefreshTokenRequest):
        try:
            payload = decode_token(data.refresh_token)
            if payload.get("token_type") != "refresh":
                raise ValueError("Invalid token type")
        except Exception as e:
            await self.audit_repo.create_log("INVALID_TOKEN", remarks=str(e))
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

        session_id = payload.get("session_id")
        user_id = payload.get("user_id")

        session = await self.session_repo.get_session_by_id(UUID(session_id))
        if not session or not session.is_active:
            raise HTTPException(status_code=401, detail="Session is inactive or expired")

        user = await self.user_repo.get_user_by_id(UUID(user_id))
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User is inactive")

        if user.role == "ORGANIZER" and user.organizer_id:
            org = await self.organizer_repo.get_organizer_by_id(user.organizer_id)
            if not org or not org.is_active:
                raise HTTPException(status_code=403, detail="Organizer is inactive")

        access_payload = {
            "user_id": str(user.id),
            "organizer_id": str(user.organizer_id) if user.organizer_id else None,
            "role": user.role,
            "session_id": str(session.id),
            "token_type": "access"
        }
        new_access_token = create_access_token(access_payload)

        now = datetime.utcnow()
        access_exp = now + timedelta(minutes=settings.jwt.access_token_expiry)
        
        await self.session_repo.update_session_activity(session.id, access_exp)
        await self.audit_repo.create_log("TOKEN_REFRESH", user_id=user.id, mobile=user.mobile)

        return {"access_token": new_access_token}

    async def logout(self, user_id: UUID, session_id: UUID):
        await self.session_repo.deactivate_session(session_id)
        await self.audit_repo.create_log("LOGOUT", user_id=user_id)
        return {"success": True, "message": "Logged out successfully"}
    
    async def get_me(self, user: User):
        name = "Platform Admin"
        if user.role == "MEMBER" and user.member_id:
            member = await self.member_repo.get_member_by_id_and_organizer(user.member_id, user.organizer_id)
            if member: name = member.full_name
        elif user.organizer_id:
            org = await self.organizer_repo.get_organizer_by_id(user.organizer_id)
            if org: name = org.name

        return {
            "id": user.id,
            "mobile": user.mobile,
            "role": user.role,
            "organizer_id": user.organizer_id,
            "name": name,
            "must_change_password": user.must_change_password
        }

