"""add supabase_user_id to gamers

Revision ID: 9340fe6969f9
Revises: 
Create Date: 2026-04-23 15:53:02.303560

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9340fe6969f9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('gamers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('supabase_user_id', sa.String(length=36), nullable=True))
        batch_op.create_index(
            batch_op.f('ix_gamers_supabase_user_id'),
            ['supabase_user_id'],
            unique=True
        )


def downgrade():
    with op.batch_alter_table('gamers', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_gamers_supabase_user_id'))
        batch_op.drop_column('supabase_user_id')
