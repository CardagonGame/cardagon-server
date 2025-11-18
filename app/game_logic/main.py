# For testing

from app.game_logic.game import Game
from app.game_logic.game_settings import GameSettings

game = Game(GameSettings())

game.get_field(0, 3, -3).set_player("andr0")
print(game.get_field(0, 3, -3).get_hex_info())

for field in game.get_fields().values():
    print(field.get_hex_info())