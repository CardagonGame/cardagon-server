from fastapi import WebSocket

from app.dto import BaseDTO


class UserConnection(BaseDTO):
    class Config:
        arbitrary_types_allowed = True

    user_id: str
    game_id: str
    websocket: WebSocket
