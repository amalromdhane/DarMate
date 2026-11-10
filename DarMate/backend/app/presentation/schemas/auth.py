from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field

from app.domain.entities.enums import UserStatus
from app.presentation.schemas.common import ORM


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    roles: list[str] = Field(default=["SEEKER"], min_length=1)
    phone: str | None = Field(default=None, max_length=30)


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class ForgotPasswordIn(BaseModel):
    email: EmailStr


class ResetPasswordIn(BaseModel):
    token: str = Field(min_length=10, max_length=200)
    new_password: str = Field(min_length=8, max_length=128)


class ChangePasswordIn(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class ProfileOut(ORM):
    first_name: str = ""
    last_name: str = ""
    phone: str | None = None
    bio: str | None = None
    birth_date: date | None = None
    city_id: int | None = None
    language: str = "fr"


class UserOut(BaseModel):
    id: int
    email: str
    status: UserStatus
    roles: list[str]
    profile: ProfileOut | None = None
    created_at: datetime | None = None


class PublicUserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    bio: str | None = None
    city_id: int | None = None
    roles: list[str]
    rating_avg: float | None = None
    rating_count: int = 0


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ProfileUpdateIn(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=80)
    last_name: str | None = Field(default=None, min_length=1, max_length=80)
    phone: str | None = Field(default=None, max_length=30)
    bio: str | None = Field(default=None, max_length=2000)
    birth_date: date | None = None
    city_id: int | None = None
    language: str | None = Field(default=None, pattern="^(fr|en|ar)$")
    roles: list[str] | None = None


class ReportIn(BaseModel):
    reported_user_id: int
    reason: str = Field(min_length=3, max_length=100)
    details: str | None = Field(default=None, max_length=2000)
    message_id: int | None = None
