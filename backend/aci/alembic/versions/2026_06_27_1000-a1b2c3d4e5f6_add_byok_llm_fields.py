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
    import sqlalchemy.exc
    columns = [
        ('llm_api_key', sa.String(), True, None),
        ('llm_base_url', sa.String(), True, None),
        ('llm_model', sa.String(), True, None),
        ('message_count', sa.Integer(), False, '0')
    ]
    
    for col_name, col_type, nullable, server_default in columns:
        try:
            if server_default:
                op.add_column('projects', sa.Column(col_name, col_type, nullable=nullable, server_default=server_default))
            else:
                op.add_column('projects', sa.Column(col_name, col_type, nullable=nullable))
        except sqlalchemy.exc.OperationalError as e:
            if 'duplicate column name' in str(e).lower():
                pass
            else:
                raise


def downgrade() -> None:
    op.drop_column('projects', 'message_count')
    op.drop_column('projects', 'llm_model')
    op.drop_column('projects', 'llm_base_url')
    op.drop_column('projects', 'llm_api_key')
