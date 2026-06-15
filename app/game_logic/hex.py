# WIP: domain model, not yet wired into the API


def hex_distance(q1: int, r1: int, s1: int, q2: int, r2: int, s2: int) -> int:
    return (abs(q1 - q2) + abs(r1 - r2) + abs(s1 - s2)) // 2


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