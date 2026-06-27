"""
Application-wide constants and enums.

Usage:
    from src.shared.core.properties.constants import (
        ChitStatus, MembershipStatus, PayoutStatus,
        AuctionStatus, UserRole, MaintenanceChargeType,
        PayoutSource, CollectionStatus, ActivityAction
    )

    ChitStatus.ACTIVE.value          # → "ACTIVE"
    UserRole.ORGANIZER.value         # → "ORGANIZER"
    ActivityAction.CHIT_CREATED.value # → "CHIT_CREATED"

Rules:
- Never use magic strings for status/role/action values in services or repositories.
- Always reference these enums so that a rename is a one-line change here.
- Add new enums here when a new entity or status type is introduced.
"""

from enum import Enum


# ─── User & Auth ─────────────────────────────────────────────────────────────

class UserRole(str, Enum):
    ORGANIZER = "ORGANIZER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


# ─── Chit Group ──────────────────────────────────────────────────────────────

class ChitStatus(str, Enum):
    DRAFT = "DRAFT"
    READY_TO_START = "READY_TO_START"
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class MaintenanceChargeType(str, Enum):
    FIXED = "FIXED"
    PERCENTAGE = "PERCENTAGE"


# ─── Chit Membership ─────────────────────────────────────────────────────────

class MembershipStatus(str, Enum):
    ACTIVE = "ACTIVE"
    REMOVED = "REMOVED"
    TRANSFERRED = "TRANSFERRED"


# ─── Chit Auction ────────────────────────────────────────────────────────────

class AuctionStatus(str, Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


# ─── Winner Payout ───────────────────────────────────────────────────────────

class PayoutStatus(str, Enum):
    DRAFT = "DRAFT"
    PAYMENT_INITIATED = "PAYMENT_INITIATED"
    PAID = "PAID"
    WINNER_CONFIRMED = "WINNER_CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    REVERSED = "REVERSED"


class PayoutSource(str, Enum):
    COLLECTION_ONLY = "COLLECTION_ONLY"
    ORGANIZER_CONTRIBUTION = "ORGANIZER_CONTRIBUTION"
    MIXED = "MIXED"


class PaymentMethod(str, Enum):
    CASH = "CASH"
    BANK_TRANSFER = "BANK_TRANSFER"
    UPI = "UPI"
    CHEQUE = "CHEQUE"
    OTHER = "OTHER"


# ─── Collection ──────────────────────────────────────────────────────────────

class CollectionStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    OVERDUE = "OVERDUE"
    WAIVED = "WAIVED"


# ─── Financial Closure ───────────────────────────────────────────────────────

class ClosureStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


# ─── Activity Log Actions ────────────────────────────────────────────────────

class ActivityAction(str, Enum):
    # Chit Group
    CHIT_CREATED = "CHIT_CREATED"
    CHIT_UPDATED = "CHIT_UPDATED"
    CHIT_READY_TO_START = "CHIT_READY_TO_START"
    CHIT_ACTIVATED = "CHIT_ACTIVATED"
    CHIT_CANCELLED = "CHIT_CANCELLED"
    CHIT_COMPLETED = "CHIT_COMPLETED"
    CHIT_STATUS_CHANGED = "CHIT_STATUS_CHANGED"

    # Membership
    MEMBER_SHARE_ALLOCATED = "MEMBER_SHARE_ALLOCATED"
    MEMBER_SHARE_UPDATED = "MEMBER_SHARE_UPDATED"
    MEMBER_REMOVED = "MEMBER_REMOVED"
    MEMBER_BULK_ALLOCATED = "MEMBER_BULK_ALLOCATED"

    # Auction
    AUCTION_OPENED = "AUCTION_OPENED"
    AUCTION_CLOSED = "AUCTION_CLOSED"
    AUCTION_CANCELLED = "AUCTION_CANCELLED"
    BID_PLACED = "BID_PLACED"
    WINNER_DECLARED = "WINNER_DECLARED"

    # Payout
    PAYOUT_DRAFT_CREATED = "PAYOUT_DRAFT_CREATED"
    PAYOUT_INITIATED = "PAYOUT_INITIATED"
    PAYOUT_MARKED_PAID = "PAYOUT_MARKED_PAID"
    PAYOUT_CONFIRMED = "PAYOUT_CONFIRMED"
    PAYOUT_CANCELLED = "PAYOUT_CANCELLED"
    PAYOUT_REVERSED = "PAYOUT_REVERSED"

    # Collection
    COLLECTION_RECORDED = "COLLECTION_RECORDED"
    COLLECTION_UPDATED = "COLLECTION_UPDATED"

    # Financial Closure
    MONTH_CLOSED = "MONTH_CLOSED"

    # Member
    MEMBER_CREATED = "MEMBER_CREATED"
    MEMBER_UPDATED = "MEMBER_UPDATED"
    MEMBER_DEACTIVATED = "MEMBER_DEACTIVATED"
    MEMBER_REACTIVATED = "MEMBER_REACTIVATED"
