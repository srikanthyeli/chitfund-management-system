import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, DateTime, UniqueConstraint, Integer, Numeric, Date, Index, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.shared.core.base_model import Base
from src.shared.core.audit import AuditMixin

class Organizer(Base, AuditMixin):
    __tablename__ = "organizers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organizer_code = Column(String(20), unique=True, nullable=False)
    name = Column(String(150), nullable=False)
    mobile = Column(String(15), unique=True, nullable=False)
    email = Column(String(150), unique=True, nullable=True)
    address = Column(Text, nullable=True)
    village = Column(String(100), nullable=True)
    mandal = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    users = relationship("User", back_populates="organizer", foreign_keys="[User.organizer_id]")
    members = relationship("Member", back_populates="organizer", cascade="all, delete-orphan", foreign_keys="[Member.organizer_id]")
    chit_groups = relationship("ChitGroup", back_populates="organizer", cascade="all, delete-orphan", foreign_keys="[ChitGroup.organizer_id]")
    chit_memberships = relationship("ChitMembership", back_populates="organizer", cascade="all, delete-orphan", foreign_keys="[ChitMembership.organizer_id]")
    chit_group_activity_logs = relationship("ChitGroupActivityLog", back_populates="organizer", cascade="all, delete-orphan", foreign_keys="[ChitGroupActivityLog.organizer_id]")


class User(Base, AuditMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("organizers.id", ondelete="CASCADE"), nullable=True)
    member_id = Column(UUID(as_uuid=True), nullable=True) # for future use
    mobile = Column(String(15), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    role = Column(String(20), nullable=False, default="MEMBER", index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    last_login_at = Column(DateTime, nullable=True)
    must_change_password = Column(Boolean, nullable=False, default=True)

    organizer = relationship("Organizer", back_populates="users", foreign_keys="[User.organizer_id]")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan", foreign_keys="[UserSession.user_id]")
    created_chit_groups = relationship("ChitGroup", back_populates="created_by_user", foreign_keys="[ChitGroup.created_by]")
    updated_chit_groups = relationship("ChitGroup", back_populates="updated_by_user", foreign_keys="[ChitGroup.updated_by]")
    performed_chit_group_activity_logs = relationship("ChitGroupActivityLog", back_populates="performed_by_user", foreign_keys="[ChitGroupActivityLog.performed_by_user_id]")


class UserSession(Base, AuditMixin):
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    device_id = Column(String(255), nullable=True)
    device_name = Column(String(255), nullable=True)
    ip_address = Column(String(100), nullable=True)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, unique=True, nullable=False)
    login_at = Column(DateTime, nullable=False)
    access_token_expires_at = Column(DateTime, nullable=False)
    refresh_token_expires_at = Column(DateTime, nullable=False)
    last_activity_at = Column(DateTime, nullable=True)
    logout_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    user = relationship("User", back_populates="sessions", foreign_keys="[UserSession.user_id]")


class LoginAuditLog(Base):
    __tablename__ = "login_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    mobile = Column(String(15), nullable=True)
    event_type = Column(String(50), nullable=False)
    ip_address = Column(String(100), nullable=True)
    device_id = Column(String(255), nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class Member(Base, AuditMixin):
    __tablename__ = "members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("organizers.id", ondelete="CASCADE"), nullable=False, index=True)
    member_code = Column(String(30), nullable=False)
    full_name = Column(String(150), nullable=False, index=True)
    mobile = Column(String(15), nullable=False, index=True)
    alternate_mobile = Column(String(15), nullable=True)
    email = Column(String(150), nullable=True)
    address = Column(Text, nullable=True)
    village = Column(String(100), nullable=True, index=True) # Adding index for search/filter if needed, but village search is not explicitly indexed. We'll index it just in case or leave it.
    mandal = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    aadhaar_last4 = Column(String(4), nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)

    organizer = relationship("Organizer", back_populates="members", foreign_keys="[Member.organizer_id]")
    activity_logs = relationship("MemberActivityLog", back_populates="member", cascade="all, delete-orphan", foreign_keys="[MemberActivityLog.member_id]")
    chit_memberships = relationship("ChitMembership", back_populates="member", cascade="all, delete-orphan", foreign_keys="[ChitMembership.member_id]")

    __table_args__ = (
        UniqueConstraint('organizer_id', 'mobile', name='uq_members_organizer_mobile'),
        UniqueConstraint('organizer_id', 'member_code', name='uq_members_organizer_member_code'),
    )


class MemberActivityLog(Base):
    __tablename__ = "member_activity_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("organizers.id", ondelete="CASCADE"), nullable=False, index=True)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type = Column(String(50), nullable=False)
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
    remarks = Column(Text, nullable=True)
    performed_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)

    member = relationship("Member", back_populates="activity_logs", foreign_keys="[MemberActivityLog.member_id]")


class ChitGroup(Base, AuditMixin):
    __tablename__ = "chit_groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("organizers.id", ondelete="CASCADE"), nullable=False, index=True)

    chit_code = Column(String(50), nullable=False)
    chit_name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)

    total_chit_value = Column(Numeric(14, 2), nullable=False)
    monthly_installment_per_share = Column(Numeric(14, 2), nullable=False)

    total_shares = Column(Integer, nullable=False)
    duration_months = Column(Integer, nullable=False)

    maintenance_charge = Column(Numeric(14, 2), nullable=False, default=0)
    maintenance_charge_type = Column(String(20), nullable=False, default="FIXED")

    start_date = Column(Date, nullable=False, index=True)
    installment_due_day = Column(Integer, nullable=False, default=1)

    status = Column(String(30), nullable=False, default="DRAFT", index=True)

    allocated_shares = Column(Integer, nullable=False, default=0)
    available_shares = Column(Integer, nullable=False)

    organizer = relationship("Organizer", back_populates="chit_groups", foreign_keys="[ChitGroup.organizer_id]")
    created_by_user = relationship("User", back_populates="created_chit_groups", foreign_keys="[ChitGroup.created_by]")
    updated_by_user = relationship("User", back_populates="updated_chit_groups", foreign_keys="[ChitGroup.updated_by]")
    chit_memberships = relationship("ChitMembership", back_populates="chit_group", cascade="all, delete-orphan", foreign_keys="[ChitMembership.chit_group_id]")
    chit_group_activity_logs = relationship("ChitGroupActivityLog", back_populates="chit_group", cascade="all, delete-orphan", foreign_keys="[ChitGroupActivityLog.chit_group_id]")
    chit_auctions = relationship("ChitAuction", back_populates="chit_group", cascade="all, delete-orphan", foreign_keys="[ChitAuction.chit_group_id]")

    __table_args__ = (
        UniqueConstraint('organizer_id', 'chit_code', name='uq_chit_groups_organizer_chit_code'),
        Index('uq_chit_groups_organizer_name', 'organizer_id', 'chit_name', unique=True, postgresql_where='is_deleted = false'),
    )


class ChitMembership(Base, AuditMixin):
    __tablename__ = "chit_memberships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("organizers.id", ondelete="CASCADE"), nullable=False, index=True)
    chit_group_id = Column(UUID(as_uuid=True), ForeignKey("chit_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True)

    share_count = Column(Integer, nullable=False, default=1)
    joined_at = Column(DateTime, nullable=False, server_default=func.now())
    status = Column(String(30), nullable=False, default="ACTIVE", index=True)
    remarks = Column(Text, nullable=True)

    # Winner tracking (Phase 4)
    has_won_auction = Column(Boolean, nullable=False, default=False)
    won_auction_id = Column(UUID(as_uuid=True), ForeignKey("chit_auctions.id", ondelete="SET NULL"), nullable=True)
    won_month_number = Column(Integer, nullable=True)

    organizer = relationship("Organizer", back_populates="chit_memberships", foreign_keys="[ChitMembership.organizer_id]")
    chit_group = relationship("ChitGroup", back_populates="chit_memberships", foreign_keys="[ChitMembership.chit_group_id]")
    member = relationship("Member", back_populates="chit_memberships", foreign_keys="[ChitMembership.member_id]")
    chit_group_activity_logs = relationship("ChitGroupActivityLog", back_populates="membership", cascade="all, delete-orphan", foreign_keys="[ChitGroupActivityLog.membership_id]")
    auction_bids = relationship("ChitAuctionBid", back_populates="membership", foreign_keys="[ChitAuctionBid.membership_id]")

    __table_args__ = (
        Index('uq_chit_memberships_group_member', 'chit_group_id', 'member_id', unique=True, postgresql_where='is_deleted = false'),
    )


class ChitGroupActivityLog(Base):
    __tablename__ = "chit_group_activity_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("organizers.id", ondelete="CASCADE"), nullable=False, index=True)
    chit_group_id = Column(UUID(as_uuid=True), ForeignKey("chit_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    membership_id = Column(UUID(as_uuid=True), ForeignKey("chit_memberships.id", ondelete="SET NULL"), nullable=True, index=True)

    action_type = Column(String(60), nullable=False, index=True)
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
    remarks = Column(Text, nullable=True)

    performed_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)

    organizer = relationship("Organizer", back_populates="chit_group_activity_logs", foreign_keys="[ChitGroupActivityLog.organizer_id]")
    chit_group = relationship("ChitGroup", back_populates="chit_group_activity_logs", foreign_keys="[ChitGroupActivityLog.chit_group_id]")
    membership = relationship("ChitMembership", back_populates="chit_group_activity_logs", foreign_keys="[ChitGroupActivityLog.membership_id]")
    performed_by_user = relationship("User", back_populates="performed_chit_group_activity_logs", foreign_keys="[ChitGroupActivityLog.performed_by_user_id]")


class ChitAuction(Base, AuditMixin):
    __tablename__ = "chit_auctions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("organizers.id", ondelete="CASCADE"), nullable=False, index=True)
    chit_group_id = Column(UUID(as_uuid=True), ForeignKey("chit_groups.id", ondelete="CASCADE"), nullable=False, index=True)

    auction_month_number = Column(Integer, nullable=False)
    auction_date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False, default="OPEN", index=True)  # DRAFT|OPEN|FINALIZED|CANCELLED

    gross_chit_amount = Column(Numeric(14, 2), nullable=False)
    maintenance_charge = Column(Numeric(14, 2), nullable=False, default=0)
    total_discount_amount = Column(Numeric(14, 2), nullable=True)
    maximum_bid_discount = Column(Numeric(14, 2), nullable=True)

    winner_membership_id = Column(UUID(as_uuid=True), ForeignKey("chit_memberships.id", ondelete="SET NULL"), nullable=True)
    winner_member_id = Column(UUID(as_uuid=True), ForeignKey("members.id", ondelete="SET NULL"), nullable=True)
    winner_payout_amount = Column(Numeric(14, 2), nullable=True)
    bonus_per_share = Column(Numeric(14, 2), nullable=True)

    notes = Column(Text, nullable=True)
    finalized_at = Column(DateTime, nullable=True)
    finalized_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    organizer = relationship("Organizer", foreign_keys="[ChitAuction.organizer_id]")
    chit_group = relationship("ChitGroup", back_populates="chit_auctions", foreign_keys="[ChitAuction.chit_group_id]")
    bids = relationship("ChitAuctionBid", back_populates="auction", cascade="all, delete-orphan", foreign_keys="[ChitAuctionBid.chit_auction_id]")
    monthly_dues = relationship("MonthlyMemberDue", back_populates="auction", cascade="all, delete-orphan", foreign_keys="[MonthlyMemberDue.chit_auction_id]")

    __table_args__ = (
        UniqueConstraint('chit_group_id', 'auction_month_number', name='uq_chit_auctions_group_month'),
    )


class ChitAuctionBid(Base, AuditMixin):
    __tablename__ = "chit_auction_bids"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("organizers.id", ondelete="CASCADE"), nullable=False, index=True)
    chit_auction_id = Column(UUID(as_uuid=True), ForeignKey("chit_auctions.id", ondelete="CASCADE"), nullable=False, index=True)
    chit_group_id = Column(UUID(as_uuid=True), ForeignKey("chit_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    membership_id = Column(UUID(as_uuid=True), ForeignKey("chit_memberships.id", ondelete="CASCADE"), nullable=False, index=True)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True)

    bid_discount_amount = Column(Numeric(14, 2), nullable=False)
    remarks = Column(Text, nullable=True)
    bid_time = Column(DateTime, nullable=False, server_default=func.now())
    status = Column(String(20), nullable=False, default="ACTIVE", index=True)  # ACTIVE|WITHDRAWN|REJECTED

    auction = relationship("ChitAuction", back_populates="bids", foreign_keys="[ChitAuctionBid.chit_auction_id]")
    membership = relationship("ChitMembership", back_populates="auction_bids", foreign_keys="[ChitAuctionBid.membership_id]")

    __table_args__ = (
        UniqueConstraint('chit_auction_id', 'membership_id', name='uq_chit_auction_bids_auction_membership'),
    )


class MonthlyMemberDue(Base, AuditMixin):
    __tablename__ = "monthly_member_dues"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("organizers.id", ondelete="CASCADE"), nullable=False, index=True)
    chit_group_id = Column(UUID(as_uuid=True), ForeignKey("chit_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    chit_auction_id = Column(UUID(as_uuid=True), ForeignKey("chit_auctions.id", ondelete="CASCADE"), nullable=False, index=True)
    membership_id = Column(UUID(as_uuid=True), ForeignKey("chit_memberships.id", ondelete="CASCADE"), nullable=False, index=True)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True)

    month_number = Column(Integer, nullable=False)
    share_count = Column(Integer, nullable=False)

    gross_installment_amount = Column(Numeric(14, 2), nullable=False)
    bonus_per_share = Column(Numeric(14, 2), nullable=False)
    total_bonus_amount = Column(Numeric(14, 2), nullable=False)
    net_payable_amount = Column(Numeric(14, 2), nullable=False)

    total_paid_amount = Column(Numeric(14, 2), nullable=False, default=0)
    remaining_amount = Column(Numeric(14, 2), nullable=False)

    payment_status = Column(String(20), nullable=False, default="PENDING", index=True)  # PENDING|PARTIALLY_PAID|PAID|OVERDUE|WAIVED
    due_date = Column(Date, nullable=True)
    grace_period_end_date = Column(Date, nullable=True)
    last_payment_at = Column(DateTime, nullable=True)
    remarks = Column(Text, nullable=True)

    auction = relationship("ChitAuction", back_populates="monthly_dues", foreign_keys="[MonthlyMemberDue.chit_auction_id]")
    receipts = relationship("ChitPaymentReceipt", back_populates="monthly_due", cascade="all, delete-orphan", foreign_keys="[ChitPaymentReceipt.monthly_member_due_id]")

    __table_args__ = (
        UniqueConstraint('chit_auction_id', 'membership_id', name='uq_monthly_dues_auction_membership'),
    )


class ChitPaymentReceipt(Base, AuditMixin):
    __tablename__ = "chit_payment_receipts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("organizers.id", ondelete="CASCADE"), nullable=False, index=True)
    chit_group_id = Column(UUID(as_uuid=True), ForeignKey("chit_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    chit_auction_id = Column(UUID(as_uuid=True), ForeignKey("chit_auctions.id", ondelete="CASCADE"), nullable=False, index=True)
    monthly_member_due_id = Column(UUID(as_uuid=True), ForeignKey("monthly_member_dues.id", ondelete="CASCADE"), nullable=False, index=True)
    membership_id = Column(UUID(as_uuid=True), ForeignKey("chit_memberships.id", ondelete="CASCADE"), nullable=False, index=True)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True)

    receipt_number = Column(String(50), nullable=False)
    payment_date = Column(DateTime, nullable=False, server_default=func.now())
    payment_amount = Column(Numeric(14, 2), nullable=False)
    payment_method = Column(String(20), nullable=False, default="CASH") # CASH|UPI|BANK_TRANSFER|CARD|OTHER
    transaction_reference = Column(String(100), nullable=True)
    collected_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    remarks = Column(Text, nullable=True)

    status = Column(String(20), nullable=False, default="SUCCESS", index=True) # SUCCESS|REVERSED|CANCELLED
    reversal_reason = Column(Text, nullable=True)
    reversed_at = Column(DateTime, nullable=True)
    reversed_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reversal_receipt_id = Column(UUID(as_uuid=True), ForeignKey("chit_payment_receipts.id", ondelete="SET NULL"), nullable=True)

    client_request_id = Column(String(100), nullable=True, index=True)

    monthly_due = relationship("MonthlyMemberDue", back_populates="receipts", foreign_keys="[ChitPaymentReceipt.monthly_member_due_id]")
    collected_by_user = relationship("User", foreign_keys="[ChitPaymentReceipt.collected_by_user_id]")
    reversed_by_user = relationship("User", foreign_keys="[ChitPaymentReceipt.reversed_by_user_id]")
    reversed_receipt = relationship("ChitPaymentReceipt", remote_side=[id], foreign_keys="[ChitPaymentReceipt.reversal_receipt_id]")

    __table_args__ = (
        UniqueConstraint('organizer_id', 'receipt_number', name='uq_payment_receipts_organizer_receipt_number'),
        Index('idx_payment_receipts_client_request_id', 'organizer_id', 'client_request_id', unique=True, postgresql_where='client_request_id IS NOT NULL'),
    )


class PaymentReceiptSequence(Base):
    __tablename__ = "payment_receipt_sequences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("organizers.id", ondelete="CASCADE"), nullable=False, index=True)
    receipt_prefix = Column(String(20), nullable=False)
    current_sequence = Column(Integer, nullable=False, default=0)
    
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('organizer_id', 'receipt_prefix', name='uq_receipt_sequences_organizer_prefix'),
    )


class ChitWinnerPayout(Base, AuditMixin):
    __tablename__ = "chit_winner_payouts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("organizers.id", ondelete="CASCADE"), nullable=False, index=True)
    chit_group_id = Column(UUID(as_uuid=True), ForeignKey("chit_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    chit_auction_id = Column(UUID(as_uuid=True), ForeignKey("chit_auctions.id", ondelete="CASCADE"), nullable=False, index=True)
    winner_membership_id = Column(UUID(as_uuid=True), ForeignKey("chit_memberships.id", ondelete="CASCADE"), nullable=False, index=True)
    winner_member_id = Column(UUID(as_uuid=True), ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True)

    month_number = Column(Integer, nullable=False)

    gross_chit_amount = Column(Numeric(14, 2), nullable=False)
    winning_bid_discount_amount = Column(Numeric(14, 2), nullable=False)
    maintenance_charge_amount = Column(Numeric(14, 2), nullable=False)
    payout_amount = Column(Numeric(14, 2), nullable=False)

    collection_expected_amount = Column(Numeric(14, 2), nullable=False, default=0)
    collection_received_amount = Column(Numeric(14, 2), nullable=False, default=0)
    collection_pending_amount = Column(Numeric(14, 2), nullable=False, default=0)

    organizer_contribution_amount = Column(Numeric(14, 2), nullable=False, default=0)
    payout_source = Column(String(30), nullable=False, default="COLLECTION_ONLY") # COLLECTION_ONLY|ORGANIZER_CONTRIBUTION|MIXED

    payment_method = Column(String(30), nullable=False, default="BANK_TRANSFER") # CASH|UPI|BANK_TRANSFER|CHEQUE|OTHER
    transaction_reference = Column(String(100), nullable=True)
    payout_date = Column(Date, nullable=False)
    remarks = Column(Text, nullable=True)

    payout_receipt_number = Column(String(50), nullable=False)

    status = Column(String(30), nullable=False, default="DRAFT", index=True) # DRAFT|PENDING_PAYMENT|PAID|WINNER_CONFIRMED|REVERSED|CANCELLED

    proof_file_url = Column(Text, nullable=True)
    receipt_html_url = Column(Text, nullable=True)
    receipt_image_url = Column(Text, nullable=True)
    
    winner_confirmed_at = Column(DateTime, nullable=True)
    winner_confirmation_note = Column(Text, nullable=True)
    reversal_reason = Column(Text, nullable=True)
    reversed_at = Column(DateTime, nullable=True)
    reversed_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reversal_payout_id = Column(UUID(as_uuid=True), ForeignKey("chit_winner_payouts.id", ondelete="SET NULL"), nullable=True)

    client_request_id = Column(String(100), nullable=True, index=True)

    reversed_by_user = relationship("User", foreign_keys="[ChitWinnerPayout.reversed_by_user_id]")
    reversed_payout = relationship("ChitWinnerPayout", remote_side=[id], foreign_keys="[ChitWinnerPayout.reversal_payout_id]")
    
    __table_args__ = (
        UniqueConstraint('chit_group_id', 'month_number', name='uq_winner_payouts_group_month'),
        UniqueConstraint('organizer_id', 'payout_receipt_number', name='uq_winner_payouts_organizer_receipt'),
        Index('idx_winner_payouts_client_request_id', 'organizer_id', 'client_request_id', unique=True, postgresql_where='client_request_id IS NOT NULL'),
    )


class ChitMonthFinancialClosure(Base, AuditMixin):
    __tablename__ = "chit_month_financial_closures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("organizers.id", ondelete="CASCADE"), nullable=False, index=True)
    chit_group_id = Column(UUID(as_uuid=True), ForeignKey("chit_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    chit_auction_id = Column(UUID(as_uuid=True), ForeignKey("chit_auctions.id", ondelete="CASCADE"), nullable=False, index=True)
    month_number = Column(Integer, nullable=False)

    total_shares = Column(Integer, nullable=False)
    active_member_count = Column(Integer, nullable=False)

    gross_chit_amount = Column(Numeric(14, 2), nullable=False)
    winning_bid_discount_amount = Column(Numeric(14, 2), nullable=False)
    maintenance_charge_amount = Column(Numeric(14, 2), nullable=False)
    dividend_pool_amount = Column(Numeric(14, 2), nullable=False)
    dividend_per_share = Column(Numeric(14, 2), nullable=False)

    expected_collection_amount = Column(Numeric(14, 2), nullable=False, default=0)
    actual_collection_amount = Column(Numeric(14, 2), nullable=False, default=0)
    pending_collection_amount = Column(Numeric(14, 2), nullable=False, default=0)

    winner_payout_amount = Column(Numeric(14, 2), nullable=False, default=0)
    organizer_contribution_amount = Column(Numeric(14, 2), nullable=False, default=0)

    net_cash_position = Column(Numeric(14, 2), nullable=False, default=0)
    shortfall_amount = Column(Numeric(14, 2), nullable=False, default=0)
    surplus_amount = Column(Numeric(14, 2), nullable=False, default=0)

    closure_status = Column(String(30), nullable=False, default="OPEN", index=True) # OPEN|READY_FOR_CLOSURE|CLOSED|REOPENED
    closed_at = Column(DateTime, nullable=True)
    closed_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    remarks = Column(Text, nullable=True)

    closed_by_user = relationship("User", foreign_keys="[ChitMonthFinancialClosure.closed_by_user_id]")

    __table_args__ = (
        UniqueConstraint('chit_group_id', 'month_number', name='uq_financial_closures_group_month'),
    )


class ChitWinnerPayoutActivityLog(Base):
    __tablename__ = "chit_winner_payout_activity_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("organizers.id", ondelete="CASCADE"), nullable=False, index=True)
    winner_payout_id = Column(UUID(as_uuid=True), ForeignKey("chit_winner_payouts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    action_type = Column(String(50), nullable=False, index=True)
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
    remarks = Column(Text, nullable=True)
    
    performed_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)

    organizer = relationship("Organizer", foreign_keys="[ChitWinnerPayoutActivityLog.organizer_id]")
    winner_payout = relationship("ChitWinnerPayout", foreign_keys="[ChitWinnerPayoutActivityLog.winner_payout_id]")
    performed_by_user = relationship("User", foreign_keys="[ChitWinnerPayoutActivityLog.performed_by_user_id]")

