from app.dto import BaseDTO


class UserGameStateResponse(BaseDTO):
    type: str = "user_game_state"
    field_radius: int


class PlayerInfo(BaseDTO):
    user_id: str
    username: str
    role: str


class PlayersMessage(BaseDTO):
    type: str = "players"
    players: list[PlayerInfo]
