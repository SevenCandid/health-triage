"""Add ACTIVE to session_status_enum

Revision ID: e09ee8c91559
Revises: 3344566a21b5
Create Date: 2026-07-29 01:14:19.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e09ee8c91559'
down_revision = '3344566a21b5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add ACTIVE to Enum if PostgreSQL
    bind = op.get_bind()
    if bind.engine.name == 'postgresql':
        op.execute("ALTER TYPE session_status_enum ADD VALUE IF NOT EXISTS 'ACTIVE'")


def downgrade() -> None:
    pass
