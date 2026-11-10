from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.entities.enums import ConversationType, NotificationType
from app.infrastructure.database.base import PK, Base, created, pk


class ConversationModel(Base):
    __tablename__ = "conversation"
    id: Mapped[int] = pk()
    type: Mapped[ConversationType] = mapped_column(Enum(ConversationType, native_enum=False, length=10))
    group_id: Mapped[int | None] = mapped_column(PK, ForeignKey("roommate_group.id", ondelete="CASCADE"), unique=True)
    private_key: Mapped[str | None] = mapped_column(String(50), unique=True)
    created_at: Mapped[datetime] = created()


class ConversationMemberModel(Base):
    __tablename__ = "conversation_member"
    __table_args__ = (UniqueConstraint("conversation_id", "user_id"),)
    id: Mapped[int] = pk()
    conversation_id: Mapped[int] = mapped_column(PK, ForeignKey("conversation.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="CASCADE"), index=True)
    last_read_at: Mapped[datetime | None] = mapped_column(DateTime)


class MessageModel(Base):
    __tablename__ = "message"
    __table_args__ = (Index("ix_message_conv_created", "conversation_id", "created_at"),)
    id: Mapped[int] = pk()
    conversation_id: Mapped[int] = mapped_column(PK, ForeignKey("conversation.id", ondelete="CASCADE"))
    sender_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="RESTRICT"))
    body: Mapped[str | None] = mapped_column(Text)
    property_id: Mapped[int | None] = mapped_column(PK, ForeignKey("property.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = created()


class MessageAttachmentModel(Base):
    __tablename__ = "message_attachment"
    id: Mapped[int] = pk()
    message_id: Mapped[int] = mapped_column(PK, ForeignKey("message.id", ondelete="CASCADE"), index=True)
    path: Mapped[str] = mapped_column(String(255))
    original_name: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(Integer)


class NotificationModel(Base):
    __tablename__ = "notification"
    __table_args__ = (Index("ix_notification_user_read", "user_id", "is_read"),)
    id: Mapped[int] = pk()
    user_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="CASCADE"))
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType, native_enum=False, length=30))
    title: Mapped[str] = mapped_column(String(150))
    body: Mapped[str | None] = mapped_column(Text)
    link: Mapped[str | None] = mapped_column(String(255))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = created()
