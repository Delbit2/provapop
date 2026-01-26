"""create_sync_locks_table

Revision ID: create_sync_locks
Revises: 7cda6cd4b83e
Create Date: 2026-01-26 22:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'create_sync_locks'
down_revision = '7cda6cd4b83e'
branch_labels = None
depends_on = None


def upgrade():
    # Criar tabela sync_locks apenas se não existir
    # Usar uma abordagem que funciona tanto no SQLite quanto no PostgreSQL
    connection = op.get_bind()
    
    # Verificar se a tabela já existe
    if connection.dialect.name == 'postgresql':
        result = connection.execute(sa.text(
            """SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'sync_locks'
            )"""
        )).scalar()
        
        if not result:
            op.create_table(
                'sync_locks',
                sa.Column('lock_name', sa.String(100), primary_key=True),
                sa.Column('acquired_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
                sa.Column('process_id', sa.Integer()),
            )
    else:
        # Para SQLite, usar try/except
        try:
            op.create_table(
                'sync_locks',
                sa.Column('lock_name', sa.String(100), primary_key=True),
                sa.Column('acquired_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
                sa.Column('process_id', sa.Integer()),
            )
        except Exception:
            # Tabela já existe, ignorar
            pass


def downgrade():
    op.drop_table('sync_locks')
