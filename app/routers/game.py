from fastapi import APIRouter, WebSocket

from app.dependencies.db import SessionDep
from app.dependencies.static import API_V1_PREFIX
from app.dependencies.user import CurrentUserDep
from app.dto.game import GamePublic
from app.models import Game, UserGameAssociation


router = APIRouter(tags=["game"])


@router.get(f"{API_V1_PREFIX}/game/{{game_id}}/basic-info")
def get_game_basic_info(game_id: str, session: SessionDep) -> GamePublic:
    """
    Retrieve basic information about a game by its ID.
    """

    game = (
        session.query(Game, UserGameAssociation)
        .filter(Game.id == game_id)
        .join(UserGameAssociation, UserGameAssociation.game_id == Game.id)
        .first()
    )

    if not game:
        return {"error": "Game not found."}

    game_data, user_game_assoc = game

    return GamePublic(
        game_id=game_data.id,
        join_code=game_data.join_code,
        your_role=user_game_assoc.role,
    )


@router.post(f"{API_V1_PREFIX}/game/create")
def create_game(session: SessionDep, user: CurrentUserDep) -> GamePublic:
    """
    Create a new game.
    """
    new_game = Game()

    session.add(new_game)
    session.commit()
    session.refresh(new_game)

    new_game_association = UserGameAssociation(
        user_id=user.id,
        game_id=new_game.id,
        role="host",
    )
    session.add(new_game_association)
    session.commit()
    session.refresh(new_game_association)

    return GamePublic(
        game_id=new_game.id,
        join_code=new_game.join_code,
        your_role=new_game_association.role,
    )


@router.post(f"{API_V1_PREFIX}/game/join/{{join_code}}")
def join_game(join_code: str, session: SessionDep, user: CurrentUserDep) -> GamePublic:
    """
    Join an existing game using a join code.
    """

    game_to_join = session.query(Game).filter(Game.join_code == join_code).first()
    if not game_to_join:
        return {"error": "Game not found."}
    existing_association = (
        session.query(UserGameAssociation)
        .filter(
            UserGameAssociation.user_id == user.id,
            UserGameAssociation.game_id == game_to_join.id,
        )
        .first()
    )

    if existing_association:
        return GamePublic(
            game_id=game_to_join.id,
            join_code=game_to_join.join_code,
            your_role=existing_association.role,
        )

    new_game_association = UserGameAssociation(
        user_id=user.id,
        game_id=game_to_join.id,
        role="player",
    )
    session.add(new_game_association)
    session.commit()
    session.refresh(new_game_association)

    return GamePublic(
        game_id=game_to_join.id,
        join_code=game_to_join.join_code,
        your_role=new_game_association.role,
    )
