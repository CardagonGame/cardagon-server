"""add constraints and indexes

Revision ID: 3e9f1a2b4c5d
Revises: d40e0aa76ee2
Create Date: 2026-05-26 22:27:48.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = '3e9f1a2b4c5d'
down_revision: Union[str, Sequence[str], None] = 'd40e0aa76ee2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        'uq_game_events_game_seq',
        'game_events',
        ['game_id', 'sequence_number'],
    )
    op.create_index('ix_game_events_game_id', 'game_events', ['game_id'])
    op.create_unique_constraint(
        'uq_user_game_associations_user_game',
        'user_game_associations',
        ['user_id', 'game_id'],
    )


def downgrade() -> None:
    op.drop_constraint('uq_user_game_associations_user_game', 'user_game_associations')
    op.drop_index('ix_game_events_game_id', table_name='game_events')
    op.drop_constraint('uq_game_events_game_seq', 'game_events')
