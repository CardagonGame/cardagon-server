import uuid

import distinctipy
from fastapi import APIRouter, HTTPException, Response
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.dependencies.colors import hex_to_rgb, rgb_to_hex
from app.dependencies.db import SessionDep
from app.dependencies.game_logic import get_players
from app.dependencies.static import API_V1_PREFIX
from app.dependencies.user import CurrentUserDep
from app.dto.game import GameDetailResponse, GamePublic, UserGamesResponse
from app.game_logic.game_defaults import DEFAULT_FIELD_INIT_PAYLOAD
from app.models import Game, GameEvent, UserGameAssociation

router = APIRouter(tags=["game"])


def _pick_player_color(existing_hex_colors: list[str]) -> str:
    existing_rgb = [(1.0, 1.0, 1.0), (0, 0, 0)] + [
        hex_to_rgb(c) for c in existing_hex_colors
    ]
    r, g, b = distinctipy.get_colors(1, existing_rgb, pastel_factor=0)[0]
    return rgb_to_hex(r, g, b)


def _game_to_public(
    game: Game,
    assoc: UserGameAssociation,
    started: bool = False,
    current_turn: int = 0,
) -> GamePublic:
    return GamePublic(
        game_id=game.id,
        join_code=game.join_code,
        your_role=assoc.role,
        date_created=game.date_created,
        name=game.name,
        started=started,
        current_turn=current_turn,
    )


@router.get(f"{API_V1_PREFIX}/games")
def get_user_games(session: SessionDep, user: CurrentUserDep) -> UserGamesResponse:
    """
    Return all games for the current user, split into hosted and joined.
    """
    rows = (
        session.query(Game, UserGameAssociation)
        .join(UserGameAssociation, UserGameAssociation.game_id == Game.id)
        .filter(UserGameAssociation.user_id == user.id)
        .all()
    )

    game_ids = [game.id for game, _ in rows]

    turn_map: dict[str, int] = {}
    started_set: set[str] = set()

    if game_ids:
        turn_rows = (
            session.query(GameEvent.game_id, func.max(GameEvent.turn_number))
            .filter(GameEvent.game_id.in_(game_ids))
            .group_by(GameEvent.game_id)
            .all()
        )
        turn_map = {gid: max_turn for gid, max_turn in turn_rows}

        started_rows = (
            session.query(GameEvent.game_id)
            .filter(GameEvent.game_id.in_(game_ids), GameEvent.type == "game_start")
            .distinct()
            .all()
        )
        started_set = {gid for (gid,) in started_rows}

    hosted: list[GamePublic] = []
    joined: list[GamePublic] = []

    for game, assoc in rows:
        (hosted if assoc.role == "host" else joined).append(
            _game_to_public(
                game,
                assoc,
                started=game.id in started_set,
                current_turn=turn_map.get(game.id, 0),
            )
        )

    return UserGamesResponse(hosted=hosted, joined=joined)


@router.get(f"{API_V1_PREFIX}/game/{{game_id}}/basic-info")
def get_game_basic_info(
    game_id: str, session: SessionDep, user: CurrentUserDep
) -> GameDetailResponse:
    """
    Retrieve basic information about a game by its ID, including the current player list.
    """

    game = (
        session.query(Game, UserGameAssociation)
        .join(UserGameAssociation, UserGameAssociation.game_id == Game.id)
        .filter(Game.id == game_id, UserGameAssociation.user_id == user.id)
        .first()
    )

    if not game:
        raise HTTPException(
            status_code=404,
            detail="Game not found.",
        )

    game_data, user_game_assoc = game

    return GameDetailResponse(
        game_id=game_data.id,
        join_code=game_data.join_code,
        your_role=user_game_assoc.role,
        date_created=game_data.date_created,
        name=game_data.name,
        players=get_players(game_id, session).players,
    )


@router.delete(f"{API_V1_PREFIX}/game/{{game_id}}/leave", status_code=204)
def leave_game(game_id: str, session: SessionDep, user: CurrentUserDep) -> Response:
    assoc = (
        session.query(UserGameAssociation)
        .filter(
            UserGameAssociation.game_id == game_id,
            UserGameAssociation.user_id == user.id,
        )
        .first()
    )

    if not assoc:
        raise HTTPException(status_code=404, detail="Game not found.")

    if assoc.role == "host":
        raise HTTPException(
            status_code=403, detail="The host cannot leave. Delete the game instead."
        )

    session.delete(assoc)
    session.commit()

    return Response(status_code=204)


@router.delete(f"{API_V1_PREFIX}/game/{{game_id}}", status_code=204)
def delete_game(game_id: str, session: SessionDep, user: CurrentUserDep) -> Response:
    assoc = (
        session.query(UserGameAssociation)
        .filter(
            UserGameAssociation.game_id == game_id,
            UserGameAssociation.user_id == user.id,
        )
        .first()
    )

    if not assoc:
        raise HTTPException(status_code=404, detail="Game not found.")

    if assoc.role != "host":
        raise HTTPException(status_code=403, detail="Only the host can delete a game.")

    game = session.query(Game).filter(Game.id == game_id).first()
    session.delete(game)
    session.commit()

    return Response(status_code=204)


@router.post(f"{API_V1_PREFIX}/game/create")
def create_game(session: SessionDep, user: CurrentUserDep) -> GamePublic:
    """
    Create a new game.
    """
    for _ in range(5):
        new_game = Game(join_code=str(uuid.uuid4())[:6].upper())
        try:
            session.add(new_game)
            session.flush()
            break
        except IntegrityError:
            session.rollback()
    else:
        raise HTTPException(status_code=500, detail="Could not generate a unique join code")

    new_game_association = UserGameAssociation(
        user_id=user.id,
        game_id=new_game.id,
        role="host",
        color=_pick_player_color([]),
    )
    session.add(new_game_association)

    field_event = GameEvent(
        game_id=new_game.id,
        sequence_number=1,
        turn_number=0,
        user_id=user.id,
        type="field_init",
        payload=DEFAULT_FIELD_INIT_PAYLOAD,
    )
    session.add(field_event)
    session.commit()
    session.refresh(new_game)
    session.refresh(new_game_association)

    return _game_to_public(new_game, new_game_association)


@router.post(f"{API_V1_PREFIX}/game/join/{{join_code}}")
def join_game(join_code: str, session: SessionDep, user: CurrentUserDep) -> GamePublic:
    """
    Join an existing game using a join code.
    """

    game_to_join = session.query(Game).filter(Game.join_code == join_code).first()
    if not game_to_join:
        raise HTTPException(
            status_code=400,
            detail="Invalid join code.",
        )

    existing_association = (
        session.query(UserGameAssociation)
        .filter(
            UserGameAssociation.user_id == user.id,
            UserGameAssociation.game_id == game_to_join.id,
        )
        .first()
    )

    if existing_association:
        return _game_to_public(game_to_join, existing_association)

    game_started = (
        session.query(GameEvent)
        .filter(
            GameEvent.game_id == game_to_join.id,
            GameEvent.type == "game_start",
        )
        .first()
    )
    if game_started:
        raise HTTPException(
            status_code=403,
            detail="game_already_started",
        )

    existing_colors = [
        a.color
        for a in session.query(UserGameAssociation)
        .filter(UserGameAssociation.game_id == game_to_join.id)
        .all()
    ]
    new_game_association = UserGameAssociation(
        user_id=user.id,
        game_id=game_to_join.id,
        role="player",
        color=_pick_player_color(existing_colors),
    )
    session.add(new_game_association)
    session.commit()
    session.refresh(new_game_association)

    return _game_to_public(game_to_join, new_game_association)
