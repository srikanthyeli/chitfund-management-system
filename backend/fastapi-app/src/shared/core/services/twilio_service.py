import os
import logging
from typing import Dict, Any
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from src.shared.common.exceptions import AppError, AuthenticationError

logger = logging.getLogger(__name__)

class TwilioService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.verify_service_sid = os.getenv("TWILIO_VERIFY_SERVICE_SID")
        
        if not all([self.account_sid, self.auth_token, self.verify_service_sid]):
            logger.error("Missing Twilio credentials or Verify Service SID in environment variables.")
            # We initialize client to None to fail gracefully if it's not configured
            self.client = None
        else:
            try:
                self.client = Client(self.account_sid, self.auth_token)
            except Exception as e:
                logger.error(f"Failed to initialize Twilio Client: {e}")
                self.client = None

    def send_otp(self, phone_number: str) -> Dict[str, Any]:
        """
        Sends an OTP via SMS to the provided phone number using Twilio Verify API.
        """
        if not self.client:
            logger.error("Twilio service is not configured properly.")
            raise AppError("SMS service is currently unavailable.", status_code=500)

        try:
            # Twilio requires E.164 format, assuming validation is done before calling this
            verification = self.client.verify.v2.services(
                self.verify_service_sid
            ).verifications.create(to=phone_number, channel="sms")
            
            logger.info(f"OTP send attempt initiated for {phone_number}. Status: {verification.status}")
            
            return {
                "success": True,
                "message": "OTP sent successfully"
            }
            
        except TwilioRestException as e:
            logger.error(f"Twilio API Error while sending OTP to {phone_number}: {e.msg}")
            raise AppError("Unable to send OTP", status_code=400)
        except Exception as e:
            logger.error(f"Unexpected error while sending OTP to {phone_number}: {str(e)}")
            raise AppError("Unable to send OTP", status_code=500)

    def verify_otp(self, phone_number: str, otp: str) -> Dict[str, Any]:
        """
        Verifies the provided OTP for the given phone number using Twilio Verify API.
        """
        if not self.client:
            logger.error("Twilio service is not configured properly.")
            raise AppError("SMS service is currently unavailable.", status_code=500)

        try:
            verification_check = self.client.verify.v2.services(
                self.verify_service_sid
            ).verification_checks.create(to=phone_number, code=otp)

            if verification_check.status == "approved":
                logger.info(f"OTP verified successfully for {phone_number}.")
                return {
                    "success": True,
                    "message": "OTP verified successfully"
                }
            else:
                logger.warning(f"OTP verification failed for {phone_number}. Status: {verification_check.status}")
                return {
                    "success": False,
                    "message": "Invalid or expired OTP"
                }

        except TwilioRestException as e:
            # Code 20404 means the verification resource was not found (expired/invalid phone)
            if e.code == 20404:
                logger.warning(f"OTP verification not found or expired for {phone_number}.")
                return {
                    "success": False,
                    "message": "Invalid or expired OTP"
                }
            logger.error(f"Twilio API Error during verification for {phone_number}: {e.msg}")
            raise AppError("Error verifying OTP", status_code=500)
        except Exception as e:
            logger.error(f"Unexpected error during OTP verification for {phone_number}: {str(e)}")
            raise AppError("Error verifying OTP", status_code=500)
