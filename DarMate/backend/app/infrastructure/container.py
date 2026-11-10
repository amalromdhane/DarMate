"""Conteneur d'injection de dépendances : résout automatiquement les use cases à partir de leurs annotations."""
import inspect
import typing
from typing import Any

from sqlalchemy.orm import Session

from app.application.interfaces import services as sp
from app.domain.repositories import ports as rp
from app.infrastructure.external_services.realtime import manager
from app.infrastructure.external_services.services import (
    Argon2PasswordHasher, ConsoleEmailSender, JwtTokenService, LocalFileStorage, SqlUnitOfWork,
)
from app.infrastructure.repositories import geo, messaging, properties, rentals, social, stats, users

_REGISTRY: dict[type, type] = {
    rp.UserRepository: users.SqlUserRepository,
    rp.UserProfileRepository: users.SqlUserProfileRepository,
    rp.RefreshTokenRepository: users.SqlRefreshTokenRepository,
    rp.PasswordResetRepository: users.SqlPasswordResetRepository,
    rp.IdentityDocumentRepository: users.SqlIdentityDocumentRepository,
    rp.AuditLogRepository: users.SqlAuditLogRepository,
    rp.ReportRepository: users.SqlReportRepository,
    rp.UserBlockRepository: users.SqlUserBlockRepository,
    rp.SettingRepository: users.SqlSettingRepository,
    rp.RegionRepository: geo.SqlRegionRepository,
    rp.CityRepository: geo.SqlCityRepository,
    rp.CategoryRepository: geo.SqlCategoryRepository,
    rp.PropertyRepository: properties.SqlPropertyRepository,
    rp.PropertyImageRepository: properties.SqlPropertyImageRepository,
    rp.FavoriteRepository: properties.SqlFavoriteRepository,
    rp.SavedSearchRepository: properties.SqlSavedSearchRepository,
    rp.SearchAlertRepository: properties.SqlSearchAlertRepository,
    rp.RoommateProfileRepository: social.SqlRoommateProfileRepository,
    rp.RoommateRequestRepository: social.SqlRoommateRequestRepository,
    rp.GroupRepository: social.SqlGroupRepository,
    rp.GroupMemberRepository: social.SqlGroupMemberRepository,
    rp.GroupInvitationRepository: social.SqlGroupInvitationRepository,
    rp.RentalRequestRepository: rentals.SqlRentalRequestRepository,
    rp.VisitRepository: rentals.SqlVisitRepository,
    rp.VisitSlotRepository: rentals.SqlVisitSlotRepository,
    rp.ReviewRepository: rentals.SqlReviewRepository,
    rp.ConversationRepository: messaging.SqlConversationRepository,
    rp.ConversationMemberRepository: messaging.SqlConversationMemberRepository,
    rp.MessageRepository: messaging.SqlMessageRepository,
    rp.MessageAttachmentRepository: messaging.SqlMessageAttachmentRepository,
    rp.NotificationRepository: messaging.SqlNotificationRepository,
    rp.StatsRepository: stats.SqlStatsRepository,
    sp.UnitOfWork: SqlUnitOfWork,
}
_SINGLETONS: dict[type, Any] = {
    sp.PasswordHasher: Argon2PasswordHasher(),
    sp.TokenService: JwtTokenService(),
    sp.FileStorage: None,  # créé paresseusement (dépend de la config)
    sp.EmailSender: ConsoleEmailSender(),
    sp.RealtimePublisher: manager,
}


class Container:
    """Construit use cases et services pour une session de base de données donnée."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self._cache: dict[type, Any] = {}

    def resolve(self, cls: type) -> Any:
        if cls in self._cache:
            return self._cache[cls]
        if cls in _SINGLETONS:
            if _SINGLETONS[cls] is None:
                _SINGLETONS[cls] = LocalFileStorage()
            return _SINGLETONS[cls]
        impl = _REGISTRY.get(cls)
        if impl is not None:
            obj = impl(self.session)
        else:  # use case ou service applicatif : câblage automatique du constructeur
            hints = typing.get_type_hints(cls.__init__)
            params = [p for p in inspect.signature(cls.__init__).parameters if p != "self"]
            obj = cls(**{p: self.resolve(hints[p]) for p in params})
        self._cache[cls] = obj
        return obj


def override_file_storage(storage: sp.FileStorage) -> None:
    _SINGLETONS[sp.FileStorage] = storage
