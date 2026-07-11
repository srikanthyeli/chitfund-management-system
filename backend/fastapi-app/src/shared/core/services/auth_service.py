import asyncpg
import uuid
from uuid import UUID
from datetime import datetime, timezone, timedelta

from src.shared.core.repository.user_repository import UserRepository
from src.shared.core.repository.organizer_repository import OrganizerRepository
from src.shared.core.repository.user_session_repository import UserSessionRepository
from src.shared.core.repository.login_audit_repository import LoginAuditRepository
from src.shared.core.repository.member_repository import MemberRepository

from src.shared.common.helpers.password_helper import verify_password, hash_password
from src.shared.common.helpers.jwt_helper import create_access_token, create_refresh_token, decode_token
from src.api.schemas.auth_schema import LoginRequest, ForceLoginRequest, RefreshTokenRequest, RequestOTP, ResetPassword
from src.shared.core.properties.app_properties import settings
from src.api.models.models import User, Member
from src.shared.common.exceptions import AuthenticationError, AuthorizationError, AppError
from src.shared.core.properties.constants import UserRole
from src.shared.core.services.otp_service import OtpService

class AuthService:
    def __init__(self, db_object: asyncpg.Connection):
        self.db = db_object
        self.user_repo = UserRepository(db_object)
        self.organizer_repo = OrganizerRepository(db_object)
        self.session_repo = UserSessionRepository(db_object)
        self.audit_repo = LoginAuditRepository(db_object)
        self.member_repo = MemberRepository(db_object)
        self.otp_service = OtpService(db_object)

    async def _validate_credentials_unified(self, mobile: str, password: str):
        # 1. Check if user is Admin / Organizer
        user = await self.user_repo.get_user_by_mobile(mobile)
        if user:
            if not verify_password(password, user.password_hash):
                await self.audit_repo.create_log("LOGIN_FAILED", user_id=user.id, mobile=mobile, remarks="Invalid password")
                raise AuthenticationError("Invalid credentials")

            if not user.is_active:
                await self.audit_repo.create_log("LOGIN_FAILED", user_id=user.id, mobile=mobile, remarks="User is inactive")
                raise AuthorizationError("User is inactive")

            if user.role == UserRole.ORGANIZER.value and user.organizer_id:
                org = await self.organizer_repo.get_organizer_by_id(user.organizer_id)
                if not org or not org.is_active:
                    await self.audit_repo.create_log("LOGIN_FAILED", user_id=user.id, mobile=mobile, remarks="Organizer is inactive")
                    raise AuthorizationError("Organizer account is inactive")
            
            return {"type": "user", "data": user}

        # 2. If not found in users, check if user is a Member
        members = await self.member_repo.get_members_by_mobile(mobile)
        if members:
            # Find the first active member with matching password
            authenticated_member = None
            for member in members:
                if member.password_hash and verify_password(password, member.password_hash):
                    if not member.is_active:
                        continue
                    org = await self.organizer_repo.get_organizer_by_id(member.organizer_id)
                    if org and org.is_active:
                        authenticated_member = member
                        break
            
            if authenticated_member:
                return {"type": "member", "data": authenticated_member}

            await self.audit_repo.create_log("MEMBER_LOGIN_FAILED", mobile=mobile, remarks="Invalid password or inactive account")
            raise AuthenticationError("Invalid credentials")

        # Not found anywhere
        await self.audit_repo.create_log("LOGIN_FAILED", mobile=mobile, remarks="User/Member not found")
        raise AuthenticationError("Invalid credentials")

    async def login(self, data: LoginRequest):
        auth_entity = await self._validate_credentials_unified(data.mobile, data.password)
        
        if auth_entity["type"] == "user":
            user: User = auth_entity["data"]
            active_session = await self.session_repo.get_active_session_by_user_id(user.id)
            if active_session:
                raise AppError(
                    message="This account is active on another phone.",
                    status_code=409,
                    details={"code": "FORCE_LOGIN_REQUIRED"}
                )
            return await self._create_user_session_and_tokens(user, data.device_id, data.device_name, "LOGIN_SUCCESS")
        
        elif auth_entity["type"] == "member":
            member: Member = auth_entity["data"]
            return await self._create_member_tokens(member, data.device_id, data.device_name, "MEMBER_LOGIN_SUCCESS")

    async def force_login(self, data: ForceLoginRequest):
        auth_entity = await self._validate_credentials_unified(data.mobile, data.password)
        
        if auth_entity["type"] == "user":
            user: User = auth_entity["data"]
            await self.session_repo.deactivate_all_sessions_for_user(user.id)
            return await self._create_user_session_and_tokens(user, data.device_id, data.device_name, "FORCE_LOGIN")
        
        elif auth_entity["type"] == "member":
            # Member sessions aren't tracked in DB right now, just generate tokens
            member: Member = auth_entity["data"]
            return await self._create_member_tokens(member, data.device_id, data.device_name, "FORCE_LOGIN")

    async def _create_user_session_and_tokens(self, user: User, device_id: str, device_name: str, event_type: str):
        now = datetime.utcnow()
        access_exp = now + timedelta(minutes=settings.jwt.access_token_expiry)
        refresh_exp = now + timedelta(days=settings.jwt.refresh_token_expiry)

        session_id = str(uuid.uuid4())
        
        refresh_payload = {
            "user_id": str(user.id),
            "session_id": session_id,
            "token_type": "refresh"
        }
        refresh_token = create_refresh_token(refresh_payload)

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

        await self.user_repo.update_last_login(user.id)
        await self.audit_repo.create_log(event_type, user_id=user.id, mobile=user.mobile, device_id=device_id)

        name = "Platform Admin"
        if user.role == UserRole.MEMBER.value and user.member_id:
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

    async def _create_member_tokens(self, member: Member, device_id: str, device_name: str, event_type: str):
        now = datetime.utcnow()
        access_exp = now + timedelta(minutes=settings.jwt.access_token_expiry)
        refresh_exp = now + timedelta(days=settings.jwt.refresh_token_expiry)

        session_id = str(uuid.uuid4())
        
        refresh_payload = {
            "member_id": str(member.id),
            "session_id": session_id,
            "token_type": "refresh",
            "role": "MEMBER"
        }
        refresh_token = create_refresh_token(refresh_payload)

        access_payload = {
            "member_id": str(member.id),
            "organizer_id": str(member.organizer_id),
            "tenant_id": str(member.organizer_id),
            "role": "MEMBER",
            "session_id": session_id,
            "token_type": "access"
        }
        access_token = create_access_token(access_payload)

        await self.audit_repo.create_log(event_type, mobile=member.mobile, device_id=device_id, remarks=f"Member ID: {member.id}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": member.id,
                "mobile": member.mobile,
                "role": "MEMBER",
                "organizer_id": member.organizer_id,
                "name": member.full_name,
                "must_change_password": False # Members don't have this explicitly in current schema flow
            }
        }

    async def refresh_token(self, data: RefreshTokenRequest):
        try:
            payload = decode_token(data.refresh_token)
            if payload.get("token_type") != "refresh":
                raise ValueError("Invalid token type")
        except Exception as e:
            await self.audit_repo.create_log("INVALID_TOKEN", remarks=str(e))
            raise AuthenticationError("Invalid or expired refresh token")

        # Check if it's a member refresh token
        if payload.get("role") == "MEMBER":
            member_id = payload.get("member_id")
            member = await self.member_repo.get_member_by_id(UUID(member_id)) if member_id else None
            
            # Since members don't have DB sessions right now, just validate member
            if not member or not member.is_active:
                raise AuthenticationError("Member is inactive")

            access_payload = {
                "member_id": str(member.id),
                "organizer_id": str(member.organizer_id),
                "tenant_id": str(member.organizer_id),
                "role": "MEMBER",
                "session_id": payload.get("session_id"),
                "token_type": "access"
            }
            new_access_token = create_access_token(access_payload)
            await self.audit_repo.create_log("MEMBER_TOKEN_REFRESH", mobile=member.mobile)
            return {"access_token": new_access_token}

        # Otherwise, user refresh token
        session_id = payload.get("session_id")
        user_id = payload.get("user_id")

        session = await self.session_repo.get_session_by_id(UUID(session_id))
        if not session or not session.is_active:
            raise AuthenticationError("Session is inactive or expired")

        user = await self.user_repo.get_user_by_id(UUID(user_id))
        if not user or not user.is_active:
            raise AuthenticationError("User is inactive")

        if user.role == UserRole.ORGANIZER.value and user.organizer_id:
            org = await self.organizer_repo.get_organizer_by_id(user.organizer_id)
            if not org or not org.is_active:
                raise AuthorizationError("Organizer is inactive")

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
        # We only have session IDs in DB for users. Members use mock UUIDs.
        # We can gracefully ignore member logouts or check if it exists.
        # If get_current_user resolves to Member, we might need a flag.
        if session_id:
            # Just attempt to deactivate. If it doesn't exist, no harm.
            try:
                await self.session_repo.deactivate_session(session_id)
            except Exception:
                pass
        
        await self.audit_repo.create_log("LOGOUT", user_id=user_id)
        return {"success": True, "message": "Logged out successfully"}
    
    async def get_me(self, current_user):
        # current_user could be User or Member based on get_current_user dependency
        if isinstance(current_user, Member):
            return {
                "id": current_user.id,
                "mobile": current_user.mobile,
                "role": "MEMBER",
                "organizer_id": current_user.organizer_id,
                "name": current_user.full_name,
                "must_change_password": False
            }

        user = current_user
        name = "Platform Admin"
        if user.role == UserRole.MEMBER.value and user.member_id:
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

    async def request_password_reset(self, data: RequestOTP):
        mobile = data.mobile
        user = await self.user_repo.get_user_by_mobile(mobile)
        members = await self.member_repo.get_members_by_mobile(mobile)

        if not user and not members:
            raise AuthenticationError("Account not found")

        # Ensure at least one account is active
        is_active = False
        if user and user.is_active:
            is_active = True
        elif members:
            for member in members:
                if member.is_active:
                    is_active = True
                    break

        if not is_active:
            raise AuthorizationError("Your account is inactive")

        return await self.otp_service.generate_and_send_otp(mobile)

    async def verify_otp_and_reset_password(self, data: ResetPassword):
        mobile = data.mobile
        await self.otp_service.verify_otp(mobile, data.otp)

        user = await self.user_repo.get_user_by_mobile(mobile)
        members = await self.member_repo.get_members_by_mobile(mobile)
        
        hashed_password = hash_password(data.new_password)

        if user:
            # We don't have update_password on user_repo, let's create a raw query or add it
            await self.db.execute("UPDATE users SET password_hash = $1 WHERE id = $2", hashed_password, user.id)

        if members:
            for member in members:
                await self.member_repo.update_password(member.id, hashed_password)

        return {"success": True, "message": "Password set successfully"}
