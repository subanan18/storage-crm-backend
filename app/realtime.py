from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime, timezone

from fastapi import WebSocket


class RealtimeHub:
    """In-memory WebSocket hub for lightweight CRM notifications.

    This is intentionally process-local for the portfolio version. A production
    multi-instance deployment can swap this layer for Redis pub/sub without
    changing the WebSocket API used by the frontend.
    """

    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, channel: str) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[channel].add(websocket)

    async def disconnect(self, websocket: WebSocket, channel: str) -> None:
        async with self._lock:
            self._connections[channel].discard(websocket)
            if not self._connections[channel]:
                self._connections.pop(channel, None)

    async def publish(self, channel: str, event_type: str, payload: dict) -> None:
        message = {
            "type": event_type,
            "channel": channel,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }
        stale: list[WebSocket] = []
        for websocket in list(self._connections.get(channel, set())):
            try:
                await websocket.send_json(message)
            except Exception:
                stale.append(websocket)

        for websocket in stale:
            await self.disconnect(websocket, channel)

    def connection_count(self, channel: str | None = None) -> int:
        if channel is not None:
            return len(self._connections.get(channel, set()))
        return sum(len(group) for group in self._connections.values())


realtime_hub = RealtimeHub()
