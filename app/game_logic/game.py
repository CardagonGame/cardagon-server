from app.game_logic.board import Board
from app.game_logic.game_settings import GameSettings


class Game():
    def __init__(self, settings: GameSettings):
        self.settings = settings
        self.player_amount = self.settings.player_amount
        self.turn_nr = 0

        self.board = Board(self.settings.board_radius)
    
    def get_fields(self):
        return self.board.get_fields()
            

    def get_field(self, q, r, s):
        return self.board.get_field(q, r, s)

        


