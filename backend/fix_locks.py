import os
from sqlalchemy import create_engine, text
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

db_url = os.environ.get('DATABASE_URL')
engine = create_engine(db_url)
with engine.connect() as conn:
    conn.execute(text("CREATE TABLE IF NOT EXISTS sync_locks (lock_name VARCHAR(255) PRIMARY KEY, process_id INTEGER, acquired_at TIMESTAMP);"))
    conn.commit()
print("✅ Tabela 'sync_locks' recriada e protegida com sucesso!")
