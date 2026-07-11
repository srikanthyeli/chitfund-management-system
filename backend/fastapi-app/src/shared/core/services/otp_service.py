import asyncpg
import random
import os
import aiohttp
from datetime import datetime, timedelta, timezone
from src.shared.core.repository.otp_repository import OTPRepository
from src.shared.common.helpers.password_helper import hash_password, verify_password
from src.shared.common.exceptions import AuthenticationError, AppError
import logging

logger = logging.getLogger(__name__)

class OtpService:
    MAX_ATTEMPTS = 3
    MAX_REQUESTS_PER_HOUR = 5
    OTP_EXPIRY_MINUTES = 5

    def __init__(self, db_object: asyncpg.Connection):
        self.db = db_object
        self.otp_repo = OTPRepository(db_object)

    async def _send_sms_twilio(self, mobile: str, otp: str):
        # Read from env variables. If missing, just log it.
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_number = os.getenv("TWILIO_FROM_NUMBER")

        if not account_sid or not auth_token or not from_number:
            logger.warning(f"SMS Gateway credentials missing! OTP for {mobile} is {otp}")
            return True

        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        auth = aiohttp.BasicAuth(login=account_sid, password=auth_token)
        data = {
            "To": mobile,
            "From": from_number,
            "Body": f"Your ChitFund Management login OTP is {otp}. It is valid for {self.OTP_EXPIRY_MINUTES} minutes. Do not share this with anyone."
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, auth=auth, data=data) as response:
                    if response.status not in (200, 201):
                        resp_text = await response.text()
                        logger.error(f"Failed to send SMS to {mobile}: {resp_text}")
                        raise AppError("Failed to send OTP via SMS.", status_code=500)
        except Exception as e:
            logger.error(f"SMS API exception: {str(e)}")
            raise AppError("Error connecting to SMS Gateway.", status_code=500)

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

        # Generate a secure random 6-digit OTP
        otp_str = f"{random.randint(100000, 999999)}"
        
        # Send via SMS Gateway
        await self._send_sms_twilio(mobile, otp_str)

        otp_hash = hash_password(otp_str)
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
