

class Hex():
    def __init__(self, q: int, r: int, s: int):
        self.q = q
        self.r = r
        self.s = s
        self.player = None
    
    def get_hex_info(self):
        return self.__dict__

    def set_player(self, player):
        self.player = player