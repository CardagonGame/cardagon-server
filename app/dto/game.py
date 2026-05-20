from datetime import datetime

from . import BaseDTO


class GamePublic(BaseDTO):
    game_id: str
    join_code: str
    your_role: str
    date_created: datetime
    name: str


class UserGamesResponse(BaseDTO):
    hosted: list[GamePublic]
    joined: list[GamePublic]
