from app.application.dto.dto import Actor, GroupView
from app.application.interfaces.services import UnitOfWork
from app.application.use_cases.common import AccessGuard, AuditService, NotificationService, UserDirectory
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationFailedError
from app.domain.entities import entities as e
from app.domain.entities.enums import ConversationType, NotificationType, RequestStatus
from app.domain.repositories import ports


class GroupAccess:
    def __init__(self, groups: ports.GroupRepository, members: ports.GroupMemberRepository) -> None:
        self.groups, self.members = groups, members

    def member_group(self, actor: Actor, group_id: int) -> tuple[e.RoommateGroup, e.GroupMember]:
        group, member = self.groups.get(group_id), self.members.find(group_id, actor.id)
        if group is None or member is None:
            raise NotFoundError("Groupe introuvable.")
        return group, member

    def admin_group(self, actor: Actor, group_id: int) -> e.RoommateGroup:
        group, member = self.member_group(actor, group_id)
        if member.role != "ADMIN":
            raise ForbiddenError("Seul l'administrateur du groupe peut effectuer cette action.")
        return group


class BuildGroupView:
    def __init__(self, members: ports.GroupMemberRepository, conversations: ports.ConversationRepository,
                 directory: UserDirectory) -> None:
        self.members, self.conversations, self.directory = members, conversations, directory

    def execute(self, group: e.RoommateGroup) -> GroupView:
        conv = self.conversations.get_by_group(group.id)
        return GroupView(group, [(m, self.directory.name_of(m.user_id)) for m in self.members.list_for_group(group.id)],
                         conv.id if conv else None)


class CreateGroup:
    def __init__(self, groups: ports.GroupRepository, members: ports.GroupMemberRepository,
                 conversations: ports.ConversationRepository, conv_members: ports.ConversationMemberRepository,
                 views: BuildGroupView, audit: AuditService, uow: UnitOfWork) -> None:
        self.groups, self.members, self.conversations, self.conv_members = groups, members, conversations, conv_members
        self.views, self.audit, self.uow = views, audit, uow

    def execute(self, actor: Actor, name: str, max_members: int = 4) -> GroupView:
        if not 2 <= max_members <= 10:
            raise ValidationFailedError("Un groupe compte entre 2 et 10 membres.")
        group = self.groups.add(e.RoommateGroup(name=name.strip(), creator_id=actor.id, max_members=max_members))
        self.members.add(e.GroupMember(group_id=group.id, user_id=actor.id, role="ADMIN"))
        conv = self.conversations.add(e.Conversation(type=ConversationType.GROUP, group_id=group.id))
        self.conv_members.add(e.ConversationMember(conversation_id=conv.id, user_id=actor.id))
        self.audit.log(actor.id, "group.create", "group", group.id)
        self.uow.commit()  # transaction unique : groupe + membre + conversation
        return self.views.execute(group)


class ListMyGroups:
    def __init__(self, groups: ports.GroupRepository, views: BuildGroupView) -> None:
        self.groups, self.views = groups, views

    def execute(self, actor: Actor) -> list[GroupView]:
        return [self.views.execute(g) for g in self.groups.list_for_user(actor.id)]


class GetGroup:
    def __init__(self, access: GroupAccess, views: BuildGroupView) -> None:
        self.access, self.views = access, views

    def execute(self, actor: Actor, group_id: int) -> GroupView:
        return self.views.execute(self.access.member_group(actor, group_id)[0])


class InviteToGroup:
    def __init__(self, access: GroupAccess, members: ports.GroupMemberRepository, invitations: ports.GroupInvitationRepository,
                 guard: AccessGuard, directory: UserDirectory, notifications: NotificationService, uow: UnitOfWork) -> None:
        self.access, self.members, self.invitations, self.guard = access, members, invitations, guard
        self.directory, self.notifications, self.uow = directory, notifications, uow

    def execute(self, actor: Actor, group_id: int, invitee_id: int) -> e.GroupInvitation:
        group = self.access.admin_group(actor, group_id)
        self.directory.require_active(invitee_id)
        self.guard.ensure_not_blocked(actor.id, invitee_id)
        if self.members.find(group_id, invitee_id):
            raise ConflictError("Cette personne fait déjà partie du groupe.")
        if self.invitations.find_pending(group_id, invitee_id):
            raise ConflictError("Une invitation est déjà en attente pour cette personne.")
        if len(self.members.list_for_group(group_id)) >= group.max_members:
            raise ConflictError("Le groupe a atteint sa taille maximale.")
        inv = self.invitations.add(e.GroupInvitation(group_id=group_id, inviter_id=actor.id, invitee_id=invitee_id))
        self.notifications.notify(invitee_id, NotificationType.GROUP_INVITATION, "Invitation à rejoindre un groupe",
                                  f"{self.directory.name_of(actor.id)} vous invite dans « {group.name} ».", "/groups/invitations")
        self.uow.commit()
        return inv


class ListMyInvitations:
    def __init__(self, invitations: ports.GroupInvitationRepository) -> None:
        self.invitations = invitations

    def execute(self, actor: Actor) -> list[e.GroupInvitation]:
        return self.invitations.list_for_invitee(actor.id)


class RespondGroupInvitation:
    def __init__(self, invitations: ports.GroupInvitationRepository, groups: ports.GroupRepository,
                 members: ports.GroupMemberRepository, conversations: ports.ConversationRepository,
                 conv_members: ports.ConversationMemberRepository, notifications: NotificationService,
                 directory: UserDirectory, uow: UnitOfWork) -> None:
        self.invitations, self.groups, self.members, self.conversations, self.conv_members = invitations, groups, members, conversations, conv_members
        self.notifications, self.directory, self.uow = notifications, directory, uow

    def execute(self, actor: Actor, invitation_id: int, accept: bool) -> e.GroupInvitation:
        inv = self.invitations.get(invitation_id)
        if inv is None or inv.invitee_id != actor.id:
            raise NotFoundError("Invitation introuvable.")
        if inv.status != RequestStatus.PENDING:
            raise ConflictError("Cette invitation a déjà reçu une réponse.")
        group = self.groups.get(inv.group_id)
        if accept:
            if len(self.members.list_for_group(group.id)) >= group.max_members:
                raise ConflictError("Le groupe est complet.")
            self.members.add(e.GroupMember(group_id=group.id, user_id=actor.id))
            conv = self.conversations.get_by_group(group.id)
            if conv:
                self.conv_members.add(e.ConversationMember(conversation_id=conv.id, user_id=actor.id))
        inv.status = RequestStatus.ACCEPTED if accept else RequestStatus.REJECTED
        self.invitations.update(inv)
        self.notifications.notify(inv.inviter_id, NotificationType.GROUP_INVITATION,
                                  "Invitation acceptée" if accept else "Invitation refusée",
                                  f"{self.directory.name_of(actor.id)} a {'rejoint' if accept else 'décliné'} « {group.name} ».",
                                  f"/groups/{group.id}")
        self.uow.commit()
        return inv


class RemoveGroupMember:
    """Quitter un groupe (soi-même) ou retirer un membre (administrateur du groupe)."""

    def __init__(self, access: GroupAccess, groups: ports.GroupRepository, members: ports.GroupMemberRepository,
                 conversations: ports.ConversationRepository, conv_members: ports.ConversationMemberRepository,
                 uow: UnitOfWork) -> None:
        self.access, self.groups, self.members, self.conversations, self.conv_members, self.uow = access, groups, members, conversations, conv_members, uow

    def execute(self, actor: Actor, group_id: int, user_id: int) -> None:
        group, me = self.access.member_group(actor, group_id)
        if user_id != actor.id and me.role != "ADMIN":
            raise ForbiddenError("Seul l'administrateur du groupe peut retirer un membre.")
        target = self.members.find(group_id, user_id)
        if target is None:
            raise NotFoundError("Membre introuvable.")
        self.members.delete(target.id)
        conv = self.conversations.get_by_group(group_id)
        if conv and (cm := self.conv_members.find(conv.id, user_id)):
            self.conv_members.delete(cm.id)
        remaining = self.members.list_for_group(group_id)
        if remaining and target.role == "ADMIN" and not any(m.role == "ADMIN" for m in remaining):
            remaining[0].role = "ADMIN"  # le plus ancien membre devient administrateur
            self.members.update(remaining[0])
        self.uow.commit()


class DeleteGroup:
    def __init__(self, access: GroupAccess, groups: ports.GroupRepository, uow: UnitOfWork) -> None:
        self.access, self.groups, self.uow = access, groups, uow

    def execute(self, actor: Actor, group_id: int) -> None:
        self.access.admin_group(actor, group_id)
        self.groups.delete(group_id)  # IntegrityError -> 409 s'il existe des demandes de location liées
        self.uow.commit()
