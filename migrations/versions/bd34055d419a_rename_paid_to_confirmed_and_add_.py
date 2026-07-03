"""rename PAID to CONFIRMED and add PREPARING to orderstatus

Revision ID: bd34055d419a
Revises: b1d5ddeaf5fe
Create Date: 2026-07-03 20:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd34055d419a'
down_revision: Union[str, Sequence[str], None] = 'b1d5ddeaf5fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE orderstatus RENAME VALUE 'PAID' TO 'CONFIRMED'")
    op.execute("ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS 'PREPARING'")


def downgrade() -> None:
    op.execute("ALTER TYPE orderstatus RENAME VALUE 'CONFIRMED' TO 'PAID'")
    op.execute("ALTER TYPE orderstatus DROP VALUE IF EXISTS 'PREPARING'")
