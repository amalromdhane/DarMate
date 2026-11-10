from fastapi import APIRouter, Depends, Query

from app.application.dto.dto import Actor
from app.application.use_cases import roommates as uc
from app.presentation.dependencies.security import get_current_actor, provide
from app.presentation.schemas import social as s

router = APIRouter(tags=["Colocataires"])


@router.get("/roommates/me", response_model=s.RoommateProfileOut | None)
def my_profile(actor: Actor = Depends(get_current_actor), usecase: uc.GetMyRoommateProfile = Depends(provide(uc.GetMyRoommateProfile))):
    return usecase.execute(actor)


@router.put("/roommates/me", response_model=s.RoommateProfileOut)
def save_profile(body: s.RoommateProfileIn, actor: Actor = Depends(get_current_actor),
                 usecase: uc.UpsertRoommateProfile = Depends(provide(uc.UpsertRoommateProfile))):
    return usecase.execute(actor, body.model_dump())


@router.get("/roommates", response_model=list[s.RoommateMatchOut])
def search(city_id: int | None = None, min_score: int = Query(0, ge=0, le=100), actor: Actor = Depends(get_current_actor),
           usecase: uc.SearchRoommates = Depends(provide(uc.SearchRoommates))):
    return [s.RoommateMatchOut(profile=s.RoommateProfileOut.model_validate(m.profile), display_name=m.display_name, score=m.score)
            for m in usecase.execute(actor, city_id, min_score)]


@router.get("/roommates/{user_id}/compatibility")
def compatibility(user_id: int, actor: Actor = Depends(get_current_actor), usecase: uc.GetCompatibility = Depends(provide(uc.GetCompatibility))):
    return {"user_id": user_id, "score": usecase.execute(actor, user_id)}


@router.get("/roommate-requests", response_model=list[s.RoommateRequestOut])
def list_requests(actor: Actor = Depends(get_current_actor), usecase: uc.ListRoommateRequests = Depends(provide(uc.ListRoommateRequests))):
    return usecase.execute(actor)


@router.post("/roommate-requests", response_model=s.RoommateRequestOut, status_code=201)
def send_request(body: s.RoommateRequestIn, actor: Actor = Depends(get_current_actor),
                 usecase: uc.SendRoommateRequest = Depends(provide(uc.SendRoommateRequest))):
    return usecase.execute(actor, body.receiver_id, body.message)


@router.patch("/roommate-requests/{request_id}", response_model=s.RoommateRequestOut)
def respond(request_id: int, body: s.RespondIn, actor: Actor = Depends(get_current_actor),
            usecase: uc.RespondRoommateRequest = Depends(provide(uc.RespondRoommateRequest))):
    return usecase.execute(actor, request_id, body.accept)
