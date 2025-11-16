from pydantic import BaseModel


class Game(BaseModel):
    round_nr: int = 0