from fastapi import APIRouter, HTTPException, Query, WebSocket

from app.dependencies.db import SessionDep
from app.dependencies.game_logic import run_game_websocket
from app.dependencies.static import API_V1_PREFIX
from app.dependencies.user import get_current_user
from app.models import UserGameAssociation

router = APIRouter(tags=["game_router"])


@router.websocket(f"{API_V1_PREFIX}/game/{{game_id}}/ws")
async def game_websocket_endpoint(
    websocket: WebSocket,
    game_id: str,
    session: SessionDep,
    token: str = Query(...),
):
    try:
        user = get_current_user(session=session, token=token)
    except HTTPException:
        await websocket.close(code=4003)
        return

    association = (
        session.query(UserGameAssociation)
        .filter(
            UserGameAssociation.user_id == user.id,
            UserGameAssociation.game_id == game_id,
        )
        .first()
    )
    if not association:
        await websocket.close(code=4003)
        return

    await run_game_websocket(websocket, game_id, user, association, session)
