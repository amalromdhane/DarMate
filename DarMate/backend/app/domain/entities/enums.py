from enum import Enum


class UserStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    BANNED = "BANNED"


class RoleName(str, Enum):
    SEEKER = "SEEKER"
    OWNER = "OWNER"
    ADMIN = "ADMIN"


class PropertyStatus(str, Enum):
    DRAFT = "DRAFT"
    AVAILABLE = "AVAILABLE"
    SUSPENDED = "SUSPENDED"
    RENTED = "RENTED"


class RentalStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class VisitStatus(str, Enum):
    PROPOSED = "PROPOSED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class RequestStatus(str, Enum):  # invitations & demandes de binôme
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class ReviewTarget(str, Enum):
    OWNER = "OWNER"
    TENANT = "TENANT"
    PROPERTY = "PROPERTY"


class ConversationType(str, Enum):
    PRIVATE = "PRIVATE"
    GROUP = "GROUP"


class DocumentStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class ReportStatus(str, Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"


class NotificationType(str, Enum):
    MESSAGE = "MESSAGE"
    RENTAL_REQUEST = "RENTAL_REQUEST"
    RENTAL_RESPONSE = "RENTAL_RESPONSE"
    GROUP_INVITATION = "GROUP_INVITATION"
    ROOMMATE_REQUEST = "ROOMMATE_REQUEST"
    VISIT = "VISIT"
    NEW_PROPERTY = "NEW_PROPERTY"
