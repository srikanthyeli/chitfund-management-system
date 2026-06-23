import jwt
from datetime import datetime, timedelta
from typing import Optional
from src.shared.core.properties.app_properties import settings
from src.shared.common.exceptions import AuthenticationError

SECRET_KEY = settings.jwt.secret_key
ALGORITHM = settings.jwt.algorithm
ACCESS_TOKEN_EXPIRY = settings.jwt.access_token_expiry  # minutes
REFRESH_TOKEN_EXPIRY = settings.jwt.refresh_token_expiry  # days

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a new Access Token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRY)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a new Refresh Token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRY)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    """
    Decodes the token and handles common JWT signature/expiration exceptions.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.PyJWTError:
        raise AuthenticationError("Invalid token")

def verify_token(token: str, token_type: str = "access") -> dict:
    """
    Decodes and verifies token type (access or refresh).
    """
    payload = decode_token(token)
    if payload.get("type") != token_type:
        raise AuthenticationError(f"Invalid token type: expected {token_type}")
    return payload
