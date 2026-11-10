from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.entities.enums import PropertyStatus
from app.presentation.schemas.common import ORM


class PropertyIn(BaseModel):
    city_id: int
    category_id: int
    title: str = Field(min_length=3, max_length=150)
    description: str = Field(default="", max_length=5000)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    rooms: int = Field(default=1, ge=1, le=50)
    surface_m2: int | None = Field(default=None, ge=1, le=100000)
    address: str | None = Field(default=None, max_length=255)
    latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180)
    coliving_allowed: bool = False
    max_roommates: int = Field(default=1, ge=1, le=10)
    conditions: str | None = Field(default=None, max_length=3000)
    available_from: date | None = None
    publish: bool = False


class PropertyUpdateIn(BaseModel):
    city_id: int | None = None
    category_id: int | None = None
    title: str | None = Field(default=None, min_length=3, max_length=150)
    description: str | None = Field(default=None, max_length=5000)
    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    rooms: int | None = Field(default=None, ge=1, le=50)
    surface_m2: int | None = Field(default=None, ge=1, le=100000)
    address: str | None = Field(default=None, max_length=255)
    latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180)
    coliving_allowed: bool | None = None
    max_roommates: int | None = Field(default=None, ge=1, le=10)
    conditions: str | None = Field(default=None, max_length=3000)
    available_from: date | None = None


class StatusIn(BaseModel):
    status: PropertyStatus


class PropertyOut(ORM):
    id: int
    owner_id: int
    city_id: int
    category_id: int
    title: str
    description: str
    price: Decimal
    rooms: int
    surface_m2: int | None
    address: str | None
    latitude: Decimal | None
    longitude: Decimal | None
    coliving_allowed: bool
    max_roommates: int
    conditions: str | None
    available_from: date | None
    status: PropertyStatus
    view_count: int
    created_at: datetime | None


class ImageOut(ORM):
    id: int
    path: str
    position: int


class PropertyCardOut(BaseModel):
    id: int
    title: str
    price: Decimal
    rooms: int
    surface_m2: int | None
    city_id: int
    city_name: str
    coliving_allowed: bool
    max_roommates: int
    status: PropertyStatus
    latitude: Decimal | None
    longitude: Decimal | None
    cover: str | None
    is_favorite: bool
    created_at: datetime | None


class PropertyDetailOut(PropertyOut):
    city_name: str
    category_name: str
    images: list[ImageOut]
    owner_name: str
    owner_rating_avg: float | None
    is_favorite: bool


class SavedSearchIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    filters: dict = Field(default_factory=dict)
    alert: bool = False


class SavedSearchOut(BaseModel):
    id: int
    name: str
    filters: dict
    alert_active: bool


class AlertIn(BaseModel):
    active: bool
