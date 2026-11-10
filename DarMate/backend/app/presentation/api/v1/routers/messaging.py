import asyncio

from fastapi import APIRouter, Depends, Query, Response, WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_in_threadpool

from app.application.dto.dto import Actor
from app.application.use_cases import messaging as uc
from app.core.config import settings
from app.core.exceptions import AppError
from app.infrastructure.database.connection import SessionLocal
from app.infrastructure.external_services.realtime import manager
from app.infrastructure.external_services.services import guess_mime
from app.presentation import mappers
from app.presentation.dependencies.security import actor_from_token, get_current_actor, provide, read_upload
from app.presentation.schemas import messaging as s
from app.application.dto.dto import MessageView

router = APIRouter(tags=["Messagerie"])


@router.get("/conversations", response_model=list[s.ConversationOut])
def conversations(actor: Actor = Depends(get_current_actor), usecase: uc.ListConversations = Depends(provide(uc.ListConversations))):
    return [mappers.conversation_out(v) for v in usecase.execute(actor)]


@router.post("/conversations", response_model=dict, status_code=201)
def open_conversation(body: s.OpenConversationIn, actor: Actor = Depends(get_current_actor),
                      usecase: uc.OpenPrivateConversation = Depends(provide(uc.OpenPrivateConversation))):
    return {"id": usecase.execute(actor, body.user_id).id}


@router.get("/conversations/{conversation_id}/messages", response_model=list[s.MessageOut])
def messages(conversation_id: int, before_id: int | None = None, limit: int = Query(50, ge=1, le=100),
             actor: Actor = Depends(get_current_actor), usecase: uc.GetMessages = Depends(provide(uc.GetMessages))):
    return [mappers.message_out(v) for v in usecase.execute(actor, conversation_id, before_id, limit)]


@router.post("/conversations/{conversation_id}/messages", response_model=s.MessageOut, status_code=201)
def send(conversation_id: int, body: s.MessageIn, actor: Actor = Depends(get_current_actor), usecase: uc.SendMessage = Depends(provide(uc.SendMessage))):
    return mappers.message_out(usecase.execute(actor, conversation_id, body.body, body.property_id))


@router.post("/conversations/{conversation_id}/attachments", response_model=s.MessageOut, status_code=201)
async def send_attachment(conversation_id: int, file=Depends(read_upload), actor: Actor = Depends(get_current_actor),
                          usecase: uc.SendMessage = Depends(provide(uc.SendMessage))):
    return mappers.message_out(usecase.execute(actor, conversation_id, None, None, file))


@router.patch("/conversations/{conversation_id}/read", status_code=204)
def mark_read(conversation_id: int, actor: Actor = Depends(get_current_actor), usecase: uc.MarkConversationRead = Depends(provide(uc.MarkConversationRead))):
    usecase.execute(actor, conversation_id)
    return Response(status_code=204)


@router.get("/attachments/{attachment_id}")
def download(attachment_id: int, actor: Actor = Depends(get_current_actor), usecase: uc.DownloadAttachment = Depends(provide(uc.DownloadAttachment))):
    data, att = usecase.execute(actor, attachment_id)
    safe_name = att.original_name.replace('"', "").replace("\n", "")
    return Response(data, media_type=att.mime_type, headers={
        "Content-Disposition": f'attachment; filename="{safe_name}"', "X-Content-Type-Options": "nosniff", "Cache-Control": "private, no-store"})


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """Temps réel : le premier message doit être {"type":"auth","token":"<access_token>"} (jamais dans l'URL)."""
    origin = ws.headers.get("origin")
    if origin and origin not in settings.cors_origins:
        await ws.close(code=4403)
        return
    await ws.accept()
    try:
        first = await asyncio.wait_for(ws.receive_json(), timeout=10)

        def authenticate() -> Actor:
            with SessionLocal() as db:
                return actor_from_token(first.get("token", ""), db)
        actor = await run_in_threadpool(authenticate)
    except (AppError, asyncio.TimeoutError, WebSocketDisconnect, ValueError, AttributeError):
        await ws.close(code=4401)
        return
    await manager.connect(actor.id, ws)
    await ws.send_json({"type": "ready"})
    try:
        while True:
            data = await ws.receive_json()
            if data.get("type") == "ping":
                await ws.send_json({"type": "pong"})
    except (WebSocketDisconnect, ValueError):
        pass
    finally:
        manager.disconnect(actor.id, ws)
