import uuid
from datetime import datetime, timezone

from sqlalchemy import CHAR, ForeignKey, ForeignKeyConstraint, MetaData, String
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
    ForeignKey("")


class Game(Base):
    __tablename__ = "games"
    id: Mapped[str] = mapped_column(
        CHAR(32), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    join_code: Mapped[str] = mapped_column(
        String(6),
        unique=True,
        index=True,
        nullable=False,
        default=lambda: str(uuid.uuid4())[:6].upper(),
    )
    date_created: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.now(timezone.utc)
    )


class UserGameAssociation(Base):
    __tablename__ = "user_game_associations"
    id: Mapped[str] = mapped_column(
        CHAR(32), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        CHAR(32),
        ForeignKey(
            User.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="fk_user_game_association_user",
        ),
        nullable=False,
    )
    game_id: Mapped[str] = mapped_column(
        CHAR(32),
        ForeignKey(
            Game.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="fk_user_game_association_game",
        ),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default="player"  # player or host
    )
