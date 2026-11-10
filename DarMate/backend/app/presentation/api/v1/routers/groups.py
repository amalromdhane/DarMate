from fastapi import APIRouter, Depends, Response

from app.application.dto.dto import Actor
from app.application.use_cases import groups as uc
from app.presentation import mappers
from app.presentation.dependencies.security import get_current_actor, provide
from app.presentation.schemas import social as s

router = APIRouter(tags=["Groupes de colocation"])


@router.post("/groups", response_model=s.GroupOut, status_code=201)
def create(body: s.GroupIn, actor: Actor = Depends(get_current_actor), usecase: uc.CreateGroup = Depends(provide(uc.CreateGroup))):
    return mappers.group_out(usecase.execute(actor, body.name, body.max_members))


@router.get("/groups", response_model=list[s.GroupOut])
def mine(actor: Actor = Depends(get_current_actor), usecase: uc.ListMyGroups = Depends(provide(uc.ListMyGroups))):
    return [mappers.group_out(v) for v in usecase.execute(actor)]


@router.get("/group-invitations", response_model=list[s.InvitationOut])
def invitations(actor: Actor = Depends(get_current_actor), usecase: uc.ListMyInvitations = Depends(provide(uc.ListMyInvitations))):
    return usecase.execute(actor)


@router.patch("/group-invitations/{invitation_id}", response_model=s.InvitationOut)
def respond(invitation_id: int, body: s.RespondIn, actor: Actor = Depends(get_current_actor),
            usecase: uc.RespondGroupInvitation = Depends(provide(uc.RespondGroupInvitation))):
    return usecase.execute(actor, invitation_id, body.accept)


@router.get("/groups/{group_id}", response_model=s.GroupOut)
def get(group_id: int, actor: Actor = Depends(get_current_actor), usecase: uc.GetGroup = Depends(provide(uc.GetGroup))):
    return mappers.group_out(usecase.execute(actor, group_id))


@router.delete("/groups/{group_id}", status_code=204)
def delete(group_id: int, actor: Actor = Depends(get_current_actor), usecase: uc.DeleteGroup = Depends(provide(uc.DeleteGroup))):
    usecase.execute(actor, group_id)
    return Response(status_code=204)


@router.post("/groups/{group_id}/invitations", response_model=s.InvitationOut, status_code=201)
def invite(group_id: int, body: s.InviteIn, actor: Actor = Depends(get_current_actor), usecase: uc.InviteToGroup = Depends(provide(uc.InviteToGroup))):
    return usecase.execute(actor, group_id, body.invitee_id)


@router.delete("/groups/{group_id}/members/{user_id}", status_code=204)
def remove_member(group_id: int, user_id: int, actor: Actor = Depends(get_current_actor),
                  usecase: uc.RemoveGroupMember = Depends(provide(uc.RemoveGroupMember))):
    usecase.execute(actor, group_id, user_id)
    return Response(status_code=204)
