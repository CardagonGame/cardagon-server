from pydantic import BaseModel, ConfigDict, Field, model_validator


class BaseDTO(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class UserBase(BaseDTO):
    email: str = Field(max_length=255)
    username: str = Field(max_length=50)
    is_active: bool = True
    is_admin: bool = False


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=255)


class UserPublic(BaseDTO):
    email: str
    username: str
    id: str


class UserRegister(BaseDTO):
    email: str = Field(max_length=255)
    username: str = Field(max_length=50)
    password: str = Field(min_length=8, max_length=255)
    invite_code: str | None


class Token(BaseDTO):
    access_token: str
    token_type: str = "bearer"
