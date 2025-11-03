from . import BaseDTO


class GamePublic(BaseDTO):
    game_id: str
    join_code: str
    your_role: str
