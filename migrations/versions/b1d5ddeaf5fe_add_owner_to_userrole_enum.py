"""add owner to userrole enum

Revision ID: b1d5ddeaf5fe
Revises: f5b1db73e438
Create Date: 2026-07-03 20:20:53.370363

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1d5ddeaf5fe'
down_revision: Union[str, Sequence[str], None] = 'f5b1db73e438'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'OWNER'")


def downgrade() -> None:
    pass
