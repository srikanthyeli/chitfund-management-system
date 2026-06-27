"""
Centralized user-facing message factory.

Usage:
    from src.shared.common.utils.error_messages import ErrorMessages

    ErrorMessages.get_success_message("chit_group")       # → "Chit group retrieved successfully"
    ErrorMessages.insert_success_message("member")        # → "Member created successfully"
    ErrorMessages.not_found_message("chit group", id)     # → "Chit group 'abc' not found"
    ErrorMessages.failed_to_get_message("member")         # → "Failed to retrieve member data"

Never hardcode user-facing strings in routers or services — always use this class.
Add new methods here when a new entity is introduced.
"""


class ErrorMessages:
    # ─── Success Messages ────────────────────────────────────────────────────

    @staticmethod
    def get_success_message(entity: str) -> str:
        return f"{entity.replace('_', ' ').title()} retrieved successfully"

    @staticmethod
    def insert_success_message(entity: str) -> str:
        return f"{entity.replace('_', ' ').title()} created successfully"

    @staticmethod
    def update_success_message(entity: str) -> str:
        return f"{entity.replace('_', ' ').title()} updated successfully"

    @staticmethod
    def delete_success_message(entity: str) -> str:
        return f"{entity.replace('_', ' ').title()} deleted successfully"

    @staticmethod
    def status_change_success_message(entity: str, new_status: str) -> str:
        return f"{entity.replace('_', ' ').title()} status changed to {new_status} successfully"

    # ─── Not Found ───────────────────────────────────────────────────────────

    @staticmethod
    def not_found_message(entity: str, identifier: str = None) -> str:
        base = f"{entity.replace('_', ' ').title()} not found"
        if identifier:
            return f"{entity.replace('_', ' ').title()} '{identifier}' not found"
        return base

    # ─── Conflict / Validation ───────────────────────────────────────────────

    @staticmethod
    def name_already_exists_message(entity: str, value: str) -> str:
        return f"A {entity.replace('_', ' ')} with the name '{value}' already exists"

    @staticmethod
    def already_exists_message(entity: str) -> str:
        return f"{entity.replace('_', ' ').title()} already exists"

    @staticmethod
    def duplicate_request_message(entity: str) -> str:
        return f"Duplicate request: {entity.replace('_', ' ')} already processed"

    # ─── Server Error Messages ───────────────────────────────────────────────

    @staticmethod
    def failed_to_get_message(entity: str) -> str:
        return f"Failed to retrieve {entity.replace('_', ' ')} data"

    @staticmethod
    def failed_to_insert_message(entity: str) -> str:
        return f"Failed to create {entity.replace('_', ' ')}"

    @staticmethod
    def failed_to_update_message(entity: str) -> str:
        return f"Failed to update {entity.replace('_', ' ')}"

    @staticmethod
    def failed_to_delete_message(entity: str) -> str:
        return f"Failed to delete {entity.replace('_', ' ')}"

    # ─── Auth Messages ───────────────────────────────────────────────────────

    @staticmethod
    def unauthorized_message() -> str:
        return "Authentication required. Please log in."

    @staticmethod
    def permission_denied_message() -> str:
        return "You do not have permission to perform this action"

    @staticmethod
    def session_expired_message() -> str:
        return "Your session has expired. Please log in again."

    @staticmethod
    def invalid_credentials_message() -> str:
        return "Invalid email or password"

    @staticmethod
    def account_already_active_message() -> str:
        return "Account is already active on another device"

    # ─── Domain-specific helpers (Chit Fund) ─────────────────────────────────

    @staticmethod
    def chit_status_transition_invalid(from_status: str, to_status: str) -> str:
        return f"Cannot transition chit group from '{from_status}' to '{to_status}'"

    @staticmethod
    def shares_exceed_available(requested: int, available: int) -> str:
        return f"Requested {requested} share(s) exceed the available {available} share(s)"

    @staticmethod
    def member_already_in_chit() -> str:
        return "This member is already part of this chit group"

    @staticmethod
    def payout_already_exists_for_month(month_number: int) -> str:
        return f"A payout already exists for month {month_number}"

    @staticmethod
    def month_already_closed(month_number: int) -> str:
        return f"Month {month_number} financial closure already exists"
