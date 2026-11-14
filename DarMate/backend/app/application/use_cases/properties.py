from app.application.dto.dto import Actor, CreatePropertyCmd, Page, PropertyCard, PropertyDetail
from app.application.interfaces.services import FileStorage, UnitOfWork, UploadedFile
from app.application.use_cases.common import AuditService, NotificationService, UserDirectory, average
from app.application.use_cases.users import IMAGE_MIMES
from app.core.clock import utcnow
from app.core.config import settings
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationFailedError
from app.domain.entities import entities as e
from app.domain.entities.enums import NotificationType, PropertyStatus, RoleName
from app.domain.repositories import ports
from app.domain.repositories.ports import PropertySearchCriteria
from app.domain.services.rental_rules import matches_filters
from app.core.images import check_image

EDITABLE = {"city_id", "category_id", "title", "description", "price", "rooms", "surface_m2", "address",
            "latitude", "longitude", "coliving_allowed", "max_roommates", "conditions", "available_from"}
MAX_IMAGES = 5
PUBLIC_STATUSES = (PropertyStatus.AVAILABLE, PropertyStatus.RENTED)


def _validate(prop: e.Property) -> None:
    if prop.price <= 0:
        raise ValidationFailedError("Le prix doit être supérieur à 0.")
    if prop.rooms < 1:
        raise ValidationFailedError("Le nombre de pièces doit être d'au moins 1.")
    if (prop.latitude is None) != (prop.longitude is None):
        raise ValidationFailedError("Renseignez la latitude et la longitude ensemble.")
    if not prop.coliving_allowed:
        prop.max_roommates = 1
    elif prop.max_roommates < 2:
        raise ValidationFailedError("Pour une colocation, le nombre maximal de colocataires doit être d'au moins 2.")


class PropertyAccess:
    def __init__(self, props: ports.PropertyRepository) -> None:
        self.props = props

    def owned(self, actor: Actor, property_id: int) -> e.Property:
        prop = self.props.get(property_id)
        if prop is None or prop.deleted_at is not None or prop.owner_id != actor.id:
            raise NotFoundError("Annonce introuvable.")  # 404 : ne révèle pas l'existence (anti-IDOR)
        return prop

    def visible(self, property_id: int, viewer_id: int | None = None) -> e.Property:
        prop = self.props.get(property_id)
        if prop is None or prop.deleted_at is not None:
            raise NotFoundError("Annonce introuvable.")
        if prop.status not in PUBLIC_STATUSES and prop.owner_id != viewer_id:
            raise NotFoundError("Annonce introuvable.")
        return prop


class AlertNotifier:
    def __init__(self, alerts: ports.SearchAlertRepository, notifications: NotificationService) -> None:
        self.alerts, self.notifications = alerts, notifications

    def new_property(self, prop: e.Property) -> None:
        for alert, search in self.alerts.list_active_with_search():
            if search.user_id != prop.owner_id and matches_filters(search.filters, prop):
                self.notifications.notify(search.user_id, NotificationType.NEW_PROPERTY,
                                          "Nouvelle annonce correspondant à votre recherche",
                                          f"{prop.title} — {prop.price} DT", f"/properties/{prop.id}")
                alert.last_notified_at = utcnow()
                self.alerts.update(alert)


class CardBuilder:
    def __init__(self, images: ports.PropertyImageRepository, cities: ports.CityRepository,
                 favorites: ports.FavoriteRepository) -> None:
        self.images, self.cities, self.favorites = images, cities, favorites

    def build(self, props: list[e.Property], viewer_id: int | None = None) -> list[PropertyCard]:
        imgs = self.images.list_for_properties([p.id for p in props])
        names = {c.id: c.name for c in self.cities.list_all()}
        fav_ids = {p.id for p in self.favorites.list_properties(viewer_id)} if viewer_id else set()
        return [PropertyCard(p, names.get(p.city_id, ""), imgs[p.id][0].path if imgs[p.id] else None, p.id in fav_ids)
                for p in props]


class CreateProperty:
    def __init__(self, props: ports.PropertyRepository, cities: ports.CityRepository,
                 categories: ports.CategoryRepository, alerts: AlertNotifier, audit: AuditService, uow: UnitOfWork) -> None:
        self.props, self.cities, self.categories, self.alerts, self.audit, self.uow = props, cities, categories, alerts, audit, uow

    def execute(self, actor: Actor, cmd: CreatePropertyCmd) -> e.Property:
        if not actor.is_owner:
            raise ForbiddenError("Activez le rôle propriétaire dans votre profil pour publier une annonce.")
        if not self.cities.get(cmd.city_id) or not self.categories.get(cmd.category_id):
            raise ValidationFailedError("Ville ou catégorie inconnue.")
        prop = e.Property(
            owner_id=actor.id, city_id=cmd.city_id, category_id=cmd.category_id, title=cmd.title.strip(),
            description=cmd.description, price=cmd.price, rooms=cmd.rooms, surface_m2=cmd.surface_m2,
            address=cmd.address, latitude=cmd.latitude, longitude=cmd.longitude,
            coliving_allowed=cmd.coliving_allowed, max_roommates=cmd.max_roommates, conditions=cmd.conditions,
            available_from=cmd.available_from,
            status=PropertyStatus.AVAILABLE if cmd.publish else PropertyStatus.DRAFT)
        _validate(prop)
        prop = self.props.add(prop)
        self.audit.log(actor.id, "property.create", "property", prop.id)
        if prop.status == PropertyStatus.AVAILABLE:
            self.alerts.new_property(prop)
        self.uow.commit()
        return prop


class UpdateProperty:
    def __init__(self, access: PropertyAccess, props: ports.PropertyRepository, cities: ports.CityRepository,
                 categories: ports.CategoryRepository, audit: AuditService, uow: UnitOfWork) -> None:
        self.access, self.props, self.cities, self.categories, self.audit, self.uow = access, props, cities, categories, audit, uow

    def execute(self, actor: Actor, property_id: int, changes: dict) -> e.Property:
        prop = self.access.owned(actor, property_id)
        if "city_id" in changes and not self.cities.get(changes["city_id"]):
            raise ValidationFailedError("Ville inconnue.")
        if "category_id" in changes and not self.categories.get(changes["category_id"]):
            raise ValidationFailedError("Catégorie inconnue.")
        for k, v in changes.items():
            if k in EDITABLE:
                setattr(prop, k, v)
        _validate(prop)
        self.props.update(prop)
        self.audit.log(actor.id, "property.update", "property", prop.id)
        self.uow.commit()
        return prop


class SetPropertyStatus:
    ALLOWED = {PropertyStatus.DRAFT, PropertyStatus.AVAILABLE, PropertyStatus.SUSPENDED}

    def __init__(self, access: PropertyAccess, props: ports.PropertyRepository, alerts: AlertNotifier,
                 audit: AuditService, uow: UnitOfWork) -> None:
        self.access, self.props, self.alerts, self.audit, self.uow = access, props, alerts, audit, uow

    def execute(self, actor: Actor, property_id: int, status: PropertyStatus) -> e.Property:
        prop = self.access.owned(actor, property_id)
        if status not in self.ALLOWED:
            raise ValidationFailedError("Statut non autorisé (une annonce devient « louée » à la confirmation d'une location).")
        if prop.status == PropertyStatus.RENTED:
            raise ConflictError("Cette annonce est déjà louée.")
        was_available = prop.status == PropertyStatus.AVAILABLE
        prop.status = status
        self.props.update(prop)
        if status == PropertyStatus.AVAILABLE and not was_available:
            self.alerts.new_property(prop)
        self.audit.log(actor.id, "property.status", "property", prop.id, status=status.value)
        self.uow.commit()
        return prop


class DeleteProperty:
    def __init__(self, access: PropertyAccess, props: ports.PropertyRepository, audit: AuditService, uow: UnitOfWork) -> None:
        self.access, self.props, self.audit, self.uow = access, props, audit, uow

    def execute(self, actor: Actor, property_id: int) -> None:
        prop = self.access.owned(actor, property_id)
        prop.deleted_at, prop.status = utcnow(), PropertyStatus.SUSPENDED  # suppression logique : conserve l'historique
        self.props.update(prop)
        self.audit.log(actor.id, "property.delete", "property", prop.id)
        self.uow.commit()


class GetProperty:
    def __init__(self, access: PropertyAccess, props: ports.PropertyRepository, images: ports.PropertyImageRepository,
                 cities: ports.CityRepository, categories: ports.CategoryRepository, favorites: ports.FavoriteRepository,
                 reviews: ports.ReviewRepository, directory: UserDirectory, uow: UnitOfWork) -> None:
        self.access, self.props, self.images, self.cities, self.categories = access, props, images, cities, categories
        self.favorites, self.reviews, self.directory, self.uow = favorites, reviews, directory, uow

    def execute(self, property_id: int, viewer_id: int | None) -> PropertyDetail:
        prop = self.access.visible(property_id, viewer_id)
        if viewer_id != prop.owner_id:
            self.props.increment_views(prop.id)
            self.uow.commit()
        city, cat = self.cities.get(prop.city_id), self.categories.get(prop.category_id)
        ratings = [r.rating for r in self.reviews.list_for_user(prop.owner_id)]
        return PropertyDetail(
            prop, city.name if city else "", cat.name if cat else "", self.images.list_for_properties([prop.id])[prop.id],
            self.directory.name_of(prop.owner_id), average(ratings),
            bool(viewer_id and self.favorites.find(viewer_id, prop.id)))


class SearchProperties:
    def __init__(self, props: ports.PropertyRepository, cards: CardBuilder) -> None:
        self.props, self.cards = props, cards

    def execute(self, criteria: PropertySearchCriteria, page: int, size: int, viewer_id: int | None) -> Page:
        criteria.available_only, criteria.owner_id, criteria.status = True, None, None
        rows, total = self.props.search(criteria, page, size)
        return Page(self.cards.build(rows, viewer_id), total, page, size)


class ListMyProperties:
    def __init__(self, props: ports.PropertyRepository, cards: CardBuilder) -> None:
        self.props, self.cards = props, cards

    def execute(self, actor: Actor, status: PropertyStatus | None, page: int, size: int) -> Page:
        c = PropertySearchCriteria(owner_id=actor.id, status=status, available_only=False)
        rows, total = self.props.search(c, page, size)
        return Page(self.cards.build(rows), total, page, size)


class MapProperties:
    def __init__(self, props: ports.PropertyRepository, cards: CardBuilder) -> None:
        self.props, self.cards = props, cards

    def execute(self, criteria: PropertySearchCriteria) -> list[PropertyCard]:
        criteria.available_only, criteria.owner_id, criteria.status = True, None, None
        return self.cards.build(self.props.list_for_map(criteria))


class AddPropertyImage:
    def __init__(self, access: PropertyAccess, images: ports.PropertyImageRepository, storage: FileStorage,
                 audit: AuditService, uow: UnitOfWork) -> None:
        self.access, self.images, self.storage, self.audit, self.uow = access, images, storage, audit, uow

    def execute(self, actor: Actor, property_id: int, file: UploadedFile) -> e.PropertyImage:
        self.access.owned(actor, property_id)
        if len(self.images.list_for_properties([property_id])[property_id]) >= MAX_IMAGES:
            raise ConflictError(f"Une annonce peut contenir au maximum {MAX_IMAGES} photos.")
        check_image(file.data)          # vérifie le contenu réel et les dimensions
        path = self.storage.save("properties", file, IMAGE_MIMES, settings.max_image_mb * 1024 * 1024, private=False)
        img = self.images.add(e.PropertyImage(property_id=property_id, path=path, position=self.images.next_position(property_id)))
        self.audit.log(actor.id, "property.image_add", "property", property_id)
        self.uow.commit()
        return img


class DeletePropertyImage:
    def __init__(self, access: PropertyAccess, images: ports.PropertyImageRepository, storage: FileStorage, uow: UnitOfWork) -> None:
        self.access, self.images, self.storage, self.uow = access, images, storage, uow

    def execute(self, actor: Actor, property_id: int, image_id: int) -> None:
        self.access.owned(actor, property_id)
        img = self.images.get(image_id)
        if img is None or img.property_id != property_id:
            raise NotFoundError("Photo introuvable.")
        self.images.delete(image_id)
        self.uow.commit()
        self.storage.delete(img.path)


class PropertyStats:
    def __init__(self, access: PropertyAccess, props: ports.PropertyRepository) -> None:
        self.access, self.props = access, props

    def execute(self, actor: Actor, property_id: int) -> dict:
        prop = self.access.owned(actor, property_id)
        return {"views": prop.view_count, "favorites": self.props.count_favorites(prop.id),
                "rental_requests": self.props.count_rental_requests(prop.id)}


class ToggleFavorite:
    def __init__(self, access: PropertyAccess, favorites: ports.FavoriteRepository, uow: UnitOfWork) -> None:
        self.access, self.favorites, self.uow = access, favorites, uow

    def execute(self, actor: Actor, property_id: int, add: bool) -> None:
        self.access.visible(property_id, actor.id)
        existing = self.favorites.find(actor.id, property_id)
        if add and not existing:
            self.favorites.add(e.Favorite(user_id=actor.id, property_id=property_id))
        elif not add and existing:
            self.favorites.delete(existing.id)
        self.uow.commit()


class ListFavorites:
    def __init__(self, favorites: ports.FavoriteRepository, cards: CardBuilder) -> None:
        self.favorites, self.cards = favorites, cards

    def execute(self, actor: Actor) -> list[PropertyCard]:
        return self.cards.build(self.favorites.list_properties(actor.id), actor.id)


class SavedSearches:
    def __init__(self, searches: ports.SavedSearchRepository, alerts: ports.SearchAlertRepository, uow: UnitOfWork) -> None:
        self.searches, self.alerts, self.uow = searches, alerts, uow

    def create(self, actor: Actor, name: str, filters: dict, alert: bool) -> tuple[e.SavedSearch, bool]:
        saved = self.searches.add(e.SavedSearch(user_id=actor.id, name=name.strip(), filters=filters))
        if alert:
            self.alerts.add(e.SearchAlert(saved_search_id=saved.id, is_active=True))
        self.uow.commit()
        return saved, alert

    def list(self, actor: Actor) -> list[tuple[e.SavedSearch, bool]]:
        out = []
        for s in self.searches.list_by_user(actor.id):
            a = self.alerts.get_by_search(s.id)
            out.append((s, bool(a and a.is_active)))
        return out

    def _own(self, actor: Actor, search_id: int) -> e.SavedSearch:
        s = self.searches.get(search_id)
        if s is None or s.user_id != actor.id:
            raise NotFoundError("Recherche introuvable.")
        return s

    def delete(self, actor: Actor, search_id: int) -> None:
        self._own(actor, search_id)
        self.searches.delete(search_id)
        self.uow.commit()

    def set_alert(self, actor: Actor, search_id: int, active: bool) -> None:
        self._own(actor, search_id)
        alert = self.alerts.get_by_search(search_id)
        if alert:
            alert.is_active = active
            self.alerts.update(alert)
        else:
            self.alerts.add(e.SearchAlert(saved_search_id=search_id, is_active=active))
        self.uow.commit()
