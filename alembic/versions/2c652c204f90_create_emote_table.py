"""create emote table

Revision ID: 2c652c204f90
Revises: 629248b3a825
Create Date: 2025-01-30 00:26:16.972588

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c652c204f90'
down_revision: Union[str, None] = '629248b3a825'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'emotes',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('count', sa.Integer, default=0),
        sa.Column('channel_id', sa.Integer, sa.ForeignKey('channels.id'), nullable=False)
    )
    


def downgrade() -> None:
    op.drop_table('emotes')
