"""update order status enum and add updated_at column

Revision ID: a1b2c3d4e5f6
Revises: d83a7660e7b3
Create Date: 2026-07-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'd83a7660e7b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add updated_at column
    op.add_column('orders', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))

    # Update enum: rename PAID -> CONFIRMED, add PREPARING
    # For PostgreSQL: alter the enum type
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect == 'postgresql':
        # Rename old enum value and add new one
        op.execute("ALTER TYPE orderstatus RENAME VALUE 'PAID' TO 'CONFIRMED'")
        op.execute("ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS 'PREPARING'")


def downgrade() -> None:
    # Remove updated_at column
    op.drop_column('orders', 'updated_at')

    # Revert enum changes
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect == 'postgresql':
        op.execute("ALTER TYPE orderstatus RENAME VALUE 'CONFIRMED' TO 'PAID'")
        op.execute("ALTER TYPE orderstatus DROP VALUE IF EXISTS 'PREPARING'")
