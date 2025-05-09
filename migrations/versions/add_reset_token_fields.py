"""Add reset token fields to User table

Revision ID: add_reset_token_fields
"""

import sqlalchemy as sa
from alembic import op


def upgrade():
    # Add reset_token and reset_token_expiry columns to User table
    op.add_column('user', sa.Column('reset_token', sa.String(length=100), nullable=True))
    op.add_column('user', sa.Column('reset_token_expiry', sa.DateTime(), nullable=True))


def downgrade():
    # Drop the reset_token and reset_token_expiry columns
    op.drop_column('user', 'reset_token_expiry')
    op.drop_column('user', 'reset_token')