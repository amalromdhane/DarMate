from app.application.dto.dto import Actor, Page
from app.application.interfaces.services import UnitOfWork
from app.application.use_cases.common import AuditService
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationFailedError
from app.domain.entities import entities as e
from app.domain.entities.enums import RoleName, UserStatus
from app.domain.repositories import ports

SETTING_PREFIXES = ("compat_weight_", "site_")


def _require_admin(actor: Actor) -> None:
    if not actor.is_admin:
        raise ForbiddenError("Réservé aux administrateurs.")


class AdminUsers:
    def __init__(self, users: ports.UserRepository, tokens: ports.RefreshTokenRepository,
                 audit: AuditService, uow: UnitOfWork) -> None:
        self.users, self.tokens, self.audit, self.uow = users, tokens, audit, uow

    def list(self, actor: Actor, text: str | None, status: UserStatus | None, page: int, size: int) -> Page:
        _require_admin(actor)
        rows, total = self.users.search(text, status, page, size)
        return Page([(u, self.users.get_roles(u.id)) for u in rows], total, page, size)

    def set_status(self, actor: Actor, user_id: int, status: UserStatus) -> e.User:
        _require_admin(actor)
        user = self.users.get(user_id)
        if user is None:
            raise NotFoundError("Utilisateur introuvable.")
        if user.id == actor.id:
            raise ConflictError("Vous ne pouvez pas modifier votre propre statut.")
        if RoleName.ADMIN.value in self.users.get_roles(user_id):
            raise ForbiddenError("Le statut d'un administrateur ne peut pas être modifié ici.")
        user.status = status
        self.users.update(user)
        if status in (UserStatus.SUSPENDED, UserStatus.BANNED):
            self.tokens.revoke_all_for_user(user.id)  # coupe les sessions ouvertes
        self.audit.log(actor.id, "admin.user_status", "user", user.id, status=status.value)
        self.uow.commit()
        return user


class ReferenceData:
    """Régions, villes et catégories : lecture publique, écriture réservée aux administrateurs."""

    def __init__(self, regions: ports.RegionRepository, cities: ports.CityRepository,
                 categories: ports.CategoryRepository, audit: AuditService, uow: UnitOfWork) -> None:
        self.regions, self.cities, self.categories, self.audit, self.uow = regions, cities, categories, audit, uow

    def _name(self, name: str) -> str:
        name = name.strip()
        if not name:
            raise ValidationFailedError("Le nom est obligatoire.")
        return name

    def create_region(self, actor: Actor, name: str) -> e.Region:
        _require_admin(actor)
        r = self.regions.add(e.Region(name=self._name(name)))
        self.audit.log(actor.id, "admin.region_create", "region", r.id)
        self.uow.commit()
        return r

    def update_region(self, actor: Actor, id: int, name: str) -> e.Region:
        _require_admin(actor)
        r = self.regions.get(id) or self._missing()
        r.name = self._name(name)
        self.regions.update(r)
        self.uow.commit()
        return r

    def delete_region(self, actor: Actor, id: int) -> None:
        _require_admin(actor)
        self.regions.delete(id)  # IntegrityError -> 409 si des villes y sont rattachées
        self.audit.log(actor.id, "admin.region_delete", "region", id)
        self.uow.commit()

    def create_city(self, actor: Actor, region_id: int, name: str) -> e.City:
        _require_admin(actor)
        if not self.regions.get(region_id):
            raise ValidationFailedError("Région inconnue.")
        c = self.cities.add(e.City(region_id=region_id, name=self._name(name)))
        self.audit.log(actor.id, "admin.city_create", "city", c.id)
        self.uow.commit()
        return c

    def update_city(self, actor: Actor, id: int, name: str | None, region_id: int | None) -> e.City:
        _require_admin(actor)
        c = self.cities.get(id) or self._missing()
        if name is not None:
            c.name = self._name(name)
        if region_id is not None:
            if not self.regions.get(region_id):
                raise ValidationFailedError("Région inconnue.")
            c.region_id = region_id
        self.cities.update(c)
        self.uow.commit()
        return c

    def delete_city(self, actor: Actor, id: int) -> None:
        _require_admin(actor)
        self.cities.delete(id)
        self.audit.log(actor.id, "admin.city_delete", "city", id)
        self.uow.commit()

    def create_category(self, actor: Actor, name: str) -> e.PropertyCategory:
        _require_admin(actor)
        c = self.categories.add(e.PropertyCategory(name=self._name(name)))
        self.audit.log(actor.id, "admin.category_create", "category", c.id)
        self.uow.commit()
        return c

    def update_category(self, actor: Actor, id: int, name: str) -> e.PropertyCategory:
        _require_admin(actor)
        c = self.categories.get(id) or self._missing()
        c.name = self._name(name)
        self.categories.update(c)
        self.uow.commit()
        return c

    def delete_category(self, actor: Actor, id: int) -> None:
        _require_admin(actor)
        self.categories.delete(id)
        self.audit.log(actor.id, "admin.category_delete", "category", id)
        self.uow.commit()

    @staticmethod
    def _missing():
        raise NotFoundError("Élément introuvable.")

    # lecture publique
    def list_regions(self): return self.regions.list_all()
    def list_cities(self, region_id: int | None = None): return self.cities.list_all(region_id)
    def list_categories(self): return self.categories.list_all()


class AppSettings:
    def __init__(self, repo: ports.SettingRepository, audit: AuditService, uow: UnitOfWork) -> None:
        self.repo, self.audit, self.uow = repo, audit, uow

    def get(self, actor: Actor) -> dict[str, str]:
        _require_admin(actor)
        return self.repo.all_as_dict()

    def update(self, actor: Actor, values: dict[str, str]) -> dict[str, str]:
        _require_admin(actor)
        for key, value in values.items():
            if not key.startswith(SETTING_PREFIXES):
                raise ValidationFailedError(f"Paramètre inconnu : {key}.")
            if key.startswith("compat_weight_"):
                try:
                    if float(value) < 0:
                        raise ValueError
                except ValueError:
                    raise ValidationFailedError(f"« {key} » doit être un nombre positif.")
            existing = self.repo.get_by_key(key)
            if existing:
                existing.value = str(value)
                self.repo.update(existing)
            else:
                self.repo.add(e.ApplicationSetting(key=key, value=str(value)))
        self.audit.log(actor.id, "admin.settings_update", "setting", None, keys=list(values))
        self.uow.commit()
        return self.repo.all_as_dict()


class AdminStats:
    def __init__(self, stats: ports.StatsRepository) -> None:
        self.stats = stats

    def execute(self, actor: Actor) -> dict[str, int]:
        _require_admin(actor)
        return self.stats.global_stats()
