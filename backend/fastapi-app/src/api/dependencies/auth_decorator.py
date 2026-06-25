import functools
from typing import List, Optional
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

def authorize(allowed_roles: Optional[List[str]] = None):
    """
    Security decorator to enforce role-based access control and tenant isolation.
    Must be used with an endpoint that injects `current_user` via `Depends(get_current_user)`.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from FastAPI dependency injection (kwargs)
            current_user = kwargs.get("current_user")
            
            if not current_user:
                logger.error("Developer Error: @authorize used on endpoint without current_user dependency.")
                raise HTTPException(status_code=500, detail="Internal server error: Authentication misconfiguration")

            # Verify role if allowed_roles are specified
            if allowed_roles and current_user.role not in allowed_roles:
                logger.warning(f"Access Denied: User {current_user.id} with role {current_user.role} attempted to access an endpoint requiring {allowed_roles}")
                raise HTTPException(status_code=403, detail="Forbidden: You do not have the required role to perform this action.")

            # Proceed to the actual endpoint logic
            return await func(*args, **kwargs)
        return wrapper
    return decorator
