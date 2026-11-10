from datetime import date, datetime

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.entities.enums import RentalStatus, ReviewTarget, VisitStatus
from app.infrastructure.database.base import PK, Base, created, pk


class RentalRequestModel(Base):
    __tablename__ = "rental_request"
    __table_args__ = (
        CheckConstraint("(applicant_user_id IS NOT NULL) <> (group_id IS NOT NULL)", name="ck_rental_single_applicant"),
    )
    id: Mapped[int] = pk()
    property_id: Mapped[int] = mapped_column(PK, ForeignKey("property.id", ondelete="RESTRICT"), index=True)
    created_by_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="RESTRICT"))
    applicant_user_id: Mapped[int | None] = mapped_column(PK, ForeignKey("user.id", ondelete="RESTRICT"), index=True)
    group_id: Mapped[int | None] = mapped_column(PK, ForeignKey("roommate_group.id", ondelete="RESTRICT"), index=True)
    message: Mapped[str | None] = mapped_column(Text)
    desired_move_in: Mapped[date | None] = mapped_column(Date)
    status: Mapped[RentalStatus] = mapped_column(Enum(RentalStatus, native_enum=False, length=20), default=RentalStatus.PENDING)
    created_at: Mapped[datetime] = created()
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class VisitModel(Base):
    __tablename__ = "visit"
    id: Mapped[int] = pk()
    property_id: Mapped[int] = mapped_column(PK, ForeignKey("property.id", ondelete="CASCADE"), index=True)
    requester_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="CASCADE"), index=True)
    rental_request_id: Mapped[int | None] = mapped_column(PK, ForeignKey("rental_request.id", ondelete="SET NULL"))
    status: Mapped[VisitStatus] = mapped_column(Enum(VisitStatus, native_enum=False, length=20), default=VisitStatus.PROPOSED)
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = created()


class VisitSlotModel(Base):
    __tablename__ = "visit_slot"
    id: Mapped[int] = pk()
    visit_id: Mapped[int] = mapped_column(PK, ForeignKey("visit.id", ondelete="CASCADE"), index=True)
    proposed_by_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="CASCADE"))
    starts_at: Mapped[datetime] = mapped_column(DateTime)
    ends_at: Mapped[datetime] = mapped_column(DateTime)
    is_selected: Mapped[bool] = mapped_column(Boolean, default=False)


class ReviewModel(Base):
    __tablename__ = "review"
    __table_args__ = (
        UniqueConstraint("rental_request_id", "reviewer_id", "target_type", "reviewee_id"),
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_review_rating"),
    )
    id: Mapped[int] = pk()
    rental_request_id: Mapped[int] = mapped_column(PK, ForeignKey("rental_request.id", ondelete="CASCADE"))
    reviewer_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="CASCADE"))
    reviewee_id: Mapped[int] = mapped_column(PK, ForeignKey("user.id", ondelete="CASCADE"), index=True)
    property_id: Mapped[int] = mapped_column(PK, ForeignKey("property.id", ondelete="CASCADE"), index=True)
    target_type: Mapped[ReviewTarget] = mapped_column(Enum(ReviewTarget, native_enum=False, length=20))
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = created()
