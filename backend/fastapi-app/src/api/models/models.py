import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.shared.core.base_model import Base
from src.shared.core.audit import AuditMixin

class User(Base, AuditMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mobile = Column(String(15), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    otp_enabled = Column(Boolean, nullable=False, default=True)
    role = Column(String(20), nullable=False, default="MEMBER", index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    organizer = relationship("Organizer", back_populates="user", uselist=False, cascade="all, delete-orphan", foreign_keys="[Organizer.user_id]")
    member = relationship("Member", back_populates="user", uselist=False, cascade="all, delete-orphan", foreign_keys="[Member.user_id]")


class Organizer(Base, AuditMixin):
    __tablename__ = "organizers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    mobile = Column(String(15), nullable=False)

    # Relationships
    user = relationship("User", back_populates="organizer", foreign_keys="[Organizer.user_id]")
    # Future relationship:
    # chit_groups = relationship("ChitGroup", back_populates="organizer")


class Member(Base, AuditMixin):
    __tablename__ = "members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    mobile = Column(String(15), nullable=False)
    address = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="ACTIVE", index=True)

    # Relationships
    user = relationship("User", back_populates="member", foreign_keys="[Member.user_id]")
    # Future relationships:
    # memberships = relationship("ChitMembership", back_populates="member")
    # bids = relationship("Bid", back_populates="member")
    # collections = relationship("Collection", back_populates="member")
    # passbook_entries = relationship("PassbookEntry", back_populates="member")
