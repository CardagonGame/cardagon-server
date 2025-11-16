from app.game_logic.board import Board
from app.game_logic.game_settings import GameSettings


class Game():
    def __init__(self, settings: GameSettings = None):
        self.settings = settings
        self.player_amount = self.settings.player_amount
        self.turn_nr = 0

        self.board = Board()

        


