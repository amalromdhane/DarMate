from datetime import timedelta

from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.core.clock import utcnow
from app.domain.entities.enums import PropertyStatus, RoleName, UserStatus
from app.domain.repositories import ports
from app.infrastructure.models.messaging import MessageModel
from app.infrastructure.models.property import PropertyModel
from app.infrastructure.models.rental import RentalRequestModel
from app.infrastructure.models.roommate import RoommateGroupModel
from app.infrastructure.models.user import RoleModel, UserModel, UserRoleModel


class SqlStatsRepository(ports.StatsRepository):
    def __init__(self, session: Session) -> None:
        self.s = session

    def _count(self, stmt) -> int:
        return self.s.execute(stmt).scalar_one()

    def _role_count(self, role: RoleName) -> int:
        return self._count(select(func.count(distinct(UserRoleModel.user_id))).join(
            RoleModel, RoleModel.id == UserRoleModel.role_id).where(RoleModel.name == role.value))

    def global_stats(self):
        since = utcnow() - timedelta(days=7)
        live = PropertyModel.deleted_at.is_(None)
        return {
            "users": self._count(select(func.count()).select_from(UserModel)),
            "active_users": self._count(select(func.count()).select_from(UserModel).where(UserModel.status == UserStatus.ACTIVE)),
            "seekers": self._role_count(RoleName.SEEKER),
            "owners": self._role_count(RoleName.OWNER),
            "properties": self._count(select(func.count()).select_from(PropertyModel).where(live)),
            "available_properties": self._count(select(func.count()).select_from(PropertyModel).where(
                live, PropertyModel.status == PropertyStatus.AVAILABLE)),
            "groups": self._count(select(func.count()).select_from(RoommateGroupModel)),
            "rental_requests": self._count(select(func.count()).select_from(RentalRequestModel)),
            "new_users_7d": self._count(select(func.count()).select_from(UserModel).where(UserModel.created_at >= since)),
            "messages_7d": self._count(select(func.count()).select_from(MessageModel).where(MessageModel.created_at >= since)),
        }
