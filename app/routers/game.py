from fastapi import APIRouter, HTTPException, Response

from app.dependencies.db import SessionDep
from app.dependencies.game_logic import get_players
from app.dependencies.static import API_V1_PREFIX
from app.dependencies.user import CurrentUserDep
from app.dto.game import GameDetailResponse, GamePublic, UserGamesResponse
from app.game_logic.game_defaults import DEFAULT_FIELD_INIT_PAYLOAD
from app.models import Game, GameEvent, UserGameAssociation

router = APIRouter(tags=["game"])


def _game_to_public(game: Game, assoc: UserGameAssociation) -> GamePublic:
    return GamePublic(
        game_id=game.id,
        join_code=game.join_code,
        your_role=assoc.role,
        date_created=game.date_created,
        name=game.name,
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

    hosted: list[GamePublic] = []
    joined: list[GamePublic] = []

    for game, assoc in rows:
        (hosted if assoc.role == "host" else joined).append(
            _game_to_public(game, assoc)
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
    new_game = Game()
    session.add(new_game)
    session.flush()

    new_game_association = UserGameAssociation(
        user_id=user.id,
        game_id=new_game.id,
        role="host",
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

    new_game_association = UserGameAssociation(
        user_id=user.id,
        game_id=game_to_join.id,
        role="player",
    )
    session.add(new_game_association)
    session.commit()
    session.refresh(new_game_association)

    return _game_to_public(game_to_join, new_game_association)
