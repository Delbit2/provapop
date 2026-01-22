"""add_category_to_questions

Revision ID: 7cda6cd4b83e
Revises: 0461ba7b49d3
Create Date: 2026-01-22 18:26:44.045863

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7cda6cd4b83e'
down_revision = '0461ba7b49d3'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar coluna category à tabela questions
    with op.batch_alter_table('questions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category', sa.String(length=20), nullable=True))


def downgrade():
    # Remover coluna category
    with op.batch_alter_table('questions', schema=None) as batch_op:
        batch_op.drop_column('category')
