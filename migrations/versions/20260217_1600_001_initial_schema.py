"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-02-17 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('google_id', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=True),
        sa.Column('photo_url', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('google_id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_google_id'), 'users', ['google_id'], unique=True)

    # Create cvs table
    op.create_table(
        'cvs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('template_slug', sa.String(length=50), nullable=False, server_default='ats_clean'),
        sa.Column('primary_color', sa.String(length=7), nullable=True),
        sa.Column('font_pair', sa.String(length=50), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cvs_user_id'), 'cvs', ['user_id'], unique=False)

    # Create cv_sections table
    op.create_table(
        'cv_sections',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('cv_id', sa.String(length=36), nullable=False),
        sa.Column('section_type', sa.String(length=50), nullable=False),
        sa.Column('label', sa.String(length=255), nullable=True),
        sa.Column('content', sa.JSON(), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_visible', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['cv_id'], ['cvs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cv_sections_cv_id'), 'cv_sections', ['cv_id'], unique=False)

    # Create download_logs table
    op.create_table(
        'download_logs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('cv_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('ip_hash', sa.String(length=64), nullable=False),
        sa.Column('cv_title', sa.String(length=255), nullable=False),
        sa.Column('downloaded_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['cv_id'], ['cvs.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_download_logs_downloaded_at'), 'download_logs', ['downloaded_at'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_download_logs_downloaded_at'), table_name='download_logs')
    op.drop_table('download_logs')
    op.drop_index(op.f('ix_cv_sections_cv_id'), table_name='cv_sections')
    op.drop_table('cv_sections')
    op.drop_index(op.f('ix_cvs_user_id'), table_name='cvs')
    op.drop_table('cvs')
    op.drop_index(op.f('ix_users_google_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
