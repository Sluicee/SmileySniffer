"""create channels table

Revision ID: 629248b3a825
Revises: 
Create Date: 2025-01-30 00:21:58.650939

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '629248b3a825'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'channels',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(255), unique=True, nullable=False),
    )


def downgrade() -> None:
    op.drop_table('channels')
