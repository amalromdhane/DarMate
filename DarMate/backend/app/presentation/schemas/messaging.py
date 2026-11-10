from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.entities.enums import ConversationType, NotificationType
from app.presentation.schemas.common import ORM


class OpenConversationIn(BaseModel):
    user_id: int


class MessageIn(BaseModel):
    body: str | None = Field(default=None, max_length=4000)
    property_id: int | None = None


class AttachmentOut(ORM):
    id: int
    original_name: str
    mime_type: str
    size_bytes: int


class MessageOut(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    body: str | None
    property_id: int | None
    created_at: datetime | None
    status: str
    attachments: list[AttachmentOut]


class ConversationOut(BaseModel):
    id: int
    type: ConversationType
    title: str
    member_ids: list[int]
    last_message: MessageOut | None
    unread_count: int


class NotificationOut(ORM):
    id: int
    type: NotificationType
    title: str
    body: str | None
    link: str | None
    is_read: bool
    created_at: datetime | None


class NotificationListOut(BaseModel):
    items: list[NotificationOut]
    unread_count: int
