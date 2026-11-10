from sqlalchemy import func, select, update

from app.core.clock import utcnow
from app.domain.entities import entities as e
from app.domain.entities.enums import PropertyStatus
from app.domain.repositories import ports
from app.domain.repositories.ports import PropertySearchCriteria
from app.infrastructure.models.property import (
    FavoriteModel, PropertyImageModel, PropertyModel, SavedSearchModel, SearchAlertModel,
)
from app.infrastructure.models.rental import RentalRequestModel
from app.infrastructure.repositories.base import SqlRepository


class SqlPropertyRepository(SqlRepository[e.Property], ports.PropertyRepository):
    model, entity = PropertyModel, e.Property

    def _filtered(self, c: PropertySearchCriteria):
        stmt = select(PropertyModel)
        if not c.include_deleted:
            stmt = stmt.where(PropertyModel.deleted_at.is_(None))
        if c.owner_id:
            stmt = stmt.where(PropertyModel.owner_id == c.owner_id)
        if c.status:
            stmt = stmt.where(PropertyModel.status == c.status)
        elif c.available_only:
            stmt = stmt.where(PropertyModel.status == PropertyStatus.AVAILABLE)
        if c.city_id:
            stmt = stmt.where(PropertyModel.city_id == c.city_id)
        if c.category_id:
            stmt = stmt.where(PropertyModel.category_id == c.category_id)
        if c.min_price is not None:
            stmt = stmt.where(PropertyModel.price >= c.min_price)
        if c.max_price is not None:
            stmt = stmt.where(PropertyModel.price <= c.max_price)
        if c.min_rooms:
            stmt = stmt.where(PropertyModel.rooms >= c.min_rooms)
        if c.coliving:
            stmt = stmt.where(PropertyModel.coliving_allowed.is_(True))
        if c.text:
            like = f"%{c.text}%"
            stmt = stmt.where(PropertyModel.title.like(like) | PropertyModel.description.like(like))
        return stmt

    def search(self, c, page, size):
        stmt = self._filtered(c)
        total = self.s.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
        order = {"price_asc": PropertyModel.price.asc(), "price_desc": PropertyModel.price.desc()}.get(
            c.sort, PropertyModel.id.desc())
        rows = self._all(stmt.order_by(order, PropertyModel.id.desc()).offset((page - 1) * size).limit(size))
        return rows, total

    def list_for_map(self, c):
        stmt = self._filtered(c).where(PropertyModel.latitude.is_not(None), PropertyModel.longitude.is_not(None))
        return self._all(stmt.limit(500))

    def increment_views(self, property_id):
        self.s.execute(update(PropertyModel).where(PropertyModel.id == property_id)
                       .values(view_count=PropertyModel.view_count + 1))

    def count_favorites(self, property_id):
        return self.s.execute(select(func.count()).select_from(FavoriteModel)
                              .where(FavoriteModel.property_id == property_id)).scalar_one()

    def count_rental_requests(self, property_id):
        return self.s.execute(select(func.count()).select_from(RentalRequestModel)
                              .where(RentalRequestModel.property_id == property_id)).scalar_one()


class SqlPropertyImageRepository(SqlRepository[e.PropertyImage], ports.PropertyImageRepository):
    model, entity = PropertyImageModel, e.PropertyImage

    def list_for_properties(self, ids):
        out: dict[int, list[e.PropertyImage]] = {i: [] for i in ids}
        if ids:
            stmt = select(PropertyImageModel).where(PropertyImageModel.property_id.in_(ids)).order_by(PropertyImageModel.position)
            for img in self._all(stmt):
                out[img.property_id].append(img)
        return out

    def next_position(self, property_id):
        m = self.s.execute(select(func.max(PropertyImageModel.position)).where(PropertyImageModel.property_id == property_id)).scalar()
        return 0 if m is None else m + 1


class SqlFavoriteRepository(SqlRepository[e.Favorite], ports.FavoriteRepository):
    model, entity = FavoriteModel, e.Favorite

    def find(self, user_id, property_id):
        return self._first(select(FavoriteModel).where(FavoriteModel.user_id == user_id, FavoriteModel.property_id == property_id))

    def list_properties(self, user_id):
        stmt = (select(PropertyModel).join(FavoriteModel, FavoriteModel.property_id == PropertyModel.id)
                .where(FavoriteModel.user_id == user_id, PropertyModel.deleted_at.is_(None)).order_by(FavoriteModel.id.desc()))
        props = SqlPropertyRepository(self.s)
        return [props._to_entity(o) for o in self.s.execute(stmt).scalars().all()]


class SqlSavedSearchRepository(SqlRepository[e.SavedSearch], ports.SavedSearchRepository):
    model, entity = SavedSearchModel, e.SavedSearch

    def list_by_user(self, user_id):
        return self._all(select(SavedSearchModel).where(SavedSearchModel.user_id == user_id).order_by(SavedSearchModel.id.desc()))


class SqlSearchAlertRepository(SqlRepository[e.SearchAlert], ports.SearchAlertRepository):
    model, entity = SearchAlertModel, e.SearchAlert

    def get_by_search(self, saved_search_id):
        return self._first(select(SearchAlertModel).where(SearchAlertModel.saved_search_id == saved_search_id))

    def list_active_with_search(self):
        stmt = select(SearchAlertModel, SavedSearchModel).join(
            SavedSearchModel, SavedSearchModel.id == SearchAlertModel.saved_search_id).where(SearchAlertModel.is_active.is_(True))
        searches = SqlSavedSearchRepository(self.s)
        return [(self._to_entity(a), searches._to_entity(s)) for a, s in self.s.execute(stmt).all()]
