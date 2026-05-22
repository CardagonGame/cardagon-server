from app.dto import BaseDTO


class UserGameStateResponse(BaseDTO):
    type: str = "user_game_state"
    field_radius: int


class GameState(BaseDTO):
    type: str = "game_state"
    started: bool = False


class PlayerInfo(BaseDTO):
    user_id: str
    username: str
    role: str
    online: bool = False


class PlayersMessage(BaseDTO):
    type: str = "players"
    players: list[PlayerInfo]


class WsPlayerInfo(PlayerInfo):
    ping_ms: int | None = None


class WsPlayersMessage(BaseDTO):
    type: str = "players"
    players: list[WsPlayerInfo]
