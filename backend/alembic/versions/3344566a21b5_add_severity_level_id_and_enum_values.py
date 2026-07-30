"""Add severity_level_id and enum values

Revision ID: 3344566a21b5
Revises: 3fc59d9f5a0a
Create Date: 2026-07-29 00:54:53.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3344566a21b5'
down_revision = '3fc59d9f5a0a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    has_column = False
    
    # Check if column already exists
    if 'assessment_sessions' in inspector.get_table_names():
        for col in inspector.get_columns('assessment_sessions'):
            if col['name'] == 'severity_level_id':
                has_column = True
                break
                
    if not has_column:
        # Add severity_level_id column
        with op.batch_alter_table('assessment_sessions', schema=None) as batch_op:
            batch_op.add_column(sa.Column('severity_level_id', sa.String(length=36), nullable=True, comment='Final severity level assigned to this session.'))
            batch_op.create_foreign_key('fk_assessment_sessions_severity_id', 'severity_levels', ['severity_level_id'], ['id'], ondelete='SET NULL')
            batch_op.create_index(batch_op.f('ix_assessment_sessions_severity_level_id'), ['severity_level_id'], unique=False)

    # Enum updates moved to main.py startup to bypass asyncpg transaction limitations
    pass


def downgrade() -> None:
    with op.batch_alter_table('assessment_sessions', schema=None) as batch_op:
        batch_op.drop_constraint('fk_assessment_sessions_severity_id', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_assessment_sessions_severity_level_id'))
        batch_op.drop_column('severity_level_id')
