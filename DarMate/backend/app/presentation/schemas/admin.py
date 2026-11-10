from pydantic import BaseModel, Field

from app.domain.entities.enums import UserStatus
from app.presentation.schemas.common import ORM


class NameIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class CityIn(BaseModel):
    region_id: int
    name: str = Field(min_length=1, max_length=100)


class CityUpdateIn(BaseModel):
    region_id: int | None = None
    name: str | None = Field(default=None, min_length=1, max_length=100)


class RegionOut(ORM):
    id: int
    name: str


class CityOut(ORM):
    id: int
    region_id: int
    name: str


class CategoryOut(ORM):
    id: int
    name: str


class AdminUserOut(BaseModel):
    id: int
    email: str
    status: UserStatus
    roles: list[str]
    created_at: str | None = None


class UserStatusIn(BaseModel):
    status: UserStatus
