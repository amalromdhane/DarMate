from fastapi import APIRouter, Depends, Query

from app.application.dto.dto import Actor
from app.application.use_cases.notifications import Notifications
from app.presentation.dependencies.security import get_current_actor, provide
from app.presentation.schemas import messaging as s
from app.presentation.schemas.common import Message

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=s.NotificationListOut)
def list_notifications(unread_only: bool = False, limit: int = Query(50, ge=1, le=100), actor: Actor = Depends(get_current_actor),
                       usecase: Notifications = Depends(provide(Notifications))):
    items, unread = usecase.list(actor, unread_only, limit)
    return s.NotificationListOut(items=[s.NotificationOut.model_validate(i) for i in items], unread_count=unread)


@router.patch("/read-all", response_model=Message)
def read_all(actor: Actor = Depends(get_current_actor), usecase: Notifications = Depends(provide(Notifications))):
    usecase.mark_all_read(actor)
    return Message(detail="Toutes les notifications sont lues.")


@router.patch("/{notification_id}/read", response_model=Message)
def read_one(notification_id: int, actor: Actor = Depends(get_current_actor), usecase: Notifications = Depends(provide(Notifications))):
    usecase.mark_read(actor, notification_id)
    return Message(detail="Notification lue.")
