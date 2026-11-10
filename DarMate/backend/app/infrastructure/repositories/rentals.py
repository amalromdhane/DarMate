from sqlalchemy import or_, select, update

from app.domain.entities import entities as e
from app.domain.entities.enums import RentalStatus
from app.domain.repositories import ports
from app.infrastructure.models.property import PropertyModel
from app.infrastructure.models.rental import RentalRequestModel, ReviewModel, VisitModel, VisitSlotModel
from app.infrastructure.models.roommate import GroupMemberModel
from app.infrastructure.repositories.base import SqlRepository

_OPEN = (RentalStatus.PENDING, RentalStatus.ACCEPTED)


class SqlRentalRequestRepository(SqlRepository[e.RentalRequest], ports.RentalRequestRepository):
    model, entity = RentalRequestModel, e.RentalRequest

    def list_sent(self, user_id):
        group_ids = select(GroupMemberModel.group_id).where(GroupMemberModel.user_id == user_id)
        stmt = select(RentalRequestModel).where(or_(
            RentalRequestModel.applicant_user_id == user_id, RentalRequestModel.created_by_id == user_id,
            RentalRequestModel.group_id.in_(group_ids))).order_by(RentalRequestModel.id.desc())
        return self._all(stmt)

    def list_received(self, owner_id, status):
        stmt = (select(RentalRequestModel).join(PropertyModel, PropertyModel.id == RentalRequestModel.property_id)
                .where(PropertyModel.owner_id == owner_id).order_by(RentalRequestModel.id.desc()))
        if status:
            stmt = stmt.where(RentalRequestModel.status == status)
        return self._all(stmt)

    def find_open(self, property_id, applicant_user_id, group_id):
        stmt = select(RentalRequestModel).where(
            RentalRequestModel.property_id == property_id, RentalRequestModel.status.in_(_OPEN))
        if group_id:
            stmt = stmt.where(RentalRequestModel.group_id == group_id)
        else:
            stmt = stmt.where(RentalRequestModel.applicant_user_id == applicant_user_id)
        return self._first(stmt)

    def participant_ids(self, request):
        if request.applicant_user_id:
            return [request.applicant_user_id]
        stmt = select(GroupMemberModel.user_id).where(GroupMemberModel.group_id == request.group_id)
        return list(self.s.execute(stmt).scalars().all())

    def reject_other_pending(self, property_id, except_id):
        stmt = select(RentalRequestModel).where(
            RentalRequestModel.property_id == property_id, RentalRequestModel.id != except_id,
            RentalRequestModel.status.in_(_OPEN))
        objs = self.s.execute(stmt).scalars().all()
        for o in objs:
            o.status = RentalStatus.REJECTED
        self.s.flush()
        return self._many(objs)


class SqlVisitRepository(SqlRepository[e.Visit], ports.VisitRepository):
    model, entity = VisitModel, e.Visit

    def list_for_user(self, user_id):
        owned = select(PropertyModel.id).where(PropertyModel.owner_id == user_id)
        stmt = select(VisitModel).where(or_(VisitModel.requester_id == user_id, VisitModel.property_id.in_(owned))
                                        ).order_by(VisitModel.id.desc())
        return self._all(stmt)


class SqlVisitSlotRepository(SqlRepository[e.VisitSlot], ports.VisitSlotRepository):
    model, entity = VisitSlotModel, e.VisitSlot

    def list_for_visit(self, visit_id):
        return self._all(select(VisitSlotModel).where(VisitSlotModel.visit_id == visit_id).order_by(VisitSlotModel.starts_at))

    def list_for_visits(self, ids):
        out: dict[int, list[e.VisitSlot]] = {i: [] for i in ids}
        if ids:
            for s in self._all(select(VisitSlotModel).where(VisitSlotModel.visit_id.in_(ids)).order_by(VisitSlotModel.starts_at)):
                out[s.visit_id].append(s)
        return out


class SqlReviewRepository(SqlRepository[e.Review], ports.ReviewRepository):
    model, entity = ReviewModel, e.Review

    def find(self, rental_request_id, reviewer_id, target_type):
        return self._first(select(ReviewModel).where(
            ReviewModel.rental_request_id == rental_request_id, ReviewModel.reviewer_id == reviewer_id,
            ReviewModel.target_type == target_type))

    def list_for_user(self, user_id):
        return self._all(select(ReviewModel).where(ReviewModel.reviewee_id == user_id).order_by(ReviewModel.id.desc()))

    def list_for_property(self, property_id):
        from app.domain.entities.enums import ReviewTarget
        return self._all(select(ReviewModel).where(
            ReviewModel.property_id == property_id, ReviewModel.target_type == ReviewTarget.PROPERTY
        ).order_by(ReviewModel.id.desc()))
