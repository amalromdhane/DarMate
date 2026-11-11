from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.entities.enums import RequestStatus
from app.infrastructure.database.base import PK, Base, created, pk

_status = lambda: mapped_column(Enum(RequestStatus, native_enum=False, length=20), default=RequestStatus.PENDING)  # noqa: E731


class RoommateProfileModel(Base):
    __tablename__ = "roommate_profile"
    id: Mapped[int] = pk()
    user_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="CASCADE"), unique=True)
    city_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("city.id", ondelete="SET NULL"), index=True)
    budget_min: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    budget_max: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    smoker: Mapped[bool] = mapped_column(Boolean, default=False)
    has_pets: Mapped[bool] = mapped_column(Boolean, default=False)
    schedule: Mapped[str] = mapped_column(String(20), default="FLEXIBLE")
    cleanliness: Mapped[int] = mapped_column(Integer, default=3)
    sociability: Mapped[int] = mapped_column(Integer, default=3)
    about: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    looking_for: Mapped[str] = mapped_column(String(10), default="ROOM")   # ROOM | HOUSE

class RoommateRequestModel(Base):
    __tablename__ = "roommate_request"
    __table_args__ = (UniqueConstraint("sender_id", "receiver_id"),)
    id: Mapped[int] = pk()
    sender_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="CASCADE"))
    receiver_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="CASCADE"), index=True)
    message: Mapped[str | None] = mapped_column(Text)
    status: Mapped[RequestStatus] = _status()
    created_at: Mapped[datetime] = created()


class RoommateGroupModel(Base):
    __tablename__ = "roommate_group"
    id: Mapped[int] = pk()
    name: Mapped[str] = mapped_column(String(100))
    creator_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="RESTRICT"))
    max_members: Mapped[int] = mapped_column(Integer, default=4)
    created_at: Mapped[datetime] = created()


class GroupMemberModel(Base):
    __tablename__ = "group_member"
    __table_args__ = (UniqueConstraint("group_id", "user_id"),)
    id: Mapped[int] = pk()
    group_id: Mapped[int] = mapped_column(PK, ForeignKey("roommate_group.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(10), default="MEMBER")
    joined_at: Mapped[datetime] = created()


class GroupInvitationModel(Base):
    __tablename__ = "group_invitation"
    __table_args__ = (UniqueConstraint("group_id", "invitee_id", "status"),)
    id: Mapped[int] = pk()
    group_id: Mapped[int] = mapped_column(PK, ForeignKey("roommate_group.id", ondelete="CASCADE"))
    inviter_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="CASCADE"))
    invitee_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="CASCADE"), index=True)
    status: Mapped[RequestStatus] = _status()
    created_at: Mapped[datetime] = created()
