from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    username: str
    password_hash: str

class UserLogin(SQLModel):
    email: str
    password: str

class UserRegister(SQLModel):
    email: str = Field(max_length=255)
    username: str = Field(max_length=50)
    password: str = Field(min_length=255)
    