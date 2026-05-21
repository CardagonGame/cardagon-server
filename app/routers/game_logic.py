from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic_core import from_json
from sqlalchemy.orm import Session

from app.dependencies.db import SessionDep
from app.dependencies.static import API_V1_PREFIX
from app.dependencies.user import get_current_user
from app.dto.game_logic import UserConnection
from app.dto.game_requests import ReadyRequest
from app.dto.game_responses import (
    PlayerInfo,
    PlayersMessage,
    WsPlayerInfo,
    WsPlayersMessage,
)
from app.models import User, UserGameAssociation

router = APIRouter(tags=["game_router"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[UserConnection] = []

    async def connect(self, user_connection: UserConnection):
        await user_connection.websocket.accept()
        self.active_connections.append(user_connection)

    def disconnect(self, user_connection: UserConnection):
        self.active_connections.remove(user_connection)

    async def send_personal_message(
        self, message: str, user_connection: UserConnection
    ):
        await user_connection.websocket.send_text(message)

    async def broadcast(self, game_id: str, message: str):
        for connection in self.active_connections:
            if connection.game_id == game_id:
                await connection.websocket.send_text(message)


manager = ConnectionManager()


def _fetch_player_rows(game_id: str, session: Session):
    return (
        session.query(User, UserGameAssociation)
        .join(UserGameAssociation, UserGameAssociation.user_id == User.id)
        .filter(UserGameAssociation.game_id == game_id)
        .all()
    )


def get_players(game_id: str, session: Session) -> PlayersMessage:
    rows = _fetch_player_rows(game_id, session)
    online_ids = {c.user_id for c in manager.active_connections if c.game_id == game_id}
    return PlayersMessage(
        players=[
            PlayerInfo(
                user_id=user.id,
                username=user.username,
                role=assoc.role,
                online=user.id in online_ids,
            )
            for user, assoc in rows
        ]
    )


def get_ws_players(game_id: str, session: Session) -> WsPlayersMessage:
    rows = _fetch_player_rows(game_id, session)
    conns = {c.user_id: c for c in manager.active_connections if c.game_id == game_id}
    return WsPlayersMessage(
        players=[
            WsPlayerInfo(
                user_id=user.id,
                username=user.username,
                role=assoc.role,
                online=user.id in conns,
                ping_ms=conns[user.id].ping_ms if user.id in conns else None,
            )
            for user, assoc in rows
        ]
    )


@router.websocket(f"{API_V1_PREFIX}/game/{{game_id}}/ws")
async def game_websocket_endpoint(
    websocket: WebSocket,
    game_id: str,
    session: SessionDep,
    token: str = Query(...),
):
    try:
        user = get_current_user(session=session, token=token)
    except HTTPException:
        await websocket.close(code=4003)
        return
    user_connection = UserConnection(
        user_id=user.id,
        game_id=game_id,
        websocket=websocket,
    )
    await manager.connect(user_connection)
    await manager.broadcast(game_id, get_ws_players(game_id, session).model_dump_json())
    try:
        while True:
            data = await websocket.receive_text()
            parsed_data = from_json(data)
            match parsed_data.get("type"):
                case "ping":
                    await manager.send_personal_message(
                        '{"type":"pong"}',
                        user_connection,
                    )
                case "ping_result":
                    ms = parsed_data.get("ms")
                    if isinstance(ms, int):
                        user_connection.ping_ms = ms
                        await manager.broadcast(
                            game_id, get_ws_players(game_id, session).model_dump_json()
                        )
                case "ready":
                    ReadyRequest.model_validate(parsed_data)
                    await manager.send_personal_message(
                        "You are ready!",
                        user_connection,
                    )

    except WebSocketDisconnect:
        manager.disconnect(user_connection)
        await manager.broadcast(
            game_id,
            get_ws_players(game_id, session).model_dump_json(),
        )
