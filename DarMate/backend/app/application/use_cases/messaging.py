from app.application.dto.dto import Actor, ConversationView, MessageView
from app.application.interfaces.services import FileStorage, RealtimePublisher, UnitOfWork, UploadedFile
from app.application.use_cases.common import AccessGuard, NotificationService, UserDirectory
from app.application.use_cases.properties import PropertyAccess
from app.application.use_cases.users import DOC_MIMES, IMAGE_MIMES
from app.core.clock import utcnow
from app.core.config import settings
from app.core.exceptions import ForbiddenError, NotFoundError, ValidationFailedError
from app.domain.entities import entities as e
from app.domain.entities.enums import ConversationType, NotificationType
from app.domain.repositories import ports

ATTACHMENT_MIMES = {**IMAGE_MIMES, **DOC_MIMES}
MAX_BODY = 4000


class ConversationAccess:
    def __init__(self, conversations: ports.ConversationRepository, members: ports.ConversationMemberRepository) -> None:
        self.conversations, self.members = conversations, members

    def member_ids(self, conversation_id: int) -> list[int]:
        return [m.user_id for m in self.members.list_for_conversation(conversation_id)]

    def load(self, actor: Actor, conversation_id: int) -> tuple[e.Conversation, e.ConversationMember]:
        conv, me = self.conversations.get(conversation_id), self.members.find(conversation_id, actor.id)
        if conv is None or me is None:
            raise NotFoundError("Conversation introuvable.")
        return conv, me


class OpenPrivateConversation:
    def __init__(self, conversations: ports.ConversationRepository, members: ports.ConversationMemberRepository,
                 guard: AccessGuard, directory: UserDirectory, uow: UnitOfWork) -> None:
        self.conversations, self.members, self.guard, self.directory, self.uow = conversations, members, guard, directory, uow

    def execute(self, actor: Actor, other_id: int) -> e.Conversation:
        if other_id == actor.id:
            raise ValidationFailedError("Vous ne pouvez pas discuter avec vous-même.")
        self.directory.require_active(other_id)
        self.guard.ensure_not_blocked(actor.id, other_id)
        key = f"{min(actor.id, other_id)}:{max(actor.id, other_id)}"
        conv = self.conversations.get_by_private_key(key)
        if conv is None:
            conv = self.conversations.add(e.Conversation(type=ConversationType.PRIVATE, private_key=key))
            for uid in (actor.id, other_id):
                self.members.add(e.ConversationMember(conversation_id=conv.id, user_id=uid))
            self.uow.commit()
        return conv


class ListConversations:
    def __init__(self, conversations: ports.ConversationRepository, access: ConversationAccess, messages: ports.MessageRepository,
                 members: ports.ConversationMemberRepository, groups: ports.GroupRepository, directory: UserDirectory) -> None:
        self.conversations, self.access, self.messages, self.members, self.groups, self.directory = conversations, access, messages, members, groups, directory

    def execute(self, actor: Actor) -> list[ConversationView]:
        out = []
        for c in self.conversations.list_for_user(actor.id):
            ids = self.access.member_ids(c.id)
            if c.type == ConversationType.GROUP:
                g = self.groups.get(c.group_id)
                title = g.name if g else "Groupe"
            else:
                title = self.directory.name_of(next((i for i in ids if i != actor.id), actor.id))
            me = self.members.find(c.id, actor.id)
            out.append(ConversationView(c, title, ids, self.messages.last_message(c.id),
                                        self.messages.unread_count(c.id, actor.id, me.last_read_at)))
        out.sort(key=lambda v: (v.last_message.id if v.last_message else 0), reverse=True)
        return out


class GetMessages:
    def __init__(self, access: ConversationAccess, messages: ports.MessageRepository,
                 attachments: ports.MessageAttachmentRepository) -> None:
        self.access, self.messages, self.attachments = access, messages, attachments

    def execute(self, actor: Actor, conversation_id: int, before_id: int | None = None, limit: int = 50) -> list[MessageView]:
        self.access.load(actor, conversation_id)
        rows = self.messages.list_for_conversation(conversation_id, before_id, min(max(limit, 1), 100))
        att = self.attachments.list_for_messages([m.id for m in rows])
        others = [m for m in self.access.members.list_for_conversation(conversation_id) if m.user_id != actor.id]
        out = []
        for m in rows:
            read = bool(others) and all(o.last_read_at and o.last_read_at >= m.created_at for o in others)
            out.append(MessageView(m, att[m.id], "read" if read else "sent"))
        return out


class SendMessage:
    def __init__(self, access: ConversationAccess, messages: ports.MessageRepository,
                 attachments: ports.MessageAttachmentRepository, props: PropertyAccess, guard: AccessGuard,
                 storage: FileStorage, notifications: NotificationService, directory: UserDirectory,
                 realtime: RealtimePublisher, uow: UnitOfWork) -> None:
        self.access, self.messages, self.attachments, self.props, self.guard = access, messages, attachments, props, guard
        self.storage, self.notifications, self.directory, self.realtime, self.uow = storage, notifications, directory, realtime, uow

    def execute(self, actor: Actor, conversation_id: int, body: str | None = None, property_id: int | None = None,
                file: UploadedFile | None = None) -> MessageView:
        conv, me = self.access.load(actor, conversation_id)
        body = (body or "").strip() or None
        if not (body or property_id or file):
            raise ValidationFailedError("Le message est vide.")
        if body and len(body) > MAX_BODY:
            raise ValidationFailedError(f"Message trop long (maximum {MAX_BODY} caractères).")
        member_ids = self.access.member_ids(conversation_id)
        if conv.type == ConversationType.PRIVATE:
            other = next(i for i in member_ids if i != actor.id)
            self.guard.ensure_not_blocked(actor.id, other)
        if property_id:
            self.props.visible(property_id, actor.id)
        msg = self.messages.add(e.Message(conversation_id=conversation_id, sender_id=actor.id, body=body, property_id=property_id))
        atts = []
        if file:
            path = self.storage.save(f"messages/{conversation_id}", file, ATTACHMENT_MIMES,
                                     settings.max_document_mb * 1024 * 1024, private=True)
            atts.append(self.attachments.add(e.MessageAttachment(
                message_id=msg.id, path=path, original_name=(file.filename or "fichier")[:255],
                mime_type=file.content_type, size_bytes=len(file.data))))
        me.last_read_at = msg.created_at
        self.access.members.update(me)
        sender = self.directory.name_of(actor.id)
        for uid in member_ids:
            if uid != actor.id:
                self.notifications.notify(uid, NotificationType.MESSAGE, f"Nouveau message de {sender}",
                                          (body or "Pièce jointe / annonce partagée")[:120], f"/messages/{conversation_id}")
        self.uow.commit()
        view = MessageView(msg, atts, "sent")
        self.realtime.publish_message(member_ids, {
            "type": "message", "conversation_id": conversation_id, "id": msg.id, "sender_id": actor.id,
            "body": msg.body, "property_id": property_id, "created_at": msg.created_at.isoformat() if msg.created_at else None,
            "attachments": [{"id": a.id, "name": a.original_name, "mime_type": a.mime_type} for a in atts]})
        return view


class MarkConversationRead:
    def __init__(self, access: ConversationAccess, realtime: RealtimePublisher, uow: UnitOfWork) -> None:
        self.access, self.realtime, self.uow = access, realtime, uow

    def execute(self, actor: Actor, conversation_id: int) -> None:
        _, me = self.access.load(actor, conversation_id)
        me.last_read_at = utcnow()
        self.access.members.update(me)
        self.uow.commit()
        self.realtime.publish_message(self.access.member_ids(conversation_id),
                                      {"type": "read", "conversation_id": conversation_id, "user_id": actor.id})


class DownloadAttachment:
    def __init__(self, attachments: ports.MessageAttachmentRepository, messages: ports.MessageRepository,
                 access: ConversationAccess, storage: FileStorage) -> None:
        self.attachments, self.messages, self.access, self.storage = attachments, messages, access, storage

    def execute(self, actor: Actor, attachment_id: int) -> tuple[bytes, e.MessageAttachment]:
        att = self.attachments.get(attachment_id)
        msg = self.messages.get(att.message_id) if att else None
        if att is None or msg is None:
            raise NotFoundError("Fichier introuvable.")
        self.access.load(actor, msg.conversation_id)  # 404 si non membre
        return self.storage.read(att.path), att
