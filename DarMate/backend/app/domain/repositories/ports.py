"""Interfaces des repositories (abstractions utilisées par la couche Application)."""
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.domain.entities import entities as e
from app.domain.entities.enums import PropertyStatus, RentalStatus, UserStatus
from app.domain.repositories.base import Repository


@dataclass
class PropertySearchCriteria:
    city_id: int | None = None
    category_id: int | None = None
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    min_rooms: int | None = None
    coliving: bool | None = None
    available_only: bool = True
    owner_id: int | None = None
    include_deleted: bool = False
    status: PropertyStatus | None = None
    text: str | None = None
    sort: str = "recent"  # recent | price_asc | price_desc


class UserRepository(Repository[e.User]):
    @abstractmethod
    def get_by_email(self, email: str) -> e.User | None: ...
    @abstractmethod
    def get_roles(self, user_id: int) -> list[str]: ...
    @abstractmethod
    def set_roles(self, user_id: int, roles: list[str]) -> None: ...
    @abstractmethod
    def search(self, text: str | None, status: UserStatus | None, page: int, size: int) -> tuple[list[e.User], int]: ...


class UserProfileRepository(Repository[e.UserProfile]):
    @abstractmethod
    def get_by_user(self, user_id: int) -> e.UserProfile | None: ...


class RefreshTokenRepository(Repository[e.RefreshToken]):
    @abstractmethod
    def get_by_hash(self, token_hash: str) -> e.RefreshToken | None: ...
    @abstractmethod
    def revoke_all_for_user(self, user_id: int) -> None: ...


class PasswordResetRepository(Repository[e.PasswordResetToken]):
    @abstractmethod
    def get_by_hash(self, token_hash: str) -> e.PasswordResetToken | None: ...


class IdentityDocumentRepository(Repository[e.IdentityDocument]): ...
class AuditLogRepository(Repository[e.AuditLog]): ...
class ReportRepository(Repository[e.Report]): ...


class UserBlockRepository(Repository[e.UserBlock]):
    @abstractmethod
    def find(self, blocker_id: int, blocked_id: int) -> e.UserBlock | None: ...
    @abstractmethod
    def exists_between(self, a: int, b: int) -> bool: ...


class SettingRepository(Repository[e.ApplicationSetting]):
    @abstractmethod
    def get_by_key(self, key: str) -> e.ApplicationSetting | None: ...
    @abstractmethod
    def all_as_dict(self) -> dict[str, str]: ...


class RegionRepository(Repository[e.Region]):
    @abstractmethod
    def list_all(self) -> list[e.Region]: ...


class CityRepository(Repository[e.City]):
    @abstractmethod
    def list_all(self, region_id: int | None = None) -> list[e.City]: ...


class CategoryRepository(Repository[e.PropertyCategory]):
    @abstractmethod
    def list_all(self) -> list[e.PropertyCategory]: ...


class PropertyRepository(Repository[e.Property]):
    @abstractmethod
    def search(self, c: PropertySearchCriteria, page: int, size: int) -> tuple[list[e.Property], int]: ...
    @abstractmethod
    def list_for_map(self, c: PropertySearchCriteria) -> list[e.Property]: ...
    @abstractmethod
    def increment_views(self, property_id: int) -> None: ...
    @abstractmethod
    def count_favorites(self, property_id: int) -> int: ...
    @abstractmethod
    def count_rental_requests(self, property_id: int) -> int: ...


class PropertyImageRepository(Repository[e.PropertyImage]):
    @abstractmethod
    def list_for_properties(self, ids: list[int]) -> dict[int, list[e.PropertyImage]]: ...
    @abstractmethod
    def next_position(self, property_id: int) -> int: ...


class FavoriteRepository(Repository[e.Favorite]):
    @abstractmethod
    def find(self, user_id: int, property_id: int) -> e.Favorite | None: ...
    @abstractmethod
    def list_properties(self, user_id: int) -> list[e.Property]: ...


class SavedSearchRepository(Repository[e.SavedSearch]):
    @abstractmethod
    def list_by_user(self, user_id: int) -> list[e.SavedSearch]: ...


class SearchAlertRepository(Repository[e.SearchAlert]):
    @abstractmethod
    def get_by_search(self, saved_search_id: int) -> e.SearchAlert | None: ...
    @abstractmethod
    def list_active_with_search(self) -> list[tuple[e.SearchAlert, e.SavedSearch]]: ...


class RoommateProfileRepository(Repository[e.RoommateProfile]):
    @abstractmethod
    def get_by_user(self, user_id: int) -> e.RoommateProfile | None: ...
    @abstractmethod
    def list_active_except(self, user_id: int, city_id: int | None) -> list[e.RoommateProfile]: ...


class RoommateRequestRepository(Repository[e.RoommateRequest]):
    @abstractmethod
    def find_between(self, a: int, b: int) -> e.RoommateRequest | None: ...
    @abstractmethod
    def list_for_user(self, user_id: int) -> list[e.RoommateRequest]: ...


class GroupRepository(Repository[e.RoommateGroup]):
    @abstractmethod
    def list_for_user(self, user_id: int) -> list[e.RoommateGroup]: ...


class GroupMemberRepository(Repository[e.GroupMember]):
    @abstractmethod
    def list_for_group(self, group_id: int) -> list[e.GroupMember]: ...
    @abstractmethod
    def find(self, group_id: int, user_id: int) -> e.GroupMember | None: ...


class GroupInvitationRepository(Repository[e.GroupInvitation]):
    @abstractmethod
    def list_for_invitee(self, user_id: int) -> list[e.GroupInvitation]: ...
    @abstractmethod
    def find_pending(self, group_id: int, invitee_id: int) -> e.GroupInvitation | None: ...


class RentalRequestRepository(Repository[e.RentalRequest]):
    @abstractmethod
    def list_sent(self, user_id: int) -> list[e.RentalRequest]: ...
    @abstractmethod
    def list_received(self, owner_id: int, status: RentalStatus | None) -> list[e.RentalRequest]: ...
    @abstractmethod
    def find_open(self, property_id: int, applicant_user_id: int | None, group_id: int | None) -> e.RentalRequest | None: ...
    @abstractmethod
    def participant_ids(self, request: e.RentalRequest) -> list[int]: ...
    @abstractmethod
    def reject_other_pending(self, property_id: int, except_id: int) -> list[e.RentalRequest]: ...


class VisitRepository(Repository[e.Visit]):
    @abstractmethod
    def list_for_user(self, user_id: int) -> list[e.Visit]: ...


class VisitSlotRepository(Repository[e.VisitSlot]):
    @abstractmethod
    def list_for_visit(self, visit_id: int) -> list[e.VisitSlot]: ...
    @abstractmethod
    def list_for_visits(self, ids: list[int]) -> dict[int, list[e.VisitSlot]]: ...


class ReviewRepository(Repository[e.Review]):
    @abstractmethod
    def find(self, rental_request_id: int, reviewer_id: int, target_type) -> e.Review | None: ...
    @abstractmethod
    def list_for_user(self, user_id: int) -> list[e.Review]: ...
    @abstractmethod
    def list_for_property(self, property_id: int) -> list[e.Review]: ...


class ConversationRepository(Repository[e.Conversation]):
    @abstractmethod
    def get_by_private_key(self, key: str) -> e.Conversation | None: ...
    @abstractmethod
    def get_by_group(self, group_id: int) -> e.Conversation | None: ...
    @abstractmethod
    def list_for_user(self, user_id: int) -> list[e.Conversation]: ...


class ConversationMemberRepository(Repository[e.ConversationMember]):
    @abstractmethod
    def list_for_conversation(self, conversation_id: int) -> list[e.ConversationMember]: ...
    @abstractmethod
    def find(self, conversation_id: int, user_id: int) -> e.ConversationMember | None: ...


class MessageRepository(Repository[e.Message]):
    @abstractmethod
    def list_for_conversation(self, conversation_id: int, before_id: int | None, limit: int) -> list[e.Message]: ...
    @abstractmethod
    def last_message(self, conversation_id: int) -> e.Message | None: ...
    @abstractmethod
    def unread_count(self, conversation_id: int, user_id: int, since: datetime | None) -> int: ...


class MessageAttachmentRepository(Repository[e.MessageAttachment]):
    @abstractmethod
    def list_for_messages(self, ids: list[int]) -> dict[int, list[e.MessageAttachment]]: ...


class NotificationRepository(Repository[e.Notification]):
    @abstractmethod
    def list_for_user(self, user_id: int, unread_only: bool, limit: int) -> list[e.Notification]: ...
    @abstractmethod
    def mark_all_read(self, user_id: int) -> None: ...
    @abstractmethod
    def unread_count(self, user_id: int) -> int: ...


class StatsRepository:
    @abstractmethod
    def global_stats(self) -> dict[str, int]: ...
