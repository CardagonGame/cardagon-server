from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    email: str | None = None
    password_hash: str


class UserCreate(SQLModel):
    username: str
    email: str | None = None
    password_hash: str


class UserUpdate(SQLModel):
    username: str | None = None
    email: str | None = None
    password_hash: str | None = None
