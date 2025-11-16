from app.dto import BaseDTO


class ReadyRequest(BaseDTO):
    type: str = "ready"