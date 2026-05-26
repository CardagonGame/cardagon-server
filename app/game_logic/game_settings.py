# WIP: domain model, not yet wired into the API
from app.dto import BaseDTO

class GameSettings(BaseDTO):
    player_amount: int = 2
    board_radius: int = 5
    start_money: int = 100