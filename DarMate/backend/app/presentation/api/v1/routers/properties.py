# from decimal import Decimal

# from fastapi import APIRouter, Depends, Query, Response

# from app.application.dto.dto import Actor, CreatePropertyCmd
# from app.application.use_cases import properties as uc
# from app.application.use_cases.reviews import ListReviews
# from app.domain.entities.enums import PropertyStatus
# from app.domain.repositories.ports import PropertySearchCriteria
# from app.presentation import mappers
# from app.presentation.dependencies.security import get_current_actor, get_optional_actor, provide, read_upload
# from app.presentation.schemas import properties as s
# from app.presentation.schemas.common import Message, PageOut
# from app.presentation.schemas.social import ReviewListOut, ReviewOut

# router = APIRouter(tags=["Logements"])


# def criteria(city_id: int | None = None, category_id: int | None = None, min_price: Decimal | None = Query(None, ge=0),
#              max_price: Decimal | None = Query(None, ge=0), min_rooms: int | None = Query(None, ge=1),
#              coliving: bool | None = None, q: str | None = Query(None, max_length=100),
#              sort: str = Query("recent", pattern="^(recent|price_asc|price_desc)$")) -> PropertySearchCriteria:
#     return PropertySearchCriteria(city_id=city_id, category_id=category_id, min_price=min_price, max_price=max_price,
#                                   min_rooms=min_rooms, coliving=coliving, text=q, sort=sort)


# @router.get("/properties", response_model=PageOut[s.PropertyCardOut])
# def search(c: PropertySearchCriteria = Depends(criteria), page: int = Query(1, ge=1), size: int = Query(12, ge=1, le=50),
#            actor: Actor | None = Depends(get_optional_actor), usecase: uc.SearchProperties = Depends(provide(uc.SearchProperties))):
#     p = usecase.execute(c, page, size, actor.id if actor else None)
#     return PageOut(items=[mappers.card_out(i) for i in p.items], total=p.total, page=p.page, size=p.size)


# @router.get("/properties/map", response_model=list[s.PropertyCardOut])
# def map_view(c: PropertySearchCriteria = Depends(criteria), usecase: uc.MapProperties = Depends(provide(uc.MapProperties))):
#     return [mappers.card_out(i) for i in usecase.execute(c)]


# @router.get("/properties/mine", response_model=PageOut[s.PropertyCardOut])
# def mine(status: PropertyStatus | None = None, page: int = Query(1, ge=1), size: int = Query(12, ge=1, le=50),
#          actor: Actor = Depends(get_current_actor), usecase: uc.ListMyProperties = Depends(provide(uc.ListMyProperties))):
#     p = usecase.execute(actor, status, page, size)
#     return PageOut(items=[mappers.card_out(i) for i in p.items], total=p.total, page=p.page, size=p.size)


# @router.post("/properties", response_model=s.PropertyOut, status_code=201)
# def create(body: s.PropertyIn, actor: Actor = Depends(get_current_actor), usecase: uc.CreateProperty = Depends(provide(uc.CreateProperty))):
#     return usecase.execute(actor, CreatePropertyCmd(**body.model_dump()))


# @router.get("/properties/{property_id}", response_model=s.PropertyDetailOut)
# def detail(property_id: int, actor: Actor | None = Depends(get_optional_actor), usecase: uc.GetProperty = Depends(provide(uc.GetProperty))):
#     return mappers.detail_out(usecase.execute(property_id, actor.id if actor else None))


# @router.put("/properties/{property_id}", response_model=s.PropertyOut)
# def update(property_id: int, body: s.PropertyUpdateIn, actor: Actor = Depends(get_current_actor),
#            usecase: uc.UpdateProperty = Depends(provide(uc.UpdateProperty))):
#     return usecase.execute(actor, property_id, body.model_dump(exclude_unset=True))


# @router.patch("/properties/{property_id}/status", response_model=s.PropertyOut)
# def set_status(property_id: int, body: s.StatusIn, actor: Actor = Depends(get_current_actor),
#                usecase: uc.SetPropertyStatus = Depends(provide(uc.SetPropertyStatus))):
#     return usecase.execute(actor, property_id, body.status)


# @router.delete("/properties/{property_id}", status_code=204)
# def delete(property_id: int, actor: Actor = Depends(get_current_actor), usecase: uc.DeleteProperty = Depends(provide(uc.DeleteProperty))):
#     usecase.execute(actor, property_id)
#     return Response(status_code=204)


# @router.post("/properties/{property_id}/images", response_model=s.ImageOut, status_code=201)
# async def add_image(property_id: int, file=Depends(read_upload), actor: Actor = Depends(get_current_actor),
#                     usecase: uc.AddPropertyImage = Depends(provide(uc.AddPropertyImage))):
#     return usecase.execute(actor, property_id, file)


# @router.delete("/properties/{property_id}/images/{image_id}", status_code=204)
# def delete_image(property_id: int, image_id: int, actor: Actor = Depends(get_current_actor),
#                  usecase: uc.DeletePropertyImage = Depends(provide(uc.DeletePropertyImage))):
#     usecase.execute(actor, property_id, image_id)
#     return Response(status_code=204)


# @router.get("/properties/{property_id}/stats")
# def stats(property_id: int, actor: Actor = Depends(get_current_actor), usecase: uc.PropertyStats = Depends(provide(uc.PropertyStats))):
#     return usecase.execute(actor, property_id)


# @router.get("/properties/{property_id}/reviews", response_model=ReviewListOut)
# def reviews(property_id: int, usecase: ListReviews = Depends(provide(ListReviews))):
#     r = usecase.for_property(property_id)
#     return ReviewListOut(items=[ReviewOut.model_validate(i) for i in r.items], average=r.average, count=r.count)


# # ---- Favoris ----
# @router.get("/favorites", response_model=list[s.PropertyCardOut], tags=["Favoris"])
# def list_favorites(actor: Actor = Depends(get_current_actor), usecase: uc.ListFavorites = Depends(provide(uc.ListFavorites))):
#     return [mappers.card_out(i) for i in usecase.execute(actor)]


# @router.put("/favorites/{property_id}", response_model=Message, tags=["Favoris"])
# def add_favorite(property_id: int, actor: Actor = Depends(get_current_actor), usecase: uc.ToggleFavorite = Depends(provide(uc.ToggleFavorite))):
#     usecase.execute(actor, property_id, True)
#     return Message(detail="Ajouté aux favoris.")


# @router.delete("/favorites/{property_id}", response_model=Message, tags=["Favoris"])
# def remove_favorite(property_id: int, actor: Actor = Depends(get_current_actor), usecase: uc.ToggleFavorite = Depends(provide(uc.ToggleFavorite))):
#     usecase.execute(actor, property_id, False)
#     return Message(detail="Retiré des favoris.")


# # ---- Recherches enregistrées & alertes ----
# @router.get("/saved-searches", response_model=list[s.SavedSearchOut], tags=["Recherches enregistrées"])
# def list_searches(actor: Actor = Depends(get_current_actor), usecase: uc.SavedSearches = Depends(provide(uc.SavedSearches))):
#     return [s.SavedSearchOut(id=x.id, name=x.name, filters=x.filters, alert_active=a) for x, a in usecase.list(actor)]


# @router.post("/saved-searches", response_model=s.SavedSearchOut, status_code=201, tags=["Recherches enregistrées"])
# def create_search(body: s.SavedSearchIn, actor: Actor = Depends(get_current_actor), usecase: uc.SavedSearches = Depends(provide(uc.SavedSearches))):
#     saved, alert = usecase.create(actor, body.name, body.filters, body.alert)
#     return s.SavedSearchOut(id=saved.id, name=saved.name, filters=saved.filters, alert_active=alert)


# @router.delete("/saved-searches/{search_id}", status_code=204, tags=["Recherches enregistrées"])
# def delete_search(search_id: int, actor: Actor = Depends(get_current_actor), usecase: uc.SavedSearches = Depends(provide(uc.SavedSearches))):
#     usecase.delete(actor, search_id)
#     return Response(status_code=204)


# @router.put("/saved-searches/{search_id}/alert", response_model=Message, tags=["Recherches enregistrées"])
# def set_alert(search_id: int, body: s.AlertIn, actor: Actor = Depends(get_current_actor), usecase: uc.SavedSearches = Depends(provide(uc.SavedSearches))):
#     usecase.set_alert(actor, search_id, body.active)
#     return Message(detail="Alerte mise à jour.")


from decimal import Decimal

from fastapi import APIRouter, Depends, Query, Response

from app.application.dto.dto import Actor, CreatePropertyCmd
from app.application.use_cases import properties as uc
from app.application.use_cases.reviews import ListReviews
from app.domain.entities.enums import PropertyStatus
from app.domain.repositories.ports import PropertySearchCriteria
from app.presentation import mappers
from app.presentation.dependencies.security import (
    get_current_actor, get_optional_actor, provide, read_upload, require_owner, require_seeker,
)
from app.presentation.schemas import properties as s
from app.presentation.schemas.common import Message, PageOut
from app.presentation.schemas.social import ReviewListOut, ReviewOut

router = APIRouter(tags=["Logements"])


def criteria(city_id: int | None = None, category_id: int | None = None, min_price: Decimal | None = Query(None, ge=0),
             max_price: Decimal | None = Query(None, ge=0), min_rooms: int | None = Query(None, ge=1),
             coliving: bool | None = None, q: str | None = Query(None, max_length=100),
             sort: str = Query("recent", pattern="^(recent|price_asc|price_desc)$")) -> PropertySearchCriteria:
    return PropertySearchCriteria(city_id=city_id, category_id=category_id, min_price=min_price, max_price=max_price,
                                  min_rooms=min_rooms, coliving=coliving, text=q, sort=sort)


# ---------- Public (consultation) ----------
@router.get("/properties", response_model=PageOut[s.PropertyCardOut])
def search(c: PropertySearchCriteria = Depends(criteria), page: int = Query(1, ge=1), size: int = Query(12, ge=1, le=50),
           actor: Actor | None = Depends(get_optional_actor), usecase: uc.SearchProperties = Depends(provide(uc.SearchProperties))):
    p = usecase.execute(c, page, size, actor.id if actor else None)
    return PageOut(items=[mappers.card_out(i) for i in p.items], total=p.total, page=p.page, size=p.size)


@router.get("/properties/map", response_model=list[s.PropertyCardOut])
def map_view(c: PropertySearchCriteria = Depends(criteria), usecase: uc.MapProperties = Depends(provide(uc.MapProperties))):
    return [mappers.card_out(i) for i in usecase.execute(c)]


# ---------- PROPRIÉTAIRE ----------
@router.get("/properties/mine", response_model=PageOut[s.PropertyCardOut], dependencies=[Depends(require_owner)])
def mine(status: PropertyStatus | None = None, page: int = Query(1, ge=1), size: int = Query(12, ge=1, le=50),
         actor: Actor = Depends(get_current_actor), usecase: uc.ListMyProperties = Depends(provide(uc.ListMyProperties))):
    p = usecase.execute(actor, status, page, size)
    return PageOut(items=[mappers.card_out(i) for i in p.items], total=p.total, page=p.page, size=p.size)


@router.post("/properties", response_model=s.PropertyOut, status_code=201)
def create(body: s.PropertyIn, actor: Actor = Depends(get_current_actor), usecase: uc.CreateProperty = Depends(provide(uc.CreateProperty))):
    return usecase.execute(actor, CreatePropertyCmd(**body.model_dump()))   # le use case exige le rôle OWNER


@router.get("/properties/{property_id}", response_model=s.PropertyDetailOut)
def detail(property_id: int, actor: Actor | None = Depends(get_optional_actor), usecase: uc.GetProperty = Depends(provide(uc.GetProperty))):
    return mappers.detail_out(usecase.execute(property_id, actor.id if actor else None))


@router.put("/properties/{property_id}", response_model=s.PropertyOut)
def update(property_id: int, body: s.PropertyUpdateIn, actor: Actor = Depends(get_current_actor),
           usecase: uc.UpdateProperty = Depends(provide(uc.UpdateProperty))):
    return usecase.execute(actor, property_id, body.model_dump(exclude_unset=True))   # propriétaire de l'annonce uniquement


@router.patch("/properties/{property_id}/status", response_model=s.PropertyOut)
def set_status(property_id: int, body: s.StatusIn, actor: Actor = Depends(get_current_actor),
               usecase: uc.SetPropertyStatus = Depends(provide(uc.SetPropertyStatus))):
    return usecase.execute(actor, property_id, body.status)


@router.delete("/properties/{property_id}", status_code=204)
def delete(property_id: int, actor: Actor = Depends(get_current_actor), usecase: uc.DeleteProperty = Depends(provide(uc.DeleteProperty))):
    usecase.execute(actor, property_id)
    return Response(status_code=204)


@router.post("/properties/{property_id}/images", response_model=s.ImageOut, status_code=201, dependencies=[Depends(require_owner)])
async def add_image(property_id: int, file=Depends(read_upload), actor: Actor = Depends(get_current_actor),
                    usecase: uc.AddPropertyImage = Depends(provide(uc.AddPropertyImage))):
    return usecase.execute(actor, property_id, file)


@router.delete("/properties/{property_id}/images/{image_id}", status_code=204)
def delete_image(property_id: int, image_id: int, actor: Actor = Depends(get_current_actor),
                 usecase: uc.DeletePropertyImage = Depends(provide(uc.DeletePropertyImage))):
    usecase.execute(actor, property_id, image_id)
    return Response(status_code=204)


@router.get("/properties/{property_id}/stats", dependencies=[Depends(require_owner)])
def stats(property_id: int, actor: Actor = Depends(get_current_actor), usecase: uc.PropertyStats = Depends(provide(uc.PropertyStats))):
    return usecase.execute(actor, property_id)


@router.get("/properties/{property_id}/reviews", response_model=ReviewListOut)
def reviews(property_id: int, usecase: ListReviews = Depends(provide(ListReviews))):
    r = usecase.for_property(property_id)
    return ReviewListOut(items=[ReviewOut.model_validate(i) for i in r.items], average=r.average, count=r.count)


# ---------- CHERCHEUR : favoris ----------
@router.get("/favorites", response_model=list[s.PropertyCardOut], tags=["Favoris"], dependencies=[Depends(require_seeker)])
def list_favorites(actor: Actor = Depends(get_current_actor), usecase: uc.ListFavorites = Depends(provide(uc.ListFavorites))):
    return [mappers.card_out(i) for i in usecase.execute(actor)]


@router.put("/favorites/{property_id}", response_model=Message, tags=["Favoris"], dependencies=[Depends(require_seeker)])
def add_favorite(property_id: int, actor: Actor = Depends(get_current_actor), usecase: uc.ToggleFavorite = Depends(provide(uc.ToggleFavorite))):
    usecase.execute(actor, property_id, True)
    return Message(detail="Ajouté aux favoris.")


@router.delete("/favorites/{property_id}", response_model=Message, tags=["Favoris"], dependencies=[Depends(require_seeker)])
def remove_favorite(property_id: int, actor: Actor = Depends(get_current_actor), usecase: uc.ToggleFavorite = Depends(provide(uc.ToggleFavorite))):
    usecase.execute(actor, property_id, False)
    return Message(detail="Retiré des favoris.")


# ---------- CHERCHEUR : recherches enregistrées et alertes ----------
@router.get("/saved-searches", response_model=list[s.SavedSearchOut], tags=["Recherches enregistrées"], dependencies=[Depends(require_seeker)])
def list_searches(actor: Actor = Depends(get_current_actor), usecase: uc.SavedSearches = Depends(provide(uc.SavedSearches))):
    return [s.SavedSearchOut(id=x.id, name=x.name, filters=x.filters, alert_active=a) for x, a in usecase.list(actor)]


@router.post("/saved-searches", response_model=s.SavedSearchOut, status_code=201, tags=["Recherches enregistrées"], dependencies=[Depends(require_seeker)])
def create_search(body: s.SavedSearchIn, actor: Actor = Depends(get_current_actor), usecase: uc.SavedSearches = Depends(provide(uc.SavedSearches))):
    saved, alert = usecase.create(actor, body.name, body.filters, body.alert)
    return s.SavedSearchOut(id=saved.id, name=saved.name, filters=saved.filters, alert_active=alert)


@router.delete("/saved-searches/{search_id}", status_code=204, tags=["Recherches enregistrées"], dependencies=[Depends(require_seeker)])
def delete_search(search_id: int, actor: Actor = Depends(get_current_actor), usecase: uc.SavedSearches = Depends(provide(uc.SavedSearches))):
    usecase.delete(actor, search_id)
    return Response(status_code=204)


@router.put("/saved-searches/{search_id}/alert", response_model=Message, tags=["Recherches enregistrées"], dependencies=[Depends(require_seeker)])
def set_alert(search_id: int, body: s.AlertIn, actor: Actor = Depends(get_current_actor), usecase: uc.SavedSearches = Depends(provide(uc.SavedSearches))):
    usecase.set_alert(actor, search_id, body.active)
    return Message(detail="Alerte mise à jour.")