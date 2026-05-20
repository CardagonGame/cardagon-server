from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from pydantic_core import from_json
from sqlalchemy.orm import Session

from app.dependencies.db import SessionDep
from app.dependencies.static import API_V1_PREFIX
from app.dependencies.user import CurrentUserDep, get_current_user
from app.dto.game_logic import UserConnection
from app.dto.game_requests import ReadyRequest
from app.dto.game_responses import PlayerInfo, PlayersMessage
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

    async def send_personal_message(self, message: str, user_connection: UserConnection):
        await user_connection.websocket.send_text(message)

    async def broadcast(self, game_id: str, message: str):
        for connection in self.active_connections:
            if connection.game_id == game_id:
                await connection.websocket.send_text(message)


manager = ConnectionManager()


def get_players(game_id: str, session: Session) -> PlayersMessage:
    rows = (
        session.query(User, UserGameAssociation)
        .join(UserGameAssociation, UserGameAssociation.user_id == User.id)
        .filter(UserGameAssociation.game_id == game_id)
        .all()
    )
    return PlayersMessage(
        players=[
            PlayerInfo(user_id=user.id, username=user.username, role=assoc.role)
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
    user = get_current_user(session=session, token=token)
    user_connection = UserConnection(
        user_id=user.id,
        game_id=game_id,
        websocket=websocket,
    )
    await manager.connect(user_connection)
    await manager.send_personal_message(
        get_players(game_id, session).model_dump_json(),
        user_connection,
    )
    try:
        while True:
            data = await websocket.receive_text()
            parsed_data = from_json(data)
            match parsed_data.get("type"):
                case "ready":
                    client_request = ReadyRequest.model_validate(parsed_data)
                    await manager.send_personal_message(
                        "You are ready!",
                        user_connection,
                    )

    except WebSocketDisconnect:
        manager.disconnect(user_connection)
        await manager.broadcast(
            game_id,
            get_players(game_id, session).model_dump_json(),
        )
