"""add owner role to userrole enum

Revision ID: add_owner_role
Revises: d83a7660e7b3
Create Date: 2026-06-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_owner_role'
down_revision: Union[str, Sequence[str], None] = 'd83a7660e7b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE userrole ADD VALUE 'OWNER'")


def downgrade() -> None:
    """Downgrade schema."""
    # PostgreSQL does not support removing enum values directly.
    # To downgrade, you would need to recreate the enum type.
    pass
