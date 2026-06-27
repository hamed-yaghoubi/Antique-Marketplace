"""add admin fields to users and products

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-27 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add role column to users table
    user_role_enum = sa.Enum('user', 'admin', name='userrole')
    user_role_enum.create(op.get_bind(), checkfirst=True)
    op.add_column('users', sa.Column('role', user_role_enum, nullable=False, server_default='user'))

    # Add sku and is_active columns to products table
    op.add_column('products', sa.Column('sku', sa.String(length=100), nullable=False, server_default='SKU-DEFAULT'))
    op.add_column('products', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))

    # Add indexes for performance
    op.create_index(op.f('ix_products_sku'), 'products', ['sku'], unique=True)
    op.create_index(op.f('ix_products_price'), 'products', ['price'], unique=False)
    op.create_index(op.f('ix_products_category'), 'products', ['category'], unique=False)
    op.create_index(op.f('ix_products_seller_id'), 'products', ['seller_id'], unique=False)
    op.create_index(op.f('ix_products_is_active'), 'products', ['is_active'], unique=False)
    op.create_index(op.f('ix_products_created_at'), 'products', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index(op.f('ix_products_created_at'), table_name='products')
    op.drop_index(op.f('ix_products_is_active'), table_name='products')
    op.drop_index(op.f('ix_products_seller_id'), table_name='products')
    op.drop_index(op.f('ix_products_category'), table_name='products')
    op.drop_index(op.f('ix_products_price'), table_name='products')
    op.drop_index(op.f('ix_products_sku'), table_name='products')

    # Drop columns
    op.drop_column('products', 'is_active')
    op.drop_column('products', 'sku')
    op.drop_column('users', 'role')

    # Drop enum
    sa.Enum(name='userrole').drop(op.get_bind(), checkfirst=True)
