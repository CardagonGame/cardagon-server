import random

from app.game_logic.hex import Hex, hex_distance


def generate_start_positions(
    field_size: int, player_count: int, max_attempts: int = 200
) -> list[tuple[int, int, int]]:
    target_distance = field_size - 2
    radius = field_size - 1
    lower_bound = -radius + 1

    valid_hexes = []
    for q in range(lower_bound, radius + 1):
        r_start = lower_bound - q if q < 0 else lower_bound
        r_end = radius if q < 0 else radius - q
        for r in range(r_start, r_end + 1):
            s = -q - r
            if hex_distance(q, r, s, 0, 0, 0) == target_distance:
                valid_hexes.append((q, r, s))

    if player_count > len(valid_hexes):
        raise ValueError(
            f"Cannot place {player_count} players: only {len(valid_hexes)} valid hexes."
        )

    for _ in range(max_attempts):
        random.shuffle(valid_hexes)
        chosen_positions = []
        for candidate in valid_hexes:
            far_enough = all(
                hex_distance(*candidate, *existing) >= 3
                for existing in chosen_positions
            )
            if far_enough:
                chosen_positions.append(candidate)
            if len(chosen_positions) == player_count:
                return chosen_positions

    raise ValueError(
        f"Could not find {player_count} valid start positions after {max_attempts} attempts."
    )


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