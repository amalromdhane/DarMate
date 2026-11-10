from sqlalchemy import select

from app.domain.entities import entities as e
from app.domain.repositories import ports
from app.infrastructure.models.geo import CityModel, PropertyCategoryModel, RegionModel
from app.infrastructure.repositories.base import SqlRepository


class SqlRegionRepository(SqlRepository[e.Region], ports.RegionRepository):
    model, entity = RegionModel, e.Region

    def list_all(self):
        return self._all(select(RegionModel).order_by(RegionModel.name))


class SqlCityRepository(SqlRepository[e.City], ports.CityRepository):
    model, entity = CityModel, e.City

    def list_all(self, region_id=None):
        stmt = select(CityModel).order_by(CityModel.name)
        if region_id:
            stmt = stmt.where(CityModel.region_id == region_id)
        return self._all(stmt)


class SqlCategoryRepository(SqlRepository[e.PropertyCategory], ports.CategoryRepository):
    model, entity = PropertyCategoryModel, e.PropertyCategory

    def list_all(self):
        return self._all(select(PropertyCategoryModel).order_by(PropertyCategoryModel.name))
