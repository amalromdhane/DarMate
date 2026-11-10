from fastapi import APIRouter, Depends, Query, Response

from app.application.dto.dto import Actor
from app.application.use_cases import admin as uc
from app.domain.entities.enums import UserStatus
from app.presentation.dependencies.security import provide, require_admin
from app.presentation.schemas import admin as s
from app.presentation.schemas.common import PageOut

router = APIRouter(prefix="/admin", tags=["Administration"], dependencies=[Depends(require_admin)])


@router.get("/users", response_model=PageOut[s.AdminUserOut])
def users(q: str | None = Query(None, max_length=100), status: UserStatus | None = None, page: int = Query(1, ge=1),
          size: int = Query(20, ge=1, le=100), actor: Actor = Depends(require_admin), usecase: uc.AdminUsers = Depends(provide(uc.AdminUsers))):
    p = usecase.list(actor, q, status, page, size)
    return PageOut(items=[s.AdminUserOut(id=u.id, email=u.email, status=u.status, roles=r,
                                         created_at=u.created_at.isoformat() if u.created_at else None) for u, r in p.items],
                   total=p.total, page=p.page, size=p.size)


@router.patch("/users/{user_id}/status", response_model=s.AdminUserOut)
def set_status(user_id: int, body: s.UserStatusIn, actor: Actor = Depends(require_admin), usecase: uc.AdminUsers = Depends(provide(uc.AdminUsers))):
    u = usecase.set_status(actor, user_id, body.status)
    return s.AdminUserOut(id=u.id, email=u.email, status=u.status, roles=usecase.users.get_roles(u.id))


@router.get("/stats")
def stats(actor: Actor = Depends(require_admin), usecase: uc.AdminStats = Depends(provide(uc.AdminStats))):
    return usecase.execute(actor)


@router.get("/settings")
def get_settings(actor: Actor = Depends(require_admin), usecase: uc.AppSettings = Depends(provide(uc.AppSettings))):
    return usecase.get(actor)


@router.put("/settings")
def put_settings(body: dict[str, str], actor: Actor = Depends(require_admin), usecase: uc.AppSettings = Depends(provide(uc.AppSettings))):
    return usecase.update(actor, body)


@router.post("/regions", response_model=s.RegionOut, status_code=201)
def create_region(body: s.NameIn, actor: Actor = Depends(require_admin), ref: uc.ReferenceData = Depends(provide(uc.ReferenceData))):
    return ref.create_region(actor, body.name)


@router.put("/regions/{id}", response_model=s.RegionOut)
def update_region(id: int, body: s.NameIn, actor: Actor = Depends(require_admin), ref: uc.ReferenceData = Depends(provide(uc.ReferenceData))):
    return ref.update_region(actor, id, body.name)


@router.delete("/regions/{id}", status_code=204)
def delete_region(id: int, actor: Actor = Depends(require_admin), ref: uc.ReferenceData = Depends(provide(uc.ReferenceData))):
    ref.delete_region(actor, id)
    return Response(status_code=204)


@router.post("/cities", response_model=s.CityOut, status_code=201)
def create_city(body: s.CityIn, actor: Actor = Depends(require_admin), ref: uc.ReferenceData = Depends(provide(uc.ReferenceData))):
    return ref.create_city(actor, body.region_id, body.name)


@router.put("/cities/{id}", response_model=s.CityOut)
def update_city(id: int, body: s.CityUpdateIn, actor: Actor = Depends(require_admin), ref: uc.ReferenceData = Depends(provide(uc.ReferenceData))):
    return ref.update_city(actor, id, body.name, body.region_id)


@router.delete("/cities/{id}", status_code=204)
def delete_city(id: int, actor: Actor = Depends(require_admin), ref: uc.ReferenceData = Depends(provide(uc.ReferenceData))):
    ref.delete_city(actor, id)
    return Response(status_code=204)


@router.post("/categories", response_model=s.CategoryOut, status_code=201)
def create_category(body: s.NameIn, actor: Actor = Depends(require_admin), ref: uc.ReferenceData = Depends(provide(uc.ReferenceData))):
    return ref.create_category(actor, body.name)


@router.put("/categories/{id}", response_model=s.CategoryOut)
def update_category(id: int, body: s.NameIn, actor: Actor = Depends(require_admin), ref: uc.ReferenceData = Depends(provide(uc.ReferenceData))):
    return ref.update_category(actor, id, body.name)


@router.delete("/categories/{id}", status_code=204)
def delete_category(id: int, actor: Actor = Depends(require_admin), ref: uc.ReferenceData = Depends(provide(uc.ReferenceData))):
    ref.delete_category(actor, id)
    return Response(status_code=204)
