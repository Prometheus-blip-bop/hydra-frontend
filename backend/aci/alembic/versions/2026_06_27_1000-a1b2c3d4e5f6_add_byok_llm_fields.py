"""add byok llm fields

Revision ID: a1b2c3d4e5f6
Revises: 48bf142a794c
Create Date: 2026-06-27 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '48bf142a794c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('projects', sa.Column('llm_api_key', sa.String(), nullable=True))
    op.add_column('projects', sa.Column('llm_base_url', sa.String(), nullable=True))
    op.add_column('projects', sa.Column('llm_model', sa.String(), nullable=True))
    op.add_column('projects', sa.Column('message_count', sa.Integer(), server_default='0', nullable=False))


def downgrade() -> None:
    op.drop_column('projects', 'message_count')
    op.drop_column('projects', 'llm_model')
    op.drop_column('projects', 'llm_base_url')
    op.drop_column('projects', 'llm_api_key')
