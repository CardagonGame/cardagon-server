from fastapi import WebSocket, WebSocketDisconnect
from pydantic_core import from_json
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.dto.game_logic import UserConnection
from app.dto.game_responses import (
    GameState,
    PlayerInfo,
    PlayersMessage,
    StartPosition,
    WsPlayerInfo,
    WsPlayersMessage,
)
from app.game_logic.board import generate_start_positions
from app.dto.user import UserPublic
from app.models import GameEvent, User, UserGameAssociation


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[UserConnection] = []

    async def connect(self, user_connection: UserConnection):
        await user_connection.websocket.accept()
        self.active_connections.append(user_connection)

    def disconnect(self, user_connection: UserConnection):
        self.active_connections.remove(user_connection)

    async def send_personal_message(self, message: str, user_connection: UserConnection):
        try:
            await user_connection.websocket.send_text(message)
        except RuntimeError:
            self.active_connections.remove(user_connection)

    async def broadcast(self, game_id: str, message: str):
        dead = []
        for connection in self.active_connections:
            if connection.game_id == game_id:
                try:
                    await connection.websocket.send_text(message)
                except RuntimeError:
                    dead.append(connection)
        for connection in dead:
            if connection in self.active_connections:
                self.active_connections.remove(connection)


manager = ConnectionManager()


def _fetch_player_rows(game_id: str, session: Session):
    return (
        session.query(User, UserGameAssociation)
        .join(UserGameAssociation, UserGameAssociation.user_id == User.id)
        .filter(UserGameAssociation.game_id == game_id)
        .all()
    )


def get_players(game_id: str, session: Session) -> PlayersMessage:
    rows = _fetch_player_rows(game_id, session)
    online_ids = {c.user_id for c in manager.active_connections if c.game_id == game_id}
    return PlayersMessage(
        players=[
            PlayerInfo(
                user_id=user.id,
                username=user.username,
                role=assoc.role,
                online=user.id in online_ids,
                color=assoc.color,
            )
            for user, assoc in rows
        ]
    )


def get_ws_players(game_id: str, session: Session) -> WsPlayersMessage:
    rows = _fetch_player_rows(game_id, session)
    conns = {c.user_id: c for c in manager.active_connections if c.game_id == game_id}
    return WsPlayersMessage(
        players=[
            WsPlayerInfo(
                user_id=user.id,
                username=user.username,
                role=assoc.role,
                online=user.id in conns,
                ping_ms=conns[user.id].ping_ms if user.id in conns else None,
                color=assoc.color,
            )
            for user, assoc in rows
        ]
    )


def build_game_state(events: list[GameEvent]) -> GameState:
    state = GameState()
    for event in events:
        match event.type:
            case "game_start":
                state.started = True
            case "field_init":
                state.field_size = event.payload.get("field_size")
            case "player_start_position":
                if event.user_id is not None:
                    state.start_positions.append(
                        StartPosition(
                            user_id=event.user_id,
                            q=event.payload["q"],
                            r=event.payload["r"],
                            s=event.payload["s"],
                        )
                    )
    return state


async def run_game_websocket(
    websocket: WebSocket,
    game_id: str,
    user: UserPublic,
    association: UserGameAssociation,
    session: Session,
):
    user_connection = UserConnection(
        user_id=user.id,
        game_id=game_id,
        websocket=websocket,
    )
    await manager.connect(user_connection)
    events = (
        session.query(GameEvent)
        .filter(GameEvent.game_id == game_id)
        .order_by(GameEvent.sequence_number)
        .all()
    )
    await manager.send_personal_message(
        build_game_state(events).model_dump_json(), user_connection
    )
    await manager.broadcast(game_id, get_ws_players(game_id, session).model_dump_json())
    try:
        while True:
            data = await websocket.receive_text()
            parsed_data = from_json(data)
            match parsed_data.get("type"):
                case "ping":
                    await manager.send_personal_message(
                        '{"type":"pong"}',
                        user_connection,
                    )
                case "ping_result":
                    ms = parsed_data.get("ms")
                    if isinstance(ms, int):
                        user_connection.ping_ms = ms
                        await manager.broadcast(
                            game_id, get_ws_players(game_id, session).model_dump_json()
                        )
                case "ready":
                    await manager.send_personal_message(
                        "You are ready!",
                        user_connection,
                    )
                case "game_start":
                    if association.role != "host":
                        await manager.send_personal_message(
                            '{"type":"error","message":"only the host can start the game"}',
                            user_connection,
                        )
                        continue
                    already_started = (
                        session.query(GameEvent)
                        .filter(
                            GameEvent.game_id == game_id,
                            GameEvent.type == "game_start",
                        )
                        .first()
                    )
                    if already_started:
                        await manager.send_personal_message(
                            '{"type":"error","message":"game already started"}',
                            user_connection,
                        )
                        continue
                    field_init_event = (
                        session.query(GameEvent)
                        .filter(
                            GameEvent.game_id == game_id,
                            GameEvent.type == "field_init",
                        )
                        .first()
                    )
                    field_size = (
                        field_init_event.payload.get("field_size", 5)
                        if field_init_event
                        else 5
                    )
                    player_rows = _fetch_player_rows(game_id, session)
                    player_ids = [
                        game_association.user_id
                        for _, game_association in player_rows
                    ]
                    try:
                        positions = generate_start_positions(field_size, len(player_ids))
                    except ValueError as exc:
                        await manager.send_personal_message(
                            f'{{"type":"error","message":"{exc}"}}',
                            user_connection,
                        )
                        continue
                    last_seq = (
                        session.query(func.max(GameEvent.sequence_number))
                        .filter(GameEvent.game_id == game_id)
                        .scalar()
                    ) or 0
                    session.add(
                        GameEvent(
                            game_id=game_id,
                            sequence_number=last_seq + 1,
                            turn_number=0,
                            user_id=user.id,
                            type="game_start",
                        )
                    )
                    for seq_offset, (player_id, (q, r, s)) in enumerate(
                        zip(player_ids, positions), start=2
                    ):
                        session.add(
                            GameEvent(
                                game_id=game_id,
                                sequence_number=last_seq + seq_offset,
                                turn_number=0,
                                user_id=player_id,
                                type="player_start_position",
                                payload={"q": q, "r": r, "s": s},
                            )
                        )
                    session.commit()
                    await manager.broadcast(game_id, '{"type":"game_start"}')
    except WebSocketDisconnect:
        manager.disconnect(user_connection)
        await manager.broadcast(
            game_id,
            get_ws_players(game_id, session).model_dump_json(),
        )
