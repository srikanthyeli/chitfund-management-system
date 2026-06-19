from sqlalchemy import Column, Integer, String, Boolean, DateTime, DECIMAL, ForeignKey, Text, JSON, Date, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class AuditMixin:
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    version = Column(Integer, nullable=False, default=1)

class User(Base, AuditMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mobile = Column(String(15), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    otp_enabled = Column(Boolean, nullable=False, default=True)
    role = Column(String(20), nullable=False, default="MEMBER", index=True)
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationships
    organizer = relationship("Organizer", back_populates="user", uselist=False)
    member = relationship("Member", back_populates="user", uselist=False)

class Organizer(Base, AuditMixin):
    __tablename__ = "organizers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    mobile = Column(String(15), nullable=False)

    # Relationships
    user = relationship("User", back_populates="organizer")
    chit_groups = relationship("ChitGroup", back_populates="organizer")

class Member(Base, AuditMixin):
    __tablename__ = "members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    mobile = Column(String(15), nullable=False)
    address = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="ACTIVE", index=True)

    # Relationships
    user = relationship("User", back_populates="member")
    memberships = relationship("ChitMembership", back_populates="member")
    bids = relationship("Bid", back_populates="member")
    collections = relationship("Collection", back_populates="member")
    passbook_entries = relationship("PassbookEntry", back_populates="member")

class ChitGroup(Base, AuditMixin):
    __tablename__ = "chit_groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("organizers.id", ondelete="RESTRICT"), nullable=False)
    name = Column(String(100), nullable=False)
    duration_months = Column(Integer, nullable=False)
    member_count = Column(Integer, nullable=False, default=0)
    monthly_amount = Column(DECIMAL(12, 2), nullable=False)
    maintenance_charge = Column(DECIMAL(12, 2), nullable=False)
    start_date = Column(Date, nullable=True)
    status = Column(String(20), nullable=False, default="DRAFT", index=True)

    # Relationships
    organizer = relationship("Organizer", back_populates="chit_groups")
    memberships = relationship("ChitMembership", back_populates="chit_group")
    auctions = relationship("Auction", back_populates="chit_group")

class ChitMembership(Base, AuditMixin):
    __tablename__ = "chit_memberships"
    __table_args__ = (
        UniqueConstraint("chit_group_id", "member_id", name="uq_chit_group_member_orm"),
        UniqueConstraint("chit_group_id", "position_no", name="uq_chit_group_position_orm"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chit_group_id = Column(UUID(as_uuid=True), ForeignKey("chit_groups.id", ondelete="CASCADE"), nullable=False)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id", ondelete="RESTRICT"), nullable=False)
    join_date = Column(DateTime, nullable=False, server_default=func.now())
    position_no = Column(Integer, nullable=False)
    won_status = Column(Boolean, nullable=False, default=False)

    # Relationships
    chit_group = relationship("ChitGroup", back_populates="memberships")
    member = relationship("Member", back_populates="memberships")

class Auction(Base, AuditMixin):
    __tablename__ = "auctions"
    __table_args__ = (
        UniqueConstraint("chit_group_id", "month_no", name="uq_group_month_auction_orm"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chit_group_id = Column(UUID(as_uuid=True), ForeignKey("chit_groups.id", ondelete="RESTRICT"), nullable=False)
    month_no = Column(Integer, nullable=False)
    winner_member_id = Column(UUID(as_uuid=True), ForeignKey("members.id", ondelete="RESTRICT"), nullable=True)
    bid_amount = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    bonus_per_member = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    winner_receivable = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    auction_date = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    chit_group = relationship("ChitGroup", back_populates="auctions")
    winner = relationship("Member")
    bids = relationship("Bid", back_populates="auction")
    collections = relationship("Collection", back_populates="auction")

class Bid(Base, AuditMixin):
    __tablename__ = "bids"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auction_id = Column(UUID(as_uuid=True), ForeignKey("auctions.id", ondelete="CASCADE"), nullable=False)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id", ondelete="RESTRICT"), nullable=False)
    bid_amount = Column(DECIMAL(12, 2), nullable=False)

    # Relationships
    auction = relationship("Auction", back_populates="bids")
    member = relationship("Member", back_populates="bids")

class Collection(Base, AuditMixin):
    __tablename__ = "collections"
    __table_args__ = (
        UniqueConstraint("auction_id", "member_id", name="uq_auction_member_collection_orm"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auction_id = Column(UUID(as_uuid=True), ForeignKey("auctions.id", ondelete="RESTRICT"), nullable=False)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id", ondelete="RESTRICT"), nullable=False)
    payable_amount = Column(DECIMAL(12, 2), nullable=False)
    paid_amount = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    penalty_amount = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    payment_date = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default="UNPAID", index=True)

    # Relationships
    auction = relationship("Auction", back_populates="collections")
    member = relationship("Member", back_populates="collections")
    passbook_entry = relationship("PassbookEntry", back_populates="collection", uselist=False)

class PassbookEntry(Base, AuditMixin):
    __tablename__ = "passbook_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collection_id = Column(UUID(as_uuid=True), ForeignKey("collections.id", ondelete="CASCADE"), unique=True, nullable=False)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id", ondelete="RESTRICT"), nullable=False)
    month_no = Column(Integer, nullable=False)
    installment = Column(DECIMAL(12, 2), nullable=False)
    bonus = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    payable = Column(DECIMAL(12, 2), nullable=False)
    entry_date = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    collection = relationship("Collection", back_populates="passbook_entry")
    member = relationship("Member", back_populates="passbook_entries")

class AuditLog(Base, AuditMixin):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_name = Column(String(100), nullable=False)
    record_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String(50), nullable=False)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    user = relationship("User")
