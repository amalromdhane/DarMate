"""Gestionnaire de connexions WebSocket (temps réel de la messagerie)."""
import asyncio
from collections import defaultdict

from fastapi import WebSocket

from app.application.interfaces.services import RealtimePublisher


class ConnectionManager(RealtimePublisher):
    def __init__(self) -> None:
        self._connections: dict[int, set[WebSocket]] = defaultdict(set)
        self._loop: asyncio.AbstractEventLoop | None = None

    async def connect(self, user_id: int, ws: WebSocket) -> None:
        self._loop = asyncio.get_running_loop()
        self._connections[user_id].add(ws)

    def disconnect(self, user_id: int, ws: WebSocket) -> None:
        self._connections[user_id].discard(ws)

    async def _send(self, user_ids: list[int], payload: dict) -> None:
        for uid in user_ids:
            for ws in list(self._connections.get(uid, ())):
                try:
                    await ws.send_json(payload)
                except Exception:
                    self._connections[uid].discard(ws)

    def publish_message(self, user_ids, payload) -> None:
        """Appelable depuis du code synchrone (threads FastAPI)."""
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self._send(user_ids, payload), self._loop)


manager = ConnectionManager()
