class AppError(Exception):
    """Base application exception"""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details

class AuthenticationError(AppError):
    """401 Unauthorized Exception"""
    def __init__(self, message: str = "Unauthorized", details: dict = None):
        super().__init__(message, status_code=401, details=details)

class AuthorizationError(AppError):
    """403 Forbidden Exception"""
    def __init__(self, message: str = "Forbidden", details: dict = None):
        super().__init__(message, status_code=403, details=details)

class UserNotFoundError(AppError):
    """404 User Not Found Exception"""
    def __init__(self, message: str = "User not found", details: dict = None):
        super().__init__(message, status_code=404, details=details)

class ValidationError(AppError):
    """422 Validation Error Exception"""
    def __init__(self, message: str = "Validation error", details: dict = None):
        super().__init__(message, status_code=422, details=details)

class InternalServerError(AppError):
    """500 Internal Server Error Exception"""
    def __init__(self, message: str = "Internal server error", details: dict = None):
        super().__init__(message, status_code=500, details=details)
