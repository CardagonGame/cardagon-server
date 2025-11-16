from app.dto import BaseDTO

class GameSettings(BaseDTO):
    player_amount: int
    board_radius: int
    start_money: int