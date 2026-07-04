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
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        # RENAME VALUE is allowed inside a transaction.
        op.execute("ALTER TYPE orderstatus RENAME VALUE 'PAID' TO 'CONFIRMED'")
        # ADD VALUE cannot run inside a transaction block on PostgreSQL, so
        # commit the current transaction, run the DDL, and begin a new one.
        op.execute("COMMIT")
        op.execute("ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS 'PREPARING'")
        op.execute("BEGIN")
    # On other dialects (e.g. SQLite) the enum is stored differently and
    # these statements are no-ops.


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        # PostgreSQL does not support DROP VALUE on an enum; RENAME back only.
        op.execute("ALTER TYPE orderstatus RENAME VALUE 'CONFIRMED' TO 'PAID'")
