# from fastapi import APIRouter, Depends, Query

# from app.application.dto.dto import Actor
# from app.application.use_cases import rentals as uc
# from app.domain.entities.enums import RentalStatus
# from app.presentation import mappers
# from app.presentation.dependencies.security import get_current_actor, provide
# from app.presentation.schemas import social as s

# router = APIRouter(prefix="/rental-requests", tags=["Demandes de location"])


# @router.post("", response_model=s.RentalRequestOut, status_code=201)
# def create(body: s.RentalRequestIn, actor: Actor = Depends(get_current_actor),
#            usecase: uc.CreateRentalRequest = Depends(provide(uc.CreateRentalRequest)),
#            views: uc.RentalViews = Depends(provide(uc.RentalViews))):
#     req = usecase.execute(actor, body.property_id, body.message, body.desired_move_in, body.group_id)
#     return mappers.rental_out(views.build([req])[0])


# @router.get("", response_model=list[s.RentalRequestOut])
# def list_requests(box: str = Query("sent", pattern="^(sent|received)$"), status: RentalStatus | None = None,
#                   actor: Actor = Depends(get_current_actor), usecase: uc.ListRentalRequests = Depends(provide(uc.ListRentalRequests))):
#     return [mappers.rental_out(v) for v in usecase.execute(actor, box, status)]


# @router.get("/{request_id}", response_model=s.RentalRequestOut)
# def get(request_id: int, actor: Actor = Depends(get_current_actor), usecase: uc.GetRentalRequest = Depends(provide(uc.GetRentalRequest))):
#     return mappers.rental_out(usecase.execute(actor, request_id))


# @router.patch("/{request_id}/status", response_model=s.RentalRequestOut)
# def update_status(request_id: int, body: s.RentalStatusIn, actor: Actor = Depends(get_current_actor),
#                   usecase: uc.UpdateRentalStatus = Depends(provide(uc.UpdateRentalStatus)),
#                   views: uc.RentalViews = Depends(provide(uc.RentalViews))):
#     return mappers.rental_out(views.build([usecase.execute(actor, request_id, body.status)])[0])


# @router.post("/{request_id}/confirm", response_model=s.RentalRequestOut)
# def confirm(request_id: int, actor: Actor = Depends(get_current_actor), usecase: uc.ConfirmRental = Depends(provide(uc.ConfirmRental)),
#             views: uc.RentalViews = Depends(provide(uc.RentalViews))):
#     return mappers.rental_out(views.build([usecase.execute(actor, request_id)])[0])


from fastapi import APIRouter, Depends, Query

from app.application.dto.dto import Actor
from app.application.use_cases import rentals as uc
from app.core.exceptions import ForbiddenError
from app.domain.entities.enums import RentalStatus
from app.presentation import mappers
from app.presentation.dependencies.security import get_current_actor, provide, require_seeker
from app.presentation.schemas import social as s

router = APIRouter(prefix="/rental-requests", tags=["Demandes de location"])


# Seul un CHERCHEUR crée une demande
@router.post("", response_model=s.RentalRequestOut, status_code=201, dependencies=[Depends(require_seeker)])
def create(body: s.RentalRequestIn, actor: Actor = Depends(get_current_actor),
           usecase: uc.CreateRentalRequest = Depends(provide(uc.CreateRentalRequest)),
           views: uc.RentalViews = Depends(provide(uc.RentalViews))):
    req = usecase.execute(actor, body.property_id, body.message, body.desired_move_in, body.group_id)
    return mappers.rental_out(views.build([req])[0])


@router.get("", response_model=list[s.RentalRequestOut])
def list_requests(box: str = Query("sent", pattern="^(sent|received)$"), status: RentalStatus | None = None,
                  actor: Actor = Depends(get_current_actor), usecase: uc.ListRentalRequests = Depends(provide(uc.ListRentalRequests))):
    # chaque rôle ne voit que sa boîte : le chercheur ses demandes envoyées, le propriétaire celles reçues
    if box == "received" and not actor.is_owner:
        raise ForbiddenError("Les demandes reçues sont réservées aux propriétaires.")
    if box == "sent" and "SEEKER" not in actor.roles:
        raise ForbiddenError("Les demandes envoyées sont réservées aux chercheurs.")
    return [mappers.rental_out(v) for v in usecase.execute(actor, box, status)]


@router.get("/{request_id}", response_model=s.RentalRequestOut)
def get(request_id: int, actor: Actor = Depends(get_current_actor), usecase: uc.GetRentalRequest = Depends(provide(uc.GetRentalRequest))):
    return mappers.rental_out(usecase.execute(actor, request_id))


# Accepter / refuser (propriétaire) ou annuler (chercheur) : les règles sont vérifiées dans le use case
@router.patch("/{request_id}/status", response_model=s.RentalRequestOut)
def update_status(request_id: int, body: s.RentalStatusIn, actor: Actor = Depends(get_current_actor),
                  usecase: uc.UpdateRentalStatus = Depends(provide(uc.UpdateRentalStatus)),
                  views: uc.RentalViews = Depends(provide(uc.RentalViews))):
    return mappers.rental_out(views.build([usecase.execute(actor, request_id, body.status)])[0])


@router.post("/{request_id}/confirm", response_model=s.RentalRequestOut)
def confirm(request_id: int, actor: Actor = Depends(get_current_actor), usecase: uc.ConfirmRental = Depends(provide(uc.ConfirmRental)),
            views: uc.RentalViews = Depends(provide(uc.RentalViews))):
    return mappers.rental_out(views.build([usecase.execute(actor, request_id)])[0])