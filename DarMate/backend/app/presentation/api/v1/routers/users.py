import mimetypes

from fastapi import APIRouter, Depends, Response, UploadFile, File, Form

from app.application.dto.dto import Actor
from app.application.use_cases import users as uc
from app.application.use_cases.auth import ChangePassword
from app.application.use_cases.reviews import ListReviews
from app.presentation import mappers
from app.presentation.dependencies.security import get_current_actor, provide, read_upload
from app.presentation.schemas import auth as s
from app.presentation.schemas.common import Message
from app.presentation.schemas.social import ReviewListOut, ReviewOut

router = APIRouter(tags=["Utilisateurs"])


@router.get("/users/me", response_model=s.UserOut)
def me(actor: Actor = Depends(get_current_actor), usecase: uc.GetUser = Depends(provide(uc.GetUser))):
    return mappers.user_out(usecase.execute(actor.id))


@router.put("/users/me", response_model=s.UserOut)
def update_me(body: s.ProfileUpdateIn, actor: Actor = Depends(get_current_actor),
              usecase: uc.UpdateMyProfile = Depends(provide(uc.UpdateMyProfile))):
    return mappers.user_out(usecase.execute(actor, body.model_dump(exclude_unset=True)))


@router.put("/users/me/password", response_model=Message)
def change_password(body: s.ChangePasswordIn, actor: Actor = Depends(get_current_actor),
                    usecase: ChangePassword = Depends(provide(ChangePassword))):
    usecase.execute(actor, body.current_password, body.new_password)
    return Message(detail="Mot de passe modifié. Reconnectez-vous sur vos autres appareils.")


@router.post("/users/me/identity-documents", status_code=201)
async def upload_identity(doc_type: str = Form("ID_CARD"), file=Depends(read_upload), actor: Actor = Depends(get_current_actor),
                          usecase: uc.UploadIdentityDocument = Depends(provide(uc.UploadIdentityDocument))):
    doc = usecase.execute(actor, file, doc_type)
    return {"id": doc.id, "doc_type": doc.doc_type, "status": doc.status}


@router.get("/users/identity-documents/{doc_id}")
def download_identity(doc_id: int, actor: Actor = Depends(get_current_actor),
                      usecase: uc.DownloadIdentityDocument = Depends(provide(uc.DownloadIdentityDocument))):
    data, path = usecase.execute(actor, doc_id)
    return Response(data, media_type=mimetypes.guess_type(path)[0] or "application/octet-stream",
                    headers={"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff"})


@router.get("/users/{user_id}/public-profile", response_model=s.PublicUserOut)
def public_profile(user_id: int, _: Actor = Depends(get_current_actor), usecase: uc.GetUser = Depends(provide(uc.GetUser))):
    return mappers.public_user_out(usecase.execute(user_id, with_rating=True))


@router.get("/users/{user_id}/reviews", response_model=ReviewListOut)
def user_reviews(user_id: int, usecase: ListReviews = Depends(provide(ListReviews))):
    r = usecase.for_user(user_id)
    return ReviewListOut(items=[ReviewOut.model_validate(i) for i in r.items], average=r.average, count=r.count)


@router.post("/users/{user_id}/block", response_model=Message)
def block(user_id: int, actor: Actor = Depends(get_current_actor), usecase: uc.BlockUser = Depends(provide(uc.BlockUser))):
    usecase.execute(actor, user_id, True)
    return Message(detail="Utilisateur bloqué.")


@router.delete("/users/{user_id}/block", response_model=Message)
def unblock(user_id: int, actor: Actor = Depends(get_current_actor), usecase: uc.BlockUser = Depends(provide(uc.BlockUser))):
    usecase.execute(actor, user_id, False)
    return Message(detail="Utilisateur débloqué.")


@router.post("/reports", response_model=Message, status_code=201)
def report(body: s.ReportIn, actor: Actor = Depends(get_current_actor), usecase: uc.ReportUser = Depends(provide(uc.ReportUser))):
    usecase.execute(actor, body.reported_user_id, body.reason, body.details, body.message_id)
    return Message(detail="Merci, votre signalement a été transmis à l'équipe de modération.")
