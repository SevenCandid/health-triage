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
    # Enum updates moved to main.py startup to bypass asyncpg transaction limitations
    pass


def downgrade() -> None:
    pass
