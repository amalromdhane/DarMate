from sqlalchemy import delete, func, select, update

from app.domain.entities import entities as e
from app.domain.entities.enums import UserStatus
from app.domain.repositories import ports
from app.infrastructure.models.user import (
    ApplicationSettingModel, AuditLogModel, IdentityDocumentModel, PasswordResetTokenModel,
    RefreshTokenModel, ReportModel, RoleModel, UserBlockModel, UserModel, UserProfileModel, UserRoleModel,
)
from app.infrastructure.repositories.base import SqlRepository
from app.core.clock import utcnow


class SqlUserRepository(SqlRepository[e.User], ports.UserRepository):
    model, entity = UserModel, e.User

    def get_by_email(self, email):
        return self._first(select(UserModel).where(UserModel.email == email.lower()))

    def get_roles(self, user_id):
        stmt = select(RoleModel.name).join(UserRoleModel, UserRoleModel.role_id == RoleModel.id).where(UserRoleModel.user_id == user_id)
        return list(self.s.execute(stmt).scalars().all())

    def set_roles(self, user_id, roles):
        self.s.execute(delete(UserRoleModel).where(UserRoleModel.user_id == user_id))
        for name in roles:
            role = self.s.execute(select(RoleModel).where(RoleModel.name == name)).scalars().first()
            if role is None:
                role = RoleModel(name=name)
                self.s.add(role)
                self.s.flush()
            self.s.add(UserRoleModel(user_id=user_id, role_id=role.id))
        self.s.flush()

    def search(self, text, status, page, size):
        stmt = select(UserModel)
        if text:
            stmt = stmt.where(UserModel.email.like(f"%{text.lower()}%"))
        if status:
            stmt = stmt.where(UserModel.status == status)
        total = self.s.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
        rows = self._all(stmt.order_by(UserModel.id.desc()).offset((page - 1) * size).limit(size))
        return rows, total


class SqlUserProfileRepository(SqlRepository[e.UserProfile], ports.UserProfileRepository):
    model, entity = UserProfileModel, e.UserProfile

    def get_by_user(self, user_id):
        return self._first(select(UserProfileModel).where(UserProfileModel.user_id == user_id))


class SqlRefreshTokenRepository(SqlRepository[e.RefreshToken], ports.RefreshTokenRepository):
    model, entity = RefreshTokenModel, e.RefreshToken

    def get_by_hash(self, token_hash):
        return self._first(select(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash))

    def revoke_all_for_user(self, user_id):
        self.s.execute(update(RefreshTokenModel).where(
            RefreshTokenModel.user_id == user_id, RefreshTokenModel.revoked_at.is_(None)).values(revoked_at=utcnow()))


class SqlPasswordResetRepository(SqlRepository[e.PasswordResetToken], ports.PasswordResetRepository):
    model, entity = PasswordResetTokenModel, e.PasswordResetToken

    def get_by_hash(self, token_hash):
        return self._first(select(PasswordResetTokenModel).where(PasswordResetTokenModel.token_hash == token_hash))


class SqlIdentityDocumentRepository(SqlRepository[e.IdentityDocument], ports.IdentityDocumentRepository):
    model, entity = IdentityDocumentModel, e.IdentityDocument


class SqlAuditLogRepository(SqlRepository[e.AuditLog], ports.AuditLogRepository):
    model, entity = AuditLogModel, e.AuditLog


class SqlReportRepository(SqlRepository[e.Report], ports.ReportRepository):
    model, entity = ReportModel, e.Report


class SqlUserBlockRepository(SqlRepository[e.UserBlock], ports.UserBlockRepository):
    model, entity = UserBlockModel, e.UserBlock

    def find(self, blocker_id, blocked_id):
        return self._first(select(UserBlockModel).where(
            UserBlockModel.blocker_id == blocker_id, UserBlockModel.blocked_id == blocked_id))

    def exists_between(self, a, b):
        stmt = select(func.count()).select_from(UserBlockModel).where(
            ((UserBlockModel.blocker_id == a) & (UserBlockModel.blocked_id == b))
            | ((UserBlockModel.blocker_id == b) & (UserBlockModel.blocked_id == a)))
        return self.s.execute(stmt).scalar_one() > 0


class SqlSettingRepository(SqlRepository[e.ApplicationSetting], ports.SettingRepository):
    model, entity = ApplicationSettingModel, e.ApplicationSetting

    def get_by_key(self, key):
        return self._first(select(ApplicationSettingModel).where(ApplicationSettingModel.key == key))

    def all_as_dict(self):
        return {s.key: s.value for s in self._all(select(ApplicationSettingModel))}
