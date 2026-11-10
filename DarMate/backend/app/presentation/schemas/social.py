from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.entities.enums import RentalStatus, RequestStatus, ReviewTarget
from app.presentation.schemas.common import ORM


class RoommateProfileIn(BaseModel):
    city_id: int | None = None
    budget_min: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    budget_max: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    smoker: bool = False
    has_pets: bool = False
    schedule: str = Field(default="FLEXIBLE", pattern="^(EARLY|NIGHT|FLEXIBLE)$")
    cleanliness: int = Field(default=3, ge=1, le=5)
    sociability: int = Field(default=3, ge=1, le=5)
    about: str | None = Field(default=None, max_length=2000)
    is_active: bool = True


class RoommateProfileOut(ORM):
    id: int
    user_id: int
    city_id: int | None
    budget_min: Decimal | None
    budget_max: Decimal | None
    smoker: bool
    has_pets: bool
    schedule: str
    cleanliness: int
    sociability: int
    about: str | None
    is_active: bool


class RoommateMatchOut(BaseModel):
    profile: RoommateProfileOut
    display_name: str
    score: int


class RoommateRequestIn(BaseModel):
    receiver_id: int
    message: str | None = Field(default=None, max_length=1000)


class RespondIn(BaseModel):
    accept: bool


class RoommateRequestOut(ORM):
    id: int
    sender_id: int
    receiver_id: int
    message: str | None
    status: RequestStatus
    created_at: datetime | None


class GroupIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    max_members: int = Field(default=4, ge=2, le=10)


class MemberOut(BaseModel):
    user_id: int
    name: str
    role: str


class GroupOut(BaseModel):
    id: int
    name: str
    creator_id: int
    max_members: int
    members: list[MemberOut]
    conversation_id: int | None


class InviteIn(BaseModel):
    invitee_id: int


class InvitationOut(ORM):
    id: int
    group_id: int
    inviter_id: int
    invitee_id: int
    status: RequestStatus
    created_at: datetime | None


class RentalRequestIn(BaseModel):
    property_id: int
    group_id: int | None = None
    message: str | None = Field(default=None, max_length=2000)
    desired_move_in: date | None = None


class RentalStatusIn(BaseModel):
    status: RentalStatus


class RentalRequestOut(BaseModel):
    id: int
    property_id: int
    property_title: str
    applicant_label: str
    applicant_user_id: int | None
    group_id: int | None
    message: str | None
    desired_move_in: date | None
    status: RentalStatus
    created_at: datetime | None


class SlotIn(BaseModel):
    starts_at: datetime
    ends_at: datetime


class SlotOut(ORM):
    id: int
    proposed_by_id: int
    starts_at: datetime
    ends_at: datetime
    is_selected: bool


class VisitIn(BaseModel):
    property_id: int
    rental_request_id: int | None = None
    note: str | None = Field(default=None, max_length=1000)
    slots: list[SlotIn] = Field(min_length=1, max_length=5)


class SlotsIn(BaseModel):
    slots: list[SlotIn] = Field(min_length=1, max_length=5)


class VisitActionIn(BaseModel):
    action: str = Field(pattern="^(accept|reject|cancel)$")
    slot_id: int | None = None


class VisitOut(BaseModel):
    id: int
    property_id: int
    property_title: str
    requester_id: int
    status: str
    note: str | None
    slots: list[SlotOut]


class ReviewIn(BaseModel):
    rental_request_id: int
    target_type: ReviewTarget
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=2000)
    reviewee_id: int | None = None


class ReviewOut(ORM):
    id: int
    rental_request_id: int
    reviewer_id: int
    reviewee_id: int
    property_id: int
    target_type: ReviewTarget
    rating: int
    comment: str | None
    created_at: datetime | None


class ReviewListOut(BaseModel):
    items: list[ReviewOut]
    average: float | None
    count: int
