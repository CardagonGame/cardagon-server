from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic_core import from_json, to_json

from app.dependencies.db import SessionDep
from app.dependencies.static import API_V1_PREFIX
from app.dependencies.user import CurrentUserDep
from app.dto.game_logic import UserConnection
from app.dto.game_requests import ReadyRequest


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
        game_connections = (
            game_connection
            for game_connection in self.active_connections
            if game_connection.game_id == game_id
        )
        for connection in game_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.websocket(f"{API_V1_PREFIX}/game/{{game_id}}/ws")
async def game_websocket_endpoint(
    *, websocket: WebSocket, game_id: str, session: SessionDep, user: CurrentUserDep
):
    user_connection = UserConnection(
        user_id=user.id,
        game_id=game_id,
        websocket=websocket,
    )
    await manager.connect(user_connection)
    try:
        while True:
            data = await websocket.receive_text()
            parsed_data = from_json(data)
            match parsed_data.get("type"):
                case "ready":
                    client_request = ReadyRequest.model_validate(parsed_data)
                    manager.send_personal_message(
                        "You are ready!",
                        user_connection,
                    )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
