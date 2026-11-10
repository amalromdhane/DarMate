from app.application.dto.dto import Actor, RentalRequestView
from app.application.interfaces.services import UnitOfWork
from app.application.use_cases.common import AuditService, NotificationService, UserDirectory
from app.application.use_cases.properties import PropertyAccess
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationFailedError
from app.domain.entities import entities as e
from app.domain.entities.enums import NotificationType, PropertyStatus, RentalStatus
from app.domain.repositories import ports
from app.domain.services.rental_rules import ensure_transition


class RentalAccess:
    def __init__(self, requests: ports.RentalRequestRepository, props: ports.PropertyRepository) -> None:
        self.requests, self.props = requests, props

    def load(self, actor: Actor, request_id: int) -> tuple[e.RentalRequest, e.Property, bool, bool]:
        """Retourne (demande, annonce, est_propriétaire, est_participant) ou 404 si l'acteur n'est pas concerné."""
        req = self.requests.get(request_id)
        if req is None:
            raise NotFoundError("Demande introuvable.")
        prop = self.props.get(req.property_id)
        is_owner = prop.owner_id == actor.id
        is_participant = actor.id == req.created_by_id or actor.id in self.requests.participant_ids(req)
        if not (is_owner or is_participant):
            raise NotFoundError("Demande introuvable.")
        return req, prop, is_owner, is_participant


class CreateRentalRequest:
    def __init__(self, access: PropertyAccess, requests: ports.RentalRequestRepository, groups: ports.GroupRepository,
                 members: ports.GroupMemberRepository, notifications: NotificationService, directory: UserDirectory,
                 audit: AuditService, uow: UnitOfWork) -> None:
        self.access, self.requests, self.groups, self.members = access, requests, groups, members
        self.notifications, self.directory, self.audit, self.uow = notifications, directory, audit, uow

    def execute(self, actor: Actor, property_id: int, message: str | None, desired_move_in, group_id: int | None) -> e.RentalRequest:
        prop = self.access.visible(property_id, actor.id)
        if prop.status != PropertyStatus.AVAILABLE:
            raise ConflictError("Cette annonce n'est plus disponible.")
        if prop.owner_id == actor.id:
            raise ForbiddenError("Vous ne pouvez pas faire une demande pour votre propre annonce.")
        applicant_id: int | None = actor.id
        if group_id:
            if not self.members.find(group_id, actor.id):
                raise NotFoundError("Groupe introuvable.")
            size = len(self.members.list_for_group(group_id))
            if not prop.coliving_allowed:
                raise ConflictError("Le propriétaire n'autorise pas la colocation pour ce logement.")
            if size > prop.max_roommates:
                raise ConflictError(f"Ce logement accepte au maximum {prop.max_roommates} colocataires.")
            applicant_id = None
        if self.requests.find_open(property_id, applicant_id, group_id):
            raise ConflictError("Vous avez déjà une demande en cours pour ce logement.")
        req = self.requests.add(e.RentalRequest(property_id=property_id, created_by_id=actor.id, applicant_user_id=applicant_id,
                                                group_id=group_id, message=message, desired_move_in=desired_move_in))
        self.notifications.notify(prop.owner_id, NotificationType.RENTAL_REQUEST, "Nouvelle demande de location",
                                  f"{self.directory.name_of(actor.id)} souhaite louer « {prop.title} ».", f"/rental-requests/{req.id}")
        self.audit.log(actor.id, "rental.create", "rental_request", req.id)
        self.uow.commit()
        return req


class RentalViews:
    def __init__(self, props: ports.PropertyRepository, groups: ports.GroupRepository, directory: UserDirectory) -> None:
        self.props, self.groups, self.directory = props, groups, directory

    def build(self, reqs: list[e.RentalRequest]) -> list[RentalRequestView]:
        out = []
        for r in reqs:
            prop = self.props.get(r.property_id)
            if r.group_id:
                g = self.groups.get(r.group_id)
                label = f"Groupe « {g.name} »" if g else "Groupe"
            else:
                label = self.directory.name_of(r.applicant_user_id)
            out.append(RentalRequestView(r, prop.title if prop else "", label))
        return out


class ListRentalRequests:
    def __init__(self, requests: ports.RentalRequestRepository, views: RentalViews) -> None:
        self.requests, self.views = requests, views

    def execute(self, actor: Actor, box: str, status: RentalStatus | None) -> list[RentalRequestView]:
        if box == "received":
            rows = self.requests.list_received(actor.id, status)
        elif box == "sent":
            rows = [r for r in self.requests.list_sent(actor.id) if status is None or r.status == status]
        else:
            raise ValidationFailedError("Boîte inconnue (sent ou received).")
        return self.views.build(rows)


class GetRentalRequest:
    def __init__(self, access: RentalAccess, views: RentalViews) -> None:
        self.access, self.views = access, views

    def execute(self, actor: Actor, request_id: int) -> RentalRequestView:
        return self.views.build([self.access.load(actor, request_id)[0]])[0]


class UpdateRentalStatus:
    def __init__(self, access: RentalAccess, requests: ports.RentalRequestRepository, notifications: NotificationService,
                 audit: AuditService, uow: UnitOfWork) -> None:
        self.access, self.requests, self.notifications, self.audit, self.uow = access, requests, notifications, audit, uow

    def execute(self, actor: Actor, request_id: int, status: RentalStatus) -> e.RentalRequest:
        req, prop, is_owner, is_participant = self.access.load(actor, request_id)
        if status in (RentalStatus.ACCEPTED, RentalStatus.REJECTED):
            if not is_owner:
                raise ForbiddenError("Seul le propriétaire peut accepter ou refuser une demande.")
            ensure_transition(req.status, status, as_owner=True)
        elif status == RentalStatus.CANCELLED:
            if not is_participant:
                raise ForbiddenError("Seul le demandeur peut annuler sa demande.")
            ensure_transition(req.status, status, as_owner=False)
        else:
            raise ValidationFailedError("Utilisez l'action de confirmation pour confirmer une location.")
        req.status = status
        self.requests.update(req)
        word = {RentalStatus.ACCEPTED: "acceptée", RentalStatus.REJECTED: "refusée", RentalStatus.CANCELLED: "annulée"}[status]
        targets = [prop.owner_id] if status == RentalStatus.CANCELLED else self.requests.participant_ids(req)
        for uid in targets:
            self.notifications.notify(uid, NotificationType.RENTAL_RESPONSE, f"Demande de location {word}",
                                      f"Demande pour « {prop.title} ».", f"/rental-requests/{req.id}")
        self.audit.log(actor.id, f"rental.{status.value.lower()}", "rental_request", req.id)
        self.uow.commit()
        return req


class ConfirmRental:
    """Confirme la location : demande -> CONFIRMED, logement -> RENTED, autres demandes rejetées (transaction unique)."""

    def __init__(self, access: RentalAccess, requests: ports.RentalRequestRepository, props: ports.PropertyRepository,
                 notifications: NotificationService, audit: AuditService, uow: UnitOfWork) -> None:
        self.access, self.requests, self.props, self.notifications, self.audit, self.uow = access, requests, props, notifications, audit, uow

    def execute(self, actor: Actor, request_id: int) -> e.RentalRequest:
        req, prop, is_owner, _ = self.access.load(actor, request_id)
        if not is_owner:
            raise ForbiddenError("Seul le propriétaire peut confirmer la location.")
        if req.status != RentalStatus.ACCEPTED:
            raise ConflictError("Acceptez d'abord la demande avant de confirmer la location.")
        if prop.status != PropertyStatus.AVAILABLE:
            raise ConflictError("Ce logement n'est plus disponible.")
        try:
            req.status = RentalStatus.CONFIRMED
            self.requests.update(req)
            prop.status = PropertyStatus.RENTED
            self.props.update(prop)
            for other in self.requests.reject_other_pending(prop.id, req.id):
                for uid in self.requests.participant_ids(other):
                    self.notifications.notify(uid, NotificationType.RENTAL_RESPONSE, "Demande de location refusée",
                                              f"« {prop.title} » a été loué.", f"/rental-requests/{other.id}")
            for uid in self.requests.participant_ids(req):
                self.notifications.notify(uid, NotificationType.RENTAL_RESPONSE, "Location confirmée",
                                          f"Votre location de « {prop.title} » est confirmée. Vous pouvez laisser un avis.",
                                          f"/rental-requests/{req.id}")
            self.audit.log(actor.id, "rental.confirm", "rental_request", req.id)
            self.uow.commit()
        except Exception:
            self.uow.rollback()
            raise
        return req
