import uuid
from datetime import datetime, timezone

from coolname import generate_slug
from sqlalchemy import CHAR, ForeignKey, Integer, MetaData, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

metadata_obj = MetaData()


class Base(DeclarativeBase):
    metadata = metadata_obj


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(
        CHAR(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False, nullable=False)


class Game(Base):
    __tablename__ = "games"
    id: Mapped[str] = mapped_column(
        CHAR(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    join_code: Mapped[str] = mapped_column(
        String(6),
        unique=True,
        index=True,
        nullable=False,
        default=lambda: str(uuid.uuid4())[:6].upper(),
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, default=lambda: generate_slug(2).replace("-", " ")
    )
    date_created: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class GameEvent(Base):
    __tablename__ = "game_events"
    id: Mapped[str] = mapped_column(
        CHAR(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    game_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey(
            Game.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="fk_game_events_game",
        ),
        nullable=False,
    )
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    turn_number: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[str | None] = mapped_column(
        CHAR(36),
        ForeignKey(
            User.id,
            onupdate="CASCADE",
            ondelete="SET NULL",
            name="fk_game_events_user",
        ),
        nullable=True,
    )
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict, server_default="{}"
    )
    date_created: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class UserGameAssociation(Base):
    __tablename__ = "user_game_associations"
    id: Mapped[str] = mapped_column(
        CHAR(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey(
            User.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="fk_user_game_association_user",
        ),
        nullable=False,
    )
    game_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey(
            Game.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="fk_user_game_association_game",
        ),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="player",  # player or host
    )
    color: Mapped[str] = mapped_column(String(7), nullable=False, default="#000000")
    date_created: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )
