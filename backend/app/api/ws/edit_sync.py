"""
WebSocket foundation for live edit session sync (collaboration-ready, single-user for now).
"""

from __future__ import annotations

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["websocket"])

_connections: dict[str, set[WebSocket]] = {}


@router.websocket("/ws/edit/{session_id}")
async def edit_session_ws(websocket: WebSocket, session_id: str) -> None:
    await websocket.accept()
    pool = _connections.setdefault(session_id, set())
    pool.add(websocket)
    logger.info("ws_connected", session_id=session_id)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                msg = {"type": "ping"}

            if msg.get("type") == "ping":
                await websocket.send_json(
                    {"type": "pong", "session_id": session_id, "collaboration": False}
                )
            elif msg.get("type") == "subscribe":
                await websocket.send_json(
                    {
                        "type": "subscribed",
                        "session_id": session_id,
                        "message": "Real-time sync channel ready (multi-user editing: future)",
                    }
                )
            else:
                await websocket.send_json({"type": "ack", "received": msg.get("type")})
    except WebSocketDisconnect:
        pool.discard(websocket)
        if not pool:
            _connections.pop(session_id, None)
        logger.info("ws_disconnected", session_id=session_id)


async def broadcast_session_event(session_id: str, event: dict) -> None:
    """Broadcast to all subscribers — call from edit handlers when collaboration ships."""
    for ws in list(_connections.get(session_id, [])):
        try:
            await ws.send_json(event)
        except Exception:
            _connections.get(session_id, set()).discard(ws)
