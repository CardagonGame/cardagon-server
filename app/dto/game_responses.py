from app.dto import BaseDTO


class UserGameStateResponse(BaseDTO):
    type: str = "user_game_state"
    field_radius: int
