from decimal import Decimal

from app.application.dto.dto import Actor, RoommateMatch
from app.application.interfaces.services import UnitOfWork
from app.application.use_cases.common import AccessGuard, NotificationService, UserDirectory
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationFailedError
from app.domain.entities import entities as e
from app.domain.entities.enums import NotificationType, RequestStatus
from app.domain.repositories import ports
from app.domain.services.compatibility import CompatibilityWeights, compatibility_score

SCHEDULES = {"EARLY", "NIGHT", "FLEXIBLE"}
LOOKING_FOR = {"ROOM", "HOUSE"}
PROFILE_FIELDS = {"city_id", "budget_min", "budget_max", "smoker", "has_pets", "schedule",
                  "cleanliness", "sociability", "about", "is_active", "looking_for"}


class UpsertRoommateProfile:
    def __init__(self, profiles: ports.RoommateProfileRepository, cities: ports.CityRepository, uow: UnitOfWork) -> None:
        self.profiles, self.cities, self.uow = profiles, cities, uow

    def execute(self, actor: Actor, data: dict) -> e.RoommateProfile:
        profile = self.profiles.get_by_user(actor.id) or e.RoommateProfile(user_id=actor.id)
        for k, v in data.items():
            if k in PROFILE_FIELDS:
                setattr(profile, k, v)
        if profile.schedule not in SCHEDULES:
            raise ValidationFailedError("Rythme de vie invalide.")
        if getattr(profile, "looking_for", "ROOM") not in LOOKING_FOR:
            raise ValidationFailedError("Choisissez une chambre ou une maison.")
        if not (1 <= profile.cleanliness <= 5 and 1 <= profile.sociability <= 5):
            raise ValidationFailedError("Les niveaux de propreté et de sociabilité vont de 1 à 5.")
        if profile.budget_min is not None and profile.budget_max is not None and profile.budget_min > profile.budget_max:
            raise ValidationFailedError("Le budget minimum dépasse le budget maximum.")
        if profile.city_id and not self.cities.get(profile.city_id):
            raise ValidationFailedError("Ville inconnue.")
        profile = self.profiles.update(profile) if profile.id else self.profiles.add(profile)
        self.uow.commit()
        return profile


class GetMyRoommateProfile:
    def __init__(self, profiles: ports.RoommateProfileRepository) -> None:
        self.profiles = profiles

    def execute(self, actor: Actor) -> e.RoommateProfile | None:
        return self.profiles.get_by_user(actor.id)


class SearchRoommates:
    def __init__(self, profiles: ports.RoommateProfileRepository, settings_repo: ports.SettingRepository,
                 blocks: ports.UserBlockRepository, directory: UserDirectory) -> None:
        self.profiles, self.settings, self.blocks, self.directory = profiles, settings_repo, blocks, directory

    def execute(self, actor: Actor, city_id: int | None, min_score: int = 0) -> list[RoommateMatch]:
        mine = self.profiles.get_by_user(actor.id)
        if mine is None:
            raise ValidationFailedError("Créez d'abord votre profil de colocation pour voir les compatibilités.")
        weights = CompatibilityWeights.from_settings(self.settings.all_as_dict())
        out = []
        for other in self.profiles.list_active_except(actor.id, city_id):
            if self.blocks.exists_between(actor.id, other.user_id):
                continue
            score = compatibility_score(mine, other, weights)
            if score >= min_score:
                out.append(RoommateMatch(other, self.directory.name_of(other.user_id), score))
        return sorted(out, key=lambda m: m.score, reverse=True)


class GetCompatibility:
    def __init__(self, profiles: ports.RoommateProfileRepository, settings_repo: ports.SettingRepository) -> None:
        self.profiles, self.settings = profiles, settings_repo

    def execute(self, actor: Actor, other_user_id: int) -> int:
        mine, other = self.profiles.get_by_user(actor.id), self.profiles.get_by_user(other_user_id)
        if mine is None:
            raise ValidationFailedError("Créez d'abord votre profil de colocation.")
        if other is None or not other.is_active:
            raise NotFoundError("Profil de colocation introuvable.")
        return compatibility_score(mine, other, CompatibilityWeights.from_settings(self.settings.all_as_dict()))


class SendRoommateRequest:
    def __init__(self, requests: ports.RoommateRequestRepository, profiles: ports.RoommateProfileRepository,
                 guard: AccessGuard, notifications: NotificationService, directory: UserDirectory, uow: UnitOfWork) -> None:
        self.requests, self.profiles, self.guard, self.notifications, self.directory, self.uow = requests, profiles, guard, notifications, directory, uow

    def execute(self, actor: Actor, receiver_id: int, message: str | None) -> e.RoommateRequest:
        if receiver_id == actor.id:
            raise ValidationFailedError("Vous ne pouvez pas vous envoyer une demande.")
        profile = self.profiles.get_by_user(receiver_id)
        if profile is None or not profile.is_active:
            raise NotFoundError("Profil de colocation introuvable.")
        self.guard.ensure_not_blocked(actor.id, receiver_id)
        if self.requests.find_between(actor.id, receiver_id):
            raise ConflictError("Une demande existe déjà entre vous et cette personne.")
        req = self.requests.add(e.RoommateRequest(sender_id=actor.id, receiver_id=receiver_id, message=message))
        self.notifications.notify(receiver_id, NotificationType.ROOMMATE_REQUEST, "Nouvelle demande de colocation",
                                  f"{self.directory.name_of(actor.id)} souhaite entrer en contact.", "/roommates/requests")
        self.uow.commit()
        return req


class RespondRoommateRequest:
    def __init__(self, requests: ports.RoommateRequestRepository, notifications: NotificationService,
                 directory: UserDirectory, uow: UnitOfWork) -> None:
        self.requests, self.notifications, self.directory, self.uow = requests, notifications, directory, uow

    def execute(self, actor: Actor, request_id: int, accept: bool) -> e.RoommateRequest:
        req = self.requests.get(request_id)
        if req is None or req.receiver_id != actor.id:
            raise NotFoundError("Demande introuvable.")
        if req.status != RequestStatus.PENDING:
            raise ConflictError("Cette demande a déjà reçu une réponse.")
        req.status = RequestStatus.ACCEPTED if accept else RequestStatus.REJECTED
        self.requests.update(req)
        verb = "accepté" if accept else "refusé"
        self.notifications.notify(req.sender_id, NotificationType.ROOMMATE_REQUEST, f"Demande de colocation {verb}e",
                                  f"{self.directory.name_of(actor.id)} a {verb} votre demande.", "/roommates/requests")
        self.uow.commit()
        return req


class ListRoommateRequests:
    def __init__(self, requests: ports.RoommateRequestRepository) -> None:
        self.requests = requests

    def execute(self, actor: Actor) -> list[e.RoommateRequest]:
        return self.requests.list_for_user(actor.id)
