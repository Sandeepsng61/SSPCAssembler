"""Add extended shipping fields to Order table

Revision ID: add_order_address_fields
"""

from alembic import op
import sqlalchemy as sa


def upgrade():
    # Add new columns to the Order table
    op.add_column('order', sa.Column('shipping_locality', sa.String(100), nullable=True))
    op.add_column('order', sa.Column('shipping_landmark', sa.String(100), nullable=True))
    op.add_column('order', sa.Column('alt_phone', sa.String(20), nullable=True))
    op.add_column('order', sa.Column('address_type', sa.String(20), server_default='home', nullable=False))


def downgrade():
    # Remove the columns if needed to rollback
    op.drop_column('order', 'shipping_locality')
    op.drop_column('order', 'shipping_landmark')
    op.drop_column('order', 'alt_phone')
    op.drop_column('order', 'address_type')