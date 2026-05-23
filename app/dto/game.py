from datetime import datetime

from . import BaseDTO
from app.dto.game_responses import PlayerInfo


class GamePublic(BaseDTO):
    game_id: str
    join_code: str
    your_role: str
    date_created: datetime
    name: str
    started: bool = False
    current_turn: int = 0


class GameDetailResponse(GamePublic):
    players: list[PlayerInfo]


class UserGamesResponse(BaseDTO):
    hosted: list[GamePublic]
    joined: list[GamePublic]
