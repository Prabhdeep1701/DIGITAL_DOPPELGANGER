"""WebSocket endpoints for real-time event streaming."""

import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Set

from app.database.session import async_session
from app.services.event_processor import process_event, finalize_session

router = APIRouter()

# Connected clients per session
_connections: Dict[str, Set[WebSocket]] = {}
# Global dashboard listeners
_dashboard_listeners: Set[WebSocket] = set()


async def broadcast_to_session(session_id: str, data: dict):
    """Broadcast event data to all listeners of a session."""
    listeners = _connections.get(session_id, set())
    dead = set()
    for ws in listeners:
        try:
            await ws.send_json(data)
        except Exception:
            dead.add(ws)
    _connections[session_id] = listeners - dead


async def broadcast_to_dashboard(data: dict):
    """Broadcast to all dashboard listeners."""
    dead = set()
    for ws in _dashboard_listeners:
        try:
            await ws.send_json(data)
        except Exception:
            dead.add(ws)
    _dashboard_listeners.difference_update(dead)


@router.websocket("/events/{session_id}")
async def websocket_events(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time event processing.

    Client sends events, server processes them through the automata engine
    and sends back state transitions in real time.
    """
    await websocket.accept()

    if session_id not in _connections:
        _connections[session_id] = set()
    _connections[session_id].add(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            event = json.loads(data)

            async with async_session() as db:
                result = await process_event(
                    db,
                    session_id=session_id,
                    event_type=event.get("event_type", ""),
                    timestamp=event.get("timestamp", 0),
                    page=event.get("page"),
                    target=event.get("target"),
                    metadata=event.get("metadata"),
                )
                await db.commit()

            # Send result back to this client
            await websocket.send_json(result)

            # Broadcast to other session listeners
            await broadcast_to_session(session_id, result)

            # Broadcast summary to dashboard
            await broadcast_to_dashboard({
                "type": "event",
                "session_id": session_id,
                "event_type": event.get("event_type"),
                "product_state": result["product_state"],
                "is_suspicious": result["is_suspicious"],
            })

    except WebSocketDisconnect:
        _connections.get(session_id, set()).discard(websocket)
        # Finalize session on disconnect
        async with async_session() as db:
            try:
                await finalize_session(db, session_id)
                await db.commit()
            except Exception:
                pass
    except Exception:
        _connections.get(session_id, set()).discard(websocket)


@router.websocket("/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """WebSocket endpoint for real-time dashboard updates."""
    await websocket.accept()
    _dashboard_listeners.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep alive
    except WebSocketDisconnect:
        _dashboard_listeners.discard(websocket)
    except Exception:
        _dashboard_listeners.discard(websocket)
