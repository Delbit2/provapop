"""add_new_question_fields

Revision ID: 0461ba7b49d3
Revises: 4677fc257233
Create Date: 2026-01-22 18:09:47.593785

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0461ba7b49d3'
down_revision = '4677fc257233'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar novas colunas à tabela questions
    with op.batch_alter_table('questions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('composition_year', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('enem_year', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('comment', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('curiosity', sa.Text(), nullable=True))


def downgrade():
    # Remover as colunas adicionadas
    with op.batch_alter_table('questions', schema=None) as batch_op:
        batch_op.drop_column('curiosity')
        batch_op.drop_column('comment')
        batch_op.drop_column('enem_year')
        batch_op.drop_column('composition_year')
