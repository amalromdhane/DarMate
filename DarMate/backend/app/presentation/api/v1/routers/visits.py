# from datetime import datetime, timezone

# from fastapi import APIRouter, Depends

# from app.application.dto.dto import Actor, SlotCmd
# from app.application.use_cases import visits as uc
# from app.presentation import mappers
# from app.presentation.dependencies.security import get_current_actor, provide
# from app.presentation.schemas import social as s

# router = APIRouter(prefix="/visits", tags=["Visites"])


# def _slots(items: list[s.SlotIn]) -> list[SlotCmd]:
#     return [SlotCmd(_utc(i.starts_at), _utc(i.ends_at)) for i in items]


# def _utc(d: datetime) -> datetime:
#     return d.astimezone(timezone.utc).replace(tzinfo=None) if d.tzinfo else d


# @router.post("", response_model=s.VisitOut, status_code=201)
# def request_visit(body: s.VisitIn, actor: Actor = Depends(get_current_actor), usecase: uc.RequestVisit = Depends(provide(uc.RequestVisit))):
#     return mappers.visit_out(usecase.execute(actor, body.property_id, _slots(body.slots), body.note, body.rental_request_id))


# @router.get("/calendar", response_model=list[s.VisitOut])
# def calendar(start: datetime | None = None, end: datetime | None = None, actor: Actor = Depends(get_current_actor),
#              usecase: uc.VisitCalendar = Depends(provide(uc.VisitCalendar))):
#     return [mappers.visit_out(v) for v in usecase.execute(actor, _utc(start) if start else None, _utc(end) if end else None)]


# @router.post("/{visit_id}/slots", response_model=s.VisitOut)
# def propose_slots(visit_id: int, body: s.SlotsIn, actor: Actor = Depends(get_current_actor), usecase: uc.ProposeSlots = Depends(provide(uc.ProposeSlots))):
#     return mappers.visit_out(usecase.execute(actor, visit_id, _slots(body.slots)))


# @router.patch("/{visit_id}", response_model=s.VisitOut)
# def respond(visit_id: int, body: s.VisitActionIn, actor: Actor = Depends(get_current_actor), usecase: uc.RespondVisit = Depends(provide(uc.RespondVisit))):
#     return mappers.visit_out(usecase.execute(actor, visit_id, body.action, body.slot_id))


from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.application.dto.dto import Actor, SlotCmd
from app.application.use_cases import visits as uc
from app.presentation import mappers
from app.presentation.dependencies.security import get_current_actor, provide, require_seeker
from app.presentation.schemas import social as s

router = APIRouter(prefix="/visits", tags=["Visites"])


def _utc(d: datetime) -> datetime:
    return d.astimezone(timezone.utc).replace(tzinfo=None) if d.tzinfo else d


def _slots(items: list[s.SlotIn]) -> list[SlotCmd]:
    return [SlotCmd(_utc(i.starts_at), _utc(i.ends_at)) for i in items]


# Seul un CHERCHEUR demande une visite
@router.post("", response_model=s.VisitOut, status_code=201, dependencies=[Depends(require_seeker)])
def request_visit(body: s.VisitIn, actor: Actor = Depends(get_current_actor), usecase: uc.RequestVisit = Depends(provide(uc.RequestVisit))):
    return mappers.visit_out(usecase.execute(actor, body.property_id, _slots(body.slots), body.note, body.rental_request_id))


# Calendrier, nouveaux créneaux et réponse : communs aux deux parties de la visite (chercheur et propriétaire)
@router.get("/calendar", response_model=list[s.VisitOut])
def calendar(start: datetime | None = None, end: datetime | None = None, actor: Actor = Depends(get_current_actor),
             usecase: uc.VisitCalendar = Depends(provide(uc.VisitCalendar))):
    return [mappers.visit_out(v) for v in usecase.execute(actor, _utc(start) if start else None, _utc(end) if end else None)]


@router.post("/{visit_id}/slots", response_model=s.VisitOut)
def propose_slots(visit_id: int, body: s.SlotsIn, actor: Actor = Depends(get_current_actor), usecase: uc.ProposeSlots = Depends(provide(uc.ProposeSlots))):
    return mappers.visit_out(usecase.execute(actor, visit_id, _slots(body.slots)))


@router.patch("/{visit_id}", response_model=s.VisitOut)
def respond(visit_id: int, body: s.VisitActionIn, actor: Actor = Depends(get_current_actor), usecase: uc.RespondVisit = Depends(provide(uc.RespondVisit))):
    return mappers.visit_out(usecase.execute(actor, visit_id, body.action, body.slot_id))