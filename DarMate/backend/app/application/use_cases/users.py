from app.application.dto.dto import Actor, UserView
from app.application.interfaces.services import FileStorage, UnitOfWork, UploadedFile
from app.application.use_cases.auth import clean_roles
from app.application.use_cases.common import AuditService, average
from app.core.config import settings
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationFailedError
from app.domain.entities import entities as e
from app.domain.repositories import ports

PROFILE_FIELDS = {"first_name", "last_name", "phone", "bio", "birth_date", "city_id", "language"}
DOC_MIMES = {"image/jpeg": ".jpg", "image/png": ".png", "application/pdf": ".pdf"}
IMAGE_MIMES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


class GetUser:
    def __init__(self, users: ports.UserRepository, profiles: ports.UserProfileRepository,
                 reviews: ports.ReviewRepository) -> None:
        self.users, self.profiles, self.reviews = users, profiles, reviews

    def execute(self, user_id: int, *, with_rating: bool = False) -> UserView:
        user = self.users.get(user_id)
        if user is None:
            raise NotFoundError("Utilisateur introuvable.")
        view = UserView(user, self.profiles.get_by_user(user_id), self.users.get_roles(user_id))
        if with_rating:
            ratings = [r.rating for r in self.reviews.list_for_user(user_id)]
            view.rating_avg, view.rating_count = average(ratings), len(ratings)
        return view


class UpdateMyProfile:
    def __init__(self, users: ports.UserRepository, profiles: ports.UserProfileRepository,
                 cities: ports.CityRepository, audit: AuditService, uow: UnitOfWork) -> None:
        self.users, self.profiles, self.cities, self.audit, self.uow = users, profiles, cities, audit, uow

    def execute(self, actor: Actor, changes: dict) -> UserView:
        profile = self.profiles.get_by_user(actor.id) or self.profiles.add(e.UserProfile(user_id=actor.id))
        if changes.get("city_id") and not self.cities.get(changes["city_id"]):
            raise ValidationFailedError("Ville inconnue.")
        for key, value in changes.items():
            if key in PROFILE_FIELDS:
                setattr(profile, key, value)
        self.profiles.update(profile)
        roles = self.users.get_roles(actor.id)
        if "roles" in changes and changes["roles"] is not None:
            new = clean_roles(changes["roles"])
            roles = sorted(new + [r for r in roles if r not in {"SEEKER", "OWNER"}])
            self.users.set_roles(actor.id, roles)
        self.audit.log(actor.id, "user.update_profile", "user", actor.id)
        self.uow.commit()
        return UserView(self.users.get(actor.id), profile, roles)


class BlockUser:
    def __init__(self, blocks: ports.UserBlockRepository, users: ports.UserRepository, uow: UnitOfWork) -> None:
        self.blocks, self.users, self.uow = blocks, users, uow

    def execute(self, actor: Actor, target_id: int, block: bool = True) -> None:
        if target_id == actor.id:
            raise ValidationFailedError("Vous ne pouvez pas vous bloquer vous-même.")
        if not self.users.get(target_id):
            raise NotFoundError("Utilisateur introuvable.")
        existing = self.blocks.find(actor.id, target_id)
        if block and not existing:
            self.blocks.add(e.UserBlock(blocker_id=actor.id, blocked_id=target_id))
        elif not block and existing:
            self.blocks.delete(existing.id)
        self.uow.commit()


class ReportUser:
    def __init__(self, reports: ports.ReportRepository, users: ports.UserRepository,
                 audit: AuditService, uow: UnitOfWork) -> None:
        self.reports, self.users, self.audit, self.uow = reports, users, audit, uow

    def execute(self, actor: Actor, reported_user_id: int, reason: str, details: str | None = None,
                message_id: int | None = None) -> e.Report:
        if reported_user_id == actor.id:
            raise ValidationFailedError("Vous ne pouvez pas vous signaler vous-même.")
        if not self.users.get(reported_user_id):
            raise NotFoundError("Utilisateur introuvable.")
        report = self.reports.add(e.Report(reporter_id=actor.id, reported_user_id=reported_user_id,
                                           reason=reason, details=details, message_id=message_id))
        self.audit.log(actor.id, "user.report", "user", reported_user_id, report_id=report.id)
        self.uow.commit()
        return report


class UploadIdentityDocument:
    def __init__(self, docs: ports.IdentityDocumentRepository, storage: FileStorage,
                 audit: AuditService, uow: UnitOfWork) -> None:
        self.docs, self.storage, self.audit, self.uow = docs, storage, audit, uow

    def execute(self, actor: Actor, file: UploadedFile, doc_type: str) -> e.IdentityDocument:
        if doc_type not in {"ID_CARD", "PASSPORT", "DRIVING_LICENSE"}:
            raise ValidationFailedError("Type de document non pris en charge.")
        path = self.storage.save(f"identity/{actor.id}", file, DOC_MIMES,
                                 settings.max_document_mb * 1024 * 1024, private=True)
        doc = self.docs.add(e.IdentityDocument(user_id=actor.id, path=path, doc_type=doc_type))
        self.audit.log(actor.id, "identity.upload", "identity_document", doc.id)
        self.uow.commit()
        return doc


class DownloadIdentityDocument:
    """Accès réservé au propriétaire du document ou à un administrateur (jamais public)."""

    def __init__(self, docs: ports.IdentityDocumentRepository, storage: FileStorage, audit: AuditService, uow: UnitOfWork) -> None:
        self.docs, self.storage, self.audit, self.uow = docs, storage, audit, uow

    def execute(self, actor: Actor, doc_id: int) -> tuple[bytes, str]:
        doc = self.docs.get(doc_id)
        if doc is None or not (doc.user_id == actor.id or actor.is_admin):
            raise NotFoundError("Document introuvable.")
        self.audit.log(actor.id, "identity.download", "identity_document", doc.id)
        self.uow.commit()
        return self.storage.read(doc.path), doc.path
