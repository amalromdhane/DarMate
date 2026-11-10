"""Entités du domaine : dataclasses pures (aucune dépendance framework)."""
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from app.domain.entities.enums import (
    ConversationType, DocumentStatus, NotificationType, PropertyStatus, RentalStatus,
    ReportStatus, RequestStatus, ReviewTarget, UserStatus, VisitStatus,
)

_E = dict(kw_only=True)


@dataclass(**_E)
class Role:
    id: int | None = None
    name: str = ""


@dataclass(**_E)
class User:
    id: int | None = None
    email: str
    password_hash: str
    status: UserStatus = UserStatus.ACTIVE
    failed_login_count: int = 0
    locked_until: datetime | None = None
    last_login_at: datetime | None = None
    created_at: datetime | None = None

    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE


@dataclass(**_E)
class UserProfile:
    id: int | None = None
    user_id: int
    first_name: str = ""
    last_name: str = ""
    phone: str | None = None
    bio: str | None = None
    birth_date: date | None = None
    city_id: int | None = None
    language: str = "fr"


@dataclass(**_E)
class RefreshToken:
    id: int | None = None
    user_id: int
    token_hash: str
    expires_at: datetime
    revoked_at: datetime | None = None


@dataclass(**_E)
class PasswordResetToken:
    id: int | None = None
    user_id: int
    token_hash: str
    expires_at: datetime
    used_at: datetime | None = None


@dataclass(**_E)
class IdentityDocument:
    id: int | None = None
    user_id: int
    path: str
    doc_type: str = "ID_CARD"
    status: DocumentStatus = DocumentStatus.PENDING
    created_at: datetime | None = None


@dataclass(**_E)
class UserBlock:
    id: int | None = None
    blocker_id: int
    blocked_id: int


@dataclass(**_E)
class AuditLog:
    id: int | None = None
    user_id: int | None = None
    action: str
    entity_type: str | None = None
    entity_id: int | None = None
    details: dict[str, Any] | None = None
    created_at: datetime | None = None


@dataclass(**_E)
class Region:
    id: int | None = None
    name: str


@dataclass(**_E)
class City:
    id: int | None = None
    region_id: int
    name: str


@dataclass(**_E)
class PropertyCategory:
    id: int | None = None
    name: str


@dataclass(**_E)
class Property:
    id: int | None = None
    owner_id: int
    city_id: int
    category_id: int
    title: str
    description: str = ""
    price: Decimal
    rooms: int = 1
    surface_m2: int | None = None
    address: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    coliving_allowed: bool = False
    max_roommates: int = 1
    conditions: str | None = None
    available_from: date | None = None
    status: PropertyStatus = PropertyStatus.DRAFT
    view_count: int = 0
    deleted_at: datetime | None = None
    created_at: datetime | None = None


@dataclass(**_E)
class PropertyImage:
    id: int | None = None
    property_id: int
    path: str
    position: int = 0


@dataclass(**_E)
class Favorite:
    id: int | None = None
    user_id: int
    property_id: int


@dataclass(**_E)
class SavedSearch:
    id: int | None = None
    user_id: int
    name: str
    filters: dict[str, Any]
    created_at: datetime | None = None


@dataclass(**_E)
class SearchAlert:
    id: int | None = None
    saved_search_id: int
    is_active: bool = True
    last_notified_at: datetime | None = None


@dataclass(**_E)
class RoommateProfile:
    id: int | None = None
    user_id: int
    city_id: int | None = None
    budget_min: Decimal | None = None
    budget_max: Decimal | None = None
    smoker: bool = False
    has_pets: bool = False
    schedule: str = "FLEXIBLE"  # EARLY | NIGHT | FLEXIBLE
    cleanliness: int = 3
    sociability: int = 3
    about: str | None = None
    is_active: bool = True


@dataclass(**_E)
class RoommateRequest:
    id: int | None = None
    sender_id: int
    receiver_id: int
    message: str | None = None
    status: RequestStatus = RequestStatus.PENDING
    created_at: datetime | None = None


@dataclass(**_E)
class RoommateGroup:
    id: int | None = None
    name: str
    creator_id: int
    max_members: int = 4
    created_at: datetime | None = None


@dataclass(**_E)
class GroupMember:
    id: int | None = None
    group_id: int
    user_id: int
    role: str = "MEMBER"  # ADMIN | MEMBER


@dataclass(**_E)
class GroupInvitation:
    id: int | None = None
    group_id: int
    inviter_id: int
    invitee_id: int
    status: RequestStatus = RequestStatus.PENDING
    created_at: datetime | None = None


@dataclass(**_E)
class RentalRequest:
    id: int | None = None
    property_id: int
    created_by_id: int
    applicant_user_id: int | None = None
    group_id: int | None = None
    message: str | None = None
    desired_move_in: date | None = None
    status: RentalStatus = RentalStatus.PENDING
    created_at: datetime | None = None


@dataclass(**_E)
class Visit:
    id: int | None = None
    property_id: int
    requester_id: int
    rental_request_id: int | None = None
    status: VisitStatus = VisitStatus.PROPOSED
    note: str | None = None
    created_at: datetime | None = None


@dataclass(**_E)
class VisitSlot:
    id: int | None = None
    visit_id: int
    proposed_by_id: int
    starts_at: datetime
    ends_at: datetime
    is_selected: bool = False


@dataclass(**_E)
class Review:
    id: int | None = None
    rental_request_id: int
    reviewer_id: int
    reviewee_id: int
    property_id: int
    target_type: ReviewTarget
    rating: int
    comment: str | None = None
    created_at: datetime | None = None


@dataclass(**_E)
class Conversation:
    id: int | None = None
    type: ConversationType = ConversationType.PRIVATE
    group_id: int | None = None
    private_key: str | None = None
    created_at: datetime | None = None


@dataclass(**_E)
class ConversationMember:
    id: int | None = None
    conversation_id: int
    user_id: int
    last_read_at: datetime | None = None


@dataclass(**_E)
class Message:
    id: int | None = None
    conversation_id: int
    sender_id: int
    body: str | None = None
    property_id: int | None = None
    created_at: datetime | None = None


@dataclass(**_E)
class MessageAttachment:
    id: int | None = None
    message_id: int
    path: str
    original_name: str
    mime_type: str
    size_bytes: int


@dataclass(**_E)
class Notification:
    id: int | None = None
    user_id: int
    type: NotificationType
    title: str
    body: str | None = None
    link: str | None = None
    is_read: bool = False
    created_at: datetime | None = None


@dataclass(**_E)
class Report:
    id: int | None = None
    reporter_id: int
    reported_user_id: int | None = None
    message_id: int | None = None
    reason: str
    details: str | None = None
    status: ReportStatus = ReportStatus.OPEN
    created_at: datetime | None = None


@dataclass(**_E)
class ApplicationSetting:
    id: int | None = None
    key: str
    value: str
