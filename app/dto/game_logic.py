from fastapi import WebSocket

from app.dto import BaseDTO


class UserConnection(BaseDTO):
    user_id: str
    game_id: str
    websocket: WebSocket
