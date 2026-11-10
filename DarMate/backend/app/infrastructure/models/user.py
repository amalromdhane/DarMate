from datetime import date, datetime

from sqlalchemy import JSON, Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.entities.enums import DocumentStatus, ReportStatus, UserStatus
from app.infrastructure.database.base import PK, Base, created, pk


class RoleModel(Base):
    __tablename__ = "role"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)


class UserModel(Base):
    __tablename__ = "user"
    id: Mapped[int] = pk()
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus, native_enum=False, length=20), default=UserStatus.ACTIVE, index=True)
    failed_login_count: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = created()
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class UserRoleModel(Base):
    __tablename__ = "user_role"
    user_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("role.id", ondelete="CASCADE"), primary_key=True)


class UserProfileModel(Base):
    __tablename__ = "user_profile"
    id: Mapped[int] = pk()
    user_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="CASCADE"), unique=True)
    first_name: Mapped[str] = mapped_column(String(80), default="")
    last_name: Mapped[str] = mapped_column(String(80), default="")
    phone: Mapped[str | None] = mapped_column(String(30))
    bio: Mapped[str | None] = mapped_column(Text)
    birth_date: Mapped[date | None] = mapped_column(Date)
    city_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("city.id", ondelete="SET NULL"))
    language: Mapped[str] = mapped_column(String(5), default="fr")


class RefreshTokenModel(Base):
    __tablename__ = "refresh_token"
    id: Mapped[int] = pk()
    user_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = created()


class PasswordResetTokenModel(Base):
    __tablename__ = "password_reset_token"
    id: Mapped[int] = pk()
    user_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    used_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = created()


class IdentityDocumentModel(Base):
    __tablename__ = "identity_document"
    id: Mapped[int] = pk()
    user_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="CASCADE"), index=True)
    path: Mapped[str] = mapped_column(String(255))
    doc_type: Mapped[str] = mapped_column(String(30), default="ID_CARD")
    status: Mapped[DocumentStatus] = mapped_column(Enum(DocumentStatus, native_enum=False, length=20), default=DocumentStatus.PENDING)
    created_at: Mapped[datetime] = created()


class UserBlockModel(Base):
    __tablename__ = "user_block"
    __table_args__ = (UniqueConstraint("blocker_id", "blocked_id"),)
    id: Mapped[int] = pk()
    blocker_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="CASCADE"))
    blocked_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="CASCADE"))


class AuditLogModel(Base):
    __tablename__ = "audit_log"
    id: Mapped[int] = pk()
    user_id: Mapped[int | None] = mapped_column(PK, ForeignKey("user.id", ondelete="SET NULL"), index=True)
    action: Mapped[str] = mapped_column(String(80), index=True)
    entity_type: Mapped[str | None] = mapped_column(String(50))
    entity_id: Mapped[int | None] = mapped_column(PK)
    details: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = created()


class ReportModel(Base):
    __tablename__ = "report"
    id: Mapped[int] = pk()
    reporter_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="CASCADE"))
    reported_user_id: Mapped[int | None] = mapped_column(PK, ForeignKey("user.id", ondelete="SET NULL"))
    message_id: Mapped[int | None] = mapped_column(PK)
    reason: Mapped[str] = mapped_column(String(100))
    details: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ReportStatus] = mapped_column(Enum(ReportStatus, native_enum=False, length=20), default=ReportStatus.OPEN)
    created_at: Mapped[datetime] = created()


class ApplicationSettingModel(Base):
    __tablename__ = "application_setting"
    id: Mapped[int] = pk()
    key: Mapped[str] = mapped_column("setting_key", String(100), unique=True)
    value: Mapped[str] = mapped_column(Text)
