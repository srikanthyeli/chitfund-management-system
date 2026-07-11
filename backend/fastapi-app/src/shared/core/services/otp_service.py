import asyncpg
from datetime import datetime, timedelta, timezone
from src.shared.core.repository.otp_repository import OTPRepository
from src.shared.common.helpers.password_helper import hash_password, verify_password
from src.shared.common.exceptions import AuthenticationError, AppError

class OtpService:
    MAX_ATTEMPTS = 3
    MAX_REQUESTS_PER_HOUR = 5
    OTP_EXPIRY_MINUTES = 5

    def __init__(self, db_object: asyncpg.Connection):
        self.db = db_object
        self.otp_repo = OTPRepository(db_object)

    async def generate_and_send_otp(self, mobile: str) -> dict:
        # Rate limit checks
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        recent_count = await self.otp_repo.count_recent_requests(mobile, one_hour_ago)
        if recent_count >= self.MAX_REQUESTS_PER_HOUR:
            raise AppError(
                message="Too many OTP requests. Please try again later.",
                status_code=429
            )

        # Generate OTP (mocked for now, integrate SMS gateway in production)
        mock_otp = "123456"
        print(f"Generated OTP for {mobile}: {mock_otp}")

        otp_hash = hash_password(mock_otp)
        expires_at = now + timedelta(minutes=self.OTP_EXPIRY_MINUTES)
        
        await self.otp_repo.create_otp_request(mobile, otp_hash, expires_at)
        
        return {"success": True, "message": "OTP sent successfully"}

    async def verify_otp(self, mobile: str, otp: str) -> bool:
        otp_request = await self.otp_repo.get_latest_otp_request(mobile)
        if not otp_request:
            raise AuthenticationError("No OTP request found for this number")

        if otp_request.is_used:
            raise AuthenticationError("OTP has already been used")

        if datetime.utcnow() > otp_request.expires_at:
            raise AuthenticationError("OTP has expired")

        if otp_request.attempts >= self.MAX_ATTEMPTS:
            raise AuthenticationError("Too many incorrect attempts. Please request a new OTP.")

        is_valid = verify_password(otp, otp_request.otp_hash)
        if not is_valid:
            await self.otp_repo.increment_attempts(otp_request.id)
            raise AuthenticationError("Invalid OTP")

        # Mark as used
        await self.otp_repo.mark_as_used(otp_request.id)
        return True
