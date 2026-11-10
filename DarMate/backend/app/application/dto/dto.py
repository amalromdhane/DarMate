"""DTO applicatifs : commandes en entrée, vues en sortie des use cases."""
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from app.domain.entities import entities as e
from app.domain.entities.enums import RoleName


@dataclass(frozen=True)
class Actor:
    """Utilisateur authentifié qui exécute un use case."""
    id: int
    roles: tuple[str, ...] = ()

    @property
    def is_admin(self) -> bool:
        return RoleName.ADMIN.value in self.roles

    @property
    def is_owner(self) -> bool:
        return RoleName.OWNER.value in self.roles


# ---------- Commandes ----------
@dataclass
class RegisterCmd:
    email: str
    password: str
    first_name: str
    last_name: str
    roles: list[str] = field(default_factory=lambda: [RoleName.SEEKER.value])
    phone: str | None = None


@dataclass
class CreatePropertyCmd:
    city_id: int
    category_id: int
    title: str
    price: Decimal
    description: str = ""
    rooms: int = 1
    surface_m2: int | None = None
    address: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    coliving_allowed: bool = False
    max_roommates: int = 1
    conditions: str | None = None
    available_from: date | None = None
    publish: bool = False


@dataclass
class SlotCmd:
    starts_at: datetime
    ends_at: datetime


# ---------- Vues ----------
@dataclass
class AuthResult:
    access_token: str
    refresh_token: str
    user: e.User
    roles: list[str]


@dataclass
class UserView:
    user: e.User
    profile: e.UserProfile | None
    roles: list[str]
    rating_avg: float | None = None
    rating_count: int = 0


@dataclass
class PropertyCard:
    property: e.Property
    city_name: str
    cover: str | None
    is_favorite: bool = False


@dataclass
class PropertyDetail:
    property: e.Property
    city_name: str
    category_name: str
    images: list[e.PropertyImage]
    owner_name: str
    owner_rating_avg: float | None
    is_favorite: bool


@dataclass
class Page:
    items: list[Any]
    total: int
    page: int
    size: int


@dataclass
class RoommateMatch:
    profile: e.RoommateProfile
    display_name: str
    score: int


@dataclass
class GroupView:
    group: e.RoommateGroup
    members: list[tuple[e.GroupMember, str]]
    conversation_id: int | None = None


@dataclass
class RentalRequestView:
    request: e.RentalRequest
    property_title: str
    applicant_label: str


@dataclass
class VisitView:
    visit: e.Visit
    property_title: str
    slots: list[e.VisitSlot]


@dataclass
class ConversationView:
    conversation: e.Conversation
    title: str
    member_ids: list[int]
    last_message: e.Message | None
    unread_count: int


@dataclass
class MessageView:
    message: e.Message
    attachments: list[e.MessageAttachment]
    status: str  # sent | read


@dataclass
class ReviewSummary:
    items: list[e.Review]
    average: float | None
    count: int
