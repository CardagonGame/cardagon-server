import uuid

from sqlalchemy import CHAR, MetaData, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

metadata_obj = MetaData()


class Base(DeclarativeBase):
    metadata = metadata_obj


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(
        CHAR(32), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False, nullable=False)
