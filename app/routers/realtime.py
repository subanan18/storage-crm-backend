from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.realtime import realtime_hub

router = APIRouter(prefix="/realtime", tags=["realtime"])


@router.websocket("/ws/{channel}")
async def realtime_channel(websocket: WebSocket, channel: str) -> None:
    await realtime_hub.connect(websocket, channel)
    await websocket.send_json(
        {
            "type": "connected",
            "channel": channel,
            "payload": {"message": "Realtime CRM channel connected"},
        }
    )

    try:
        while True:
            message = await websocket.receive_text()
            if message.strip().lower() == "ping":
                await websocket.send_json(
                    {
                        "type": "pong",
                        "channel": channel,
                        "payload": {"connections": realtime_hub.connection_count(channel)},
                    }
                )
    except WebSocketDisconnect:
        await realtime_hub.disconnect(websocket, channel)
