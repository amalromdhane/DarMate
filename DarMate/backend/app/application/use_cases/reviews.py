from app.application.dto.dto import Actor, ReviewSummary
from app.application.interfaces.services import UnitOfWork
from app.application.use_cases.common import AuditService, NotificationService, average
from app.application.use_cases.rentals import RentalAccess
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationFailedError
from app.domain.entities import entities as e
from app.domain.entities.enums import NotificationType, RentalStatus, ReviewTarget
from app.domain.repositories import ports


class CreateReview:
    def __init__(self, access: RentalAccess, requests: ports.RentalRequestRepository, reviews: ports.ReviewRepository,
                 notifications: NotificationService, audit: AuditService, uow: UnitOfWork) -> None:
        self.access, self.requests, self.reviews, self.notifications, self.audit, self.uow = access, requests, reviews, notifications, audit, uow

    def execute(self, actor: Actor, rental_request_id: int, target: ReviewTarget, rating: int,
                comment: str | None, reviewee_id: int | None = None) -> e.Review:
        req, prop, is_owner, is_participant = self.access.load(actor, rental_request_id)
        if req.status != RentalStatus.CONFIRMED:  # pas d'avis sans location confirmée
            raise ConflictError("Vous pourrez donner un avis une fois la location confirmée.")
        if not 1 <= rating <= 5:
            raise ValidationFailedError("La note doit être comprise entre 1 et 5.")
        participants = self.requests.participant_ids(req)
        if is_owner:
            if target != ReviewTarget.TENANT:
                raise ForbiddenError("Un propriétaire ne peut évaluer que ses locataires.")
            reviewee = reviewee_id or (participants[0] if len(participants) == 1 else None)
            if reviewee not in participants:
                raise ValidationFailedError("Indiquez le locataire évalué.")
        else:
            if actor.id not in participants:
                raise ForbiddenError("Seuls les locataires de cette location peuvent évaluer le propriétaire ou le logement.")
            if target == ReviewTarget.TENANT:
                raise ForbiddenError("Vous ne pouvez évaluer que le propriétaire ou le logement.")
            reviewee = prop.owner_id
        if self.reviews.find(rental_request_id, actor.id, target) and not (is_owner and len(participants) > 1):
            raise ConflictError("Vous avez déjà laissé cet avis.")
        if is_owner and any(r for r in [self.reviews.find(rental_request_id, actor.id, target)] if r and r.reviewee_id == reviewee):
            raise ConflictError("Vous avez déjà évalué ce locataire.")
        review = self.reviews.add(e.Review(rental_request_id=rental_request_id, reviewer_id=actor.id, reviewee_id=reviewee,
                                           property_id=prop.id, target_type=target, rating=rating, comment=comment))
        self.notifications.notify(reviewee, NotificationType.RENTAL_RESPONSE, "Vous avez reçu un nouvel avis",
                                  f"Note : {rating}/5", f"/users/{reviewee}")
        self.audit.log(actor.id, "review.create", "review", review.id)
        self.uow.commit()
        return review


class ListReviews:
    def __init__(self, reviews: ports.ReviewRepository) -> None:
        self.reviews = reviews

    def for_user(self, user_id: int) -> ReviewSummary:
        items = self.reviews.list_for_user(user_id)
        return ReviewSummary(items, average([r.rating for r in items]), len(items))

    def for_property(self, property_id: int) -> ReviewSummary:
        items = self.reviews.list_for_property(property_id)
        return ReviewSummary(items, average([r.rating for r in items]), len(items))
