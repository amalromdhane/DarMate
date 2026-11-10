from sqlalchemy import or_, select

from app.domain.entities import entities as e
from app.domain.entities.enums import RequestStatus
from app.domain.repositories import ports
from app.infrastructure.models.roommate import (
    GroupInvitationModel, GroupMemberModel, RoommateGroupModel, RoommateProfileModel, RoommateRequestModel,
)
from app.infrastructure.repositories.base import SqlRepository


class SqlRoommateProfileRepository(SqlRepository[e.RoommateProfile], ports.RoommateProfileRepository):
    model, entity = RoommateProfileModel, e.RoommateProfile

    def get_by_user(self, user_id):
        return self._first(select(RoommateProfileModel).where(RoommateProfileModel.user_id == user_id))

    def list_active_except(self, user_id, city_id):
        stmt = select(RoommateProfileModel).where(RoommateProfileModel.user_id != user_id, RoommateProfileModel.is_active.is_(True))
        if city_id:
            stmt = stmt.where(RoommateProfileModel.city_id == city_id)
        return self._all(stmt.limit(200))


class SqlRoommateRequestRepository(SqlRepository[e.RoommateRequest], ports.RoommateRequestRepository):
    model, entity = RoommateRequestModel, e.RoommateRequest

    def find_between(self, a, b):
        return self._first(select(RoommateRequestModel).where(
            or_((RoommateRequestModel.sender_id == a) & (RoommateRequestModel.receiver_id == b),
                (RoommateRequestModel.sender_id == b) & (RoommateRequestModel.receiver_id == a))))

    def list_for_user(self, user_id):
        return self._all(select(RoommateRequestModel).where(
            or_(RoommateRequestModel.sender_id == user_id, RoommateRequestModel.receiver_id == user_id)
        ).order_by(RoommateRequestModel.id.desc()))


class SqlGroupRepository(SqlRepository[e.RoommateGroup], ports.GroupRepository):
    model, entity = RoommateGroupModel, e.RoommateGroup

    def list_for_user(self, user_id):
        stmt = (select(RoommateGroupModel).join(GroupMemberModel, GroupMemberModel.group_id == RoommateGroupModel.id)
                .where(GroupMemberModel.user_id == user_id).order_by(RoommateGroupModel.id.desc()))
        return self._all(stmt)


class SqlGroupMemberRepository(SqlRepository[e.GroupMember], ports.GroupMemberRepository):
    model, entity = GroupMemberModel, e.GroupMember

    def list_for_group(self, group_id):
        return self._all(select(GroupMemberModel).where(GroupMemberModel.group_id == group_id).order_by(GroupMemberModel.id))

    def find(self, group_id, user_id):
        return self._first(select(GroupMemberModel).where(GroupMemberModel.group_id == group_id, GroupMemberModel.user_id == user_id))


class SqlGroupInvitationRepository(SqlRepository[e.GroupInvitation], ports.GroupInvitationRepository):
    model, entity = GroupInvitationModel, e.GroupInvitation

    def list_for_invitee(self, user_id):
        return self._all(select(GroupInvitationModel).where(GroupInvitationModel.invitee_id == user_id)
                         .order_by(GroupInvitationModel.id.desc()))

    def find_pending(self, group_id, invitee_id):
        return self._first(select(GroupInvitationModel).where(
            GroupInvitationModel.group_id == group_id, GroupInvitationModel.invitee_id == invitee_id,
            GroupInvitationModel.status == RequestStatus.PENDING))
