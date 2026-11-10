from datetime import datetime

from sqlalchemy import func, select, update

from app.domain.entities import entities as e
from app.domain.repositories import ports
from app.infrastructure.models.messaging import (
    ConversationMemberModel, ConversationModel, MessageAttachmentModel, MessageModel, NotificationModel,
)
from app.infrastructure.repositories.base import SqlRepository


class SqlConversationRepository(SqlRepository[e.Conversation], ports.ConversationRepository):
    model, entity = ConversationModel, e.Conversation

    def get_by_private_key(self, key):
        return self._first(select(ConversationModel).where(ConversationModel.private_key == key))

    def get_by_group(self, group_id):
        return self._first(select(ConversationModel).where(ConversationModel.group_id == group_id))

    def list_for_user(self, user_id):
        stmt = (select(ConversationModel).join(ConversationMemberModel, ConversationMemberModel.conversation_id == ConversationModel.id)
                .where(ConversationMemberModel.user_id == user_id).order_by(ConversationModel.id.desc()))
        return self._all(stmt)


class SqlConversationMemberRepository(SqlRepository[e.ConversationMember], ports.ConversationMemberRepository):
    model, entity = ConversationMemberModel, e.ConversationMember

    def list_for_conversation(self, conversation_id):
        return self._all(select(ConversationMemberModel).where(ConversationMemberModel.conversation_id == conversation_id))

    def find(self, conversation_id, user_id):
        return self._first(select(ConversationMemberModel).where(
            ConversationMemberModel.conversation_id == conversation_id, ConversationMemberModel.user_id == user_id))


class SqlMessageRepository(SqlRepository[e.Message], ports.MessageRepository):
    model, entity = MessageModel, e.Message

    def list_for_conversation(self, conversation_id, before_id, limit):
        stmt = select(MessageModel).where(MessageModel.conversation_id == conversation_id)
        if before_id:
            stmt = stmt.where(MessageModel.id < before_id)
        rows = self._all(stmt.order_by(MessageModel.id.desc()).limit(limit))
        return list(reversed(rows))

    def last_message(self, conversation_id):
        return self._first(select(MessageModel).where(MessageModel.conversation_id == conversation_id).order_by(MessageModel.id.desc()).limit(1))

    def unread_count(self, conversation_id, user_id, since):
        stmt = select(func.count()).select_from(MessageModel).where(
            MessageModel.conversation_id == conversation_id, MessageModel.sender_id != user_id)
        if since:
            stmt = stmt.where(MessageModel.created_at > since)
        return self.s.execute(stmt).scalar_one()


class SqlMessageAttachmentRepository(SqlRepository[e.MessageAttachment], ports.MessageAttachmentRepository):
    model, entity = MessageAttachmentModel, e.MessageAttachment

    def list_for_messages(self, ids):
        out: dict[int, list[e.MessageAttachment]] = {i: [] for i in ids}
        if ids:
            for a in self._all(select(MessageAttachmentModel).where(MessageAttachmentModel.message_id.in_(ids))):
                out[a.message_id].append(a)
        return out


class SqlNotificationRepository(SqlRepository[e.Notification], ports.NotificationRepository):
    model, entity = NotificationModel, e.Notification

    def list_for_user(self, user_id, unread_only, limit):
        stmt = select(NotificationModel).where(NotificationModel.user_id == user_id)
        if unread_only:
            stmt = stmt.where(NotificationModel.is_read.is_(False))
        return self._all(stmt.order_by(NotificationModel.id.desc()).limit(limit))

    def mark_all_read(self, user_id):
        self.s.execute(update(NotificationModel).where(NotificationModel.user_id == user_id).values(is_read=True))

    def unread_count(self, user_id):
        return self.s.execute(select(func.count()).select_from(NotificationModel).where(
            NotificationModel.user_id == user_id, NotificationModel.is_read.is_(False))).scalar_one()
