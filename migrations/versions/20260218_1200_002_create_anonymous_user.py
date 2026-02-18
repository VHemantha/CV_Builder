"""Create anonymous system user for public CVs

Revision ID: 002
Revises: 001
Create Date: 2026-02-18 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Generate a UUID for the anonymous user
    anonymous_id = str(uuid.uuid4())

    # Insert anonymous system user
    # Note: Using raw SQL that works with both SQLite and PostgreSQL
    op.execute(f"""
        INSERT INTO users (id, google_id, email, display_name, is_active, created_at, last_login)
        VALUES (
            '{anonymous_id}',
            'anonymous-system',
            'anonymous@system.internal',
            'Anonymous User',
            1,
            '{datetime.utcnow().isoformat()}',
            '{datetime.utcnow().isoformat()}'
        )
    """)


def downgrade():
    # Remove the anonymous user
    op.execute("DELETE FROM users WHERE email = 'anonymous@system.internal'")
