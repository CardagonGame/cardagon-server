from app.game_logic.hex import Hex

class Board():
    def __init__(self, radius: int = 5):
        self.radius = radius
        self.fields = {}
        higher_bound, lower_bound = radius - 1, -radius + 1

        for q in range(lower_bound, higher_bound + 1):
            if q < 0:
                r_start, r_end = lower_bound - q, higher_bound

            else:
                r_start, r_end = lower_bound, higher_bound - q

            for r in range(r_start, r_end + 1):
                s = 0 - q - r
                self.fields[(q, r, s)] = Hex(q, r, s)

    def get_fields(self):
        return self.fields
    
    def get_field(self, q, r, s):
        return self.fields[(q, r, s)]