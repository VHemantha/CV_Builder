"""Add password authentication support

Revision ID: 003
Revises: 002
Create Date: 2026-02-18 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Make google_id nullable (for non-OAuth users)
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('google_id',
                              existing_type=sa.String(255),
                              nullable=True)

    # Add password_hash column
    op.add_column('users', sa.Column('password_hash', sa.String(255), nullable=True))


def downgrade():
    # Remove password_hash column
    op.drop_column('users', 'password_hash')

    # Make google_id NOT NULL again
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('google_id',
                              existing_type=sa.String(255),
                              nullable=False)
