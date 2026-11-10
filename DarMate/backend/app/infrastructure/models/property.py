from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import JSON, Boolean, Date, DateTime, Enum, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.entities.enums import PropertyStatus
from app.infrastructure.database.base import PK, Base, created, pk


class PropertyModel(Base):
    __tablename__ = "property"
    __table_args__ = (
        Index("ix_property_search", "city_id", "price", "status"),
    )
    id: Mapped[int] = pk()
    owner_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="RESTRICT"), index=True)
    city_id: Mapped[int] = mapped_column(Integer, ForeignKey("city.id", ondelete="RESTRICT"))
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("property_category.id", ondelete="RESTRICT"))
    title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text, default="")
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    rooms: Mapped[int] = mapped_column(Integer, default=1)
    surface_m2: Mapped[int | None] = mapped_column(Integer)
    address: Mapped[str | None] = mapped_column(String(255))
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    coliving_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    max_roommates: Mapped[int] = mapped_column(Integer, default=1)
    conditions: Mapped[str | None] = mapped_column(Text)
    available_from: Mapped[date | None] = mapped_column(Date)
    status: Mapped[PropertyStatus] = mapped_column(Enum(PropertyStatus, native_enum=False, length=20), default=PropertyStatus.DRAFT)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = created()
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class PropertyImageModel(Base):
    __tablename__ = "property_image"
    id: Mapped[int] = pk()
    property_id: Mapped[int] = mapped_column(PK, ForeignKey("property.id", ondelete="CASCADE"), index=True)
    path: Mapped[str] = mapped_column(String(255))
    position: Mapped[int] = mapped_column(Integer, default=0)


class FavoriteModel(Base):
    __tablename__ = "favorite"
    __table_args__ = (UniqueConstraint("user_id", "property_id"),)
    id: Mapped[int] = pk()
    user_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="CASCADE"), index=True)
    property_id: Mapped[int] = mapped_column(PK, ForeignKey("property.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = created()


class SavedSearchModel(Base):
    __tablename__ = "saved_search"
    id: Mapped[int] = pk()
    user_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    filters: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = created()


class SearchAlertModel(Base):
    __tablename__ = "search_alert"
    id: Mapped[int] = pk()
    saved_search_id: Mapped[int] = mapped_column(PK, ForeignKey("saved_search.id", ondelete="CASCADE"), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_notified_at: Mapped[datetime | None] = mapped_column(DateTime)
