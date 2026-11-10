"""Services applicatifs transverses (audit, notifications, accès)."""
from app.core.exceptions import ForbiddenError, NotFoundError
from app.domain.entities import entities as e
from app.domain.entities.enums import NotificationType, UserStatus
from app.domain.repositories import ports


class AuditService:
    def __init__(self, repo: ports.AuditLogRepository) -> None:
        self.repo = repo

    def log(self, user_id: int | None, action: str, entity_type: str | None = None,
            entity_id: int | None = None, **details) -> None:
        self.repo.add(e.AuditLog(user_id=user_id, action=action, entity_type=entity_type,
                                 entity_id=entity_id, details=details or None))


class NotificationService:
    def __init__(self, repo: ports.NotificationRepository) -> None:
        self.repo = repo

    def notify(self, user_id: int, type: NotificationType, title: str,
               body: str | None = None, link: str | None = None) -> None:
        self.repo.add(e.Notification(user_id=user_id, type=type, title=title, body=body, link=link))


class UserDirectory:
    """Accès simplifié aux noms d'affichage des utilisateurs."""

    def __init__(self, users: ports.UserRepository, profiles: ports.UserProfileRepository) -> None:
        self.users, self.profiles = users, profiles

    def name_of(self, user_id: int) -> str:
        p = self.profiles.get_by_user(user_id)
        if p and (p.first_name or p.last_name):
            return f"{p.first_name} {p.last_name}".strip()
        u = self.users.get(user_id)
        return u.email.split("@")[0] if u else "Utilisateur"

    def require_active(self, user_id: int) -> e.User:
        u = self.users.get(user_id)
        if u is None or u.status != UserStatus.ACTIVE:
            raise NotFoundError("Utilisateur introuvable.")
        return u


class AccessGuard:
    """Règles d'accès centralisées (anti-IDOR) réutilisées par les use cases."""

    def __init__(self, blocks: ports.UserBlockRepository) -> None:
        self.blocks = blocks

    def ensure_not_blocked(self, a: int, b: int) -> None:
        if self.blocks.exists_between(a, b):
            raise ForbiddenError("Action impossible : un blocage existe entre ces utilisateurs.")


def average(values: list[int]) -> float | None:
    return round(sum(values) / len(values), 2) if values else None
