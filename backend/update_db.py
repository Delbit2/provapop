from app import db, app
from sqlalchemy import text

with app.app_context():
    queries = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS total_play_time INTEGER DEFAULT 0;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS current_streak INTEGER DEFAULT 0;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_play_date DATE;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token VARCHAR(255);",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token_expiry TIMESTAMP;"
    ]
    with db.engine.connect() as conn:
        for q in queries:
            try:
                conn.execute(text(q))
                conn.commit()
                print(f"Sucesso: {q}")
            except Exception as e:
                print(f"Erro ao executar {q}: {e}")
    print("Atualização da tabela users concluída com sucesso!")
