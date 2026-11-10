from datetime import datetime

from app.application.dto.dto import Actor, SlotCmd, VisitView
from app.application.interfaces.services import UnitOfWork
from app.application.use_cases.common import NotificationService, UserDirectory
from app.application.use_cases.properties import PropertyAccess
from app.core.clock import utcnow
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationFailedError
from app.domain.entities import entities as e
from app.domain.entities.enums import NotificationType, PropertyStatus, VisitStatus
from app.domain.repositories import ports

MAX_SLOTS = 5


def _validate_slots(slots: list[SlotCmd]) -> None:
    if not slots or len(slots) > MAX_SLOTS:
        raise ValidationFailedError(f"Proposez entre 1 et {MAX_SLOTS} créneaux.")
    now = utcnow()
    for s in slots:
        if s.starts_at <= now or s.ends_at <= s.starts_at:
            raise ValidationFailedError("Chaque créneau doit être dans le futur et se terminer après son début.")


class VisitAccess:
    def __init__(self, visits: ports.VisitRepository, props: ports.PropertyRepository) -> None:
        self.visits, self.props = visits, props

    def load(self, actor: Actor, visit_id: int) -> tuple[e.Visit, e.Property, int]:
        """Retourne (visite, annonce, id de l'autre partie). 404 si l'acteur n'est pas concerné."""
        visit = self.visits.get(visit_id)
        if visit is None:
            raise NotFoundError("Visite introuvable.")
        prop = self.props.get(visit.property_id)
        if actor.id == visit.requester_id:
            return visit, prop, prop.owner_id
        if actor.id == prop.owner_id:
            return visit, prop, visit.requester_id
        raise NotFoundError("Visite introuvable.")


class RequestVisit:
    def __init__(self, access: PropertyAccess, visits: ports.VisitRepository, slots: ports.VisitSlotRepository,
                 requests: ports.RentalRequestRepository, notifications: NotificationService,
                 directory: UserDirectory, uow: UnitOfWork) -> None:
        self.access, self.visits, self.slots, self.requests = access, visits, slots, requests
        self.notifications, self.directory, self.uow = notifications, directory, uow

    def execute(self, actor: Actor, property_id: int, slots: list[SlotCmd], note: str | None,
                rental_request_id: int | None = None) -> VisitView:
        prop = self.access.visible(property_id, actor.id)
        if prop.owner_id == actor.id:
            raise ForbiddenError("Vous ne pouvez pas visiter votre propre logement.")
        if prop.status != PropertyStatus.AVAILABLE:
            raise ConflictError("Ce logement n'est plus disponible.")
        _validate_slots(slots)
        if rental_request_id:
            rr = self.requests.get(rental_request_id)
            if rr is None or rr.property_id != property_id or actor.id not in (rr.created_by_id, *self.requests.participant_ids(rr)):
                raise NotFoundError("Demande de location introuvable.")
        visit = self.visits.add(e.Visit(property_id=property_id, requester_id=actor.id, rental_request_id=rental_request_id, note=note))
        created = [self.slots.add(e.VisitSlot(visit_id=visit.id, proposed_by_id=actor.id, starts_at=s.starts_at, ends_at=s.ends_at)) for s in slots]
        self.notifications.notify(prop.owner_id, NotificationType.VISIT, "Nouvelle demande de visite",
                                  f"{self.directory.name_of(actor.id)} souhaite visiter « {prop.title} ».", "/visits")
        self.uow.commit()
        return VisitView(visit, prop.title, created)


class ProposeSlots:
    """Proposer de nouveaux créneaux (aussi utilisé pour modifier une visite déjà acceptée)."""

    def __init__(self, access: VisitAccess, visits: ports.VisitRepository, slots: ports.VisitSlotRepository,
                 notifications: NotificationService, uow: UnitOfWork) -> None:
        self.access, self.visits, self.slots, self.notifications, self.uow = access, visits, slots, notifications, uow

    def execute(self, actor: Actor, visit_id: int, new_slots: list[SlotCmd]) -> VisitView:
        visit, prop, other_id = self.access.load(actor, visit_id)
        if visit.status in (VisitStatus.CANCELLED, VisitStatus.REJECTED):
            raise ConflictError("Cette visite est terminée.")
        _validate_slots(new_slots)
        existing = self.slots.list_for_visit(visit_id)
        if len(existing) + len(new_slots) > MAX_SLOTS * 3:
            raise ConflictError("Trop de créneaux proposés pour cette visite.")
        if visit.status == VisitStatus.ACCEPTED:  # modification : on repart en négociation
            for s in existing:
                if s.is_selected:
                    s.is_selected = False
                    self.slots.update(s)
            visit.status = VisitStatus.PROPOSED
            self.visits.update(visit)
        for s in new_slots:
            self.slots.add(e.VisitSlot(visit_id=visit_id, proposed_by_id=actor.id, starts_at=s.starts_at, ends_at=s.ends_at))
        self.notifications.notify(other_id, NotificationType.VISIT, "Nouveaux créneaux de visite proposés", prop.title, "/visits")
        self.uow.commit()
        return VisitView(visit, prop.title, self.slots.list_for_visit(visit_id))


class RespondVisit:
    def __init__(self, access: VisitAccess, visits: ports.VisitRepository, slots: ports.VisitSlotRepository,
                 notifications: NotificationService, uow: UnitOfWork) -> None:
        self.access, self.visits, self.slots, self.notifications, self.uow = access, visits, slots, notifications, uow

    def execute(self, actor: Actor, visit_id: int, action: str, slot_id: int | None = None) -> VisitView:
        visit, prop, other_id = self.access.load(actor, visit_id)
        if visit.status in (VisitStatus.CANCELLED, VisitStatus.REJECTED):
            raise ConflictError("Cette visite est terminée.")
        if action == "accept":
            slot = self.slots.get(slot_id) if slot_id else None
            if slot is None or slot.visit_id != visit_id:
                raise ValidationFailedError("Choisissez un créneau de cette visite.")
            if slot.proposed_by_id == actor.id:
                raise ForbiddenError("Vous ne pouvez pas accepter votre propre créneau : l'autre partie doit le faire.")
            if slot.starts_at <= utcnow():
                raise ValidationFailedError("Ce créneau est déjà passé.")
            for s in self.slots.list_for_visit(visit_id):
                s.is_selected = s.id == slot.id
                self.slots.update(s)
            visit.status, title = VisitStatus.ACCEPTED, "Visite confirmée"
        elif action == "reject":
            visit.status, title = VisitStatus.REJECTED, "Visite refusée"
        elif action == "cancel":
            visit.status, title = VisitStatus.CANCELLED, "Visite annulée"
        else:
            raise ValidationFailedError("Action inconnue (accept, reject, cancel).")
        self.visits.update(visit)
        self.notifications.notify(other_id, NotificationType.VISIT, title, prop.title, "/visits")
        self.uow.commit()
        return VisitView(visit, prop.title, self.slots.list_for_visit(visit_id))


class VisitCalendar:
    def __init__(self, visits: ports.VisitRepository, slots: ports.VisitSlotRepository, props: ports.PropertyRepository) -> None:
        self.visits, self.slots, self.props = visits, slots, props

    def execute(self, actor: Actor, start: datetime | None = None, end: datetime | None = None) -> list[VisitView]:
        visits = [v for v in self.visits.list_for_user(actor.id) if v.status in (VisitStatus.PROPOSED, VisitStatus.ACCEPTED)]
        slot_map = self.slots.list_for_visits([v.id for v in visits])
        out = []
        for v in visits:
            slots = slot_map[v.id]
            ref = [s for s in slots if s.is_selected] or slots
            if start and all(s.ends_at < start for s in ref):
                continue
            if end and all(s.starts_at > end for s in ref):
                continue
            out.append(VisitView(v, self.props.get(v.property_id).title, slots))
        return out
