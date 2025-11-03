from fastapi import APIRouter

from app.dependencies.db import SessionDep
from app.dependencies.user import CurrentUserDep
from app.dto.game import GamePublic
from app.models import Game, UserGameAssociation


router = APIRouter(tags=["game"], prefix="/game")


@router.post("/create")
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


@router.post("/join/{join_code}")
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
