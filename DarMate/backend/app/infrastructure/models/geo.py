from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class RegionModel(Base):
    __tablename__ = "region"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)


class CityModel(Base):
    __tablename__ = "city"
    __table_args__ = (UniqueConstraint("region_id", "name"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    region_id: Mapped[int] = mapped_column(Integer, ForeignKey("region.id", ondelete="RESTRICT"), index=True)
    name: Mapped[str] = mapped_column(String(100))


class PropertyCategoryModel(Base):
    __tablename__ = "property_category"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
