"""create desktop table

Revision ID: 6f01aefa2e00
Revises: 
Create Date: 2024-07-13 15:17:58.872091

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f01aefa2e00'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('desktop',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
        sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
        sa.Column('occupied', sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name='desktop_pkey')
    )


def downgrade() -> None:
    op.drop_table('desktop')
