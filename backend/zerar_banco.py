from app import app, db
from sqlalchemy import text

with app.app_context():
    print("🚨 Iniciando protocolo de limpeza NUCLEAR (com CASCADE)...")
    
    # Lista de TODAS as tabelas (velhas em inglês e novas em português)
    tabelas = [
        "quiz_attempts", "questions", "users", 
        "tentativas_questoes", "historico_partidas", 
        "usuario_habilidades", "questoes", "gamers", 
        "alembic_version"
    ]
    
    # O comando CASCADE força o apagamento mesmo que haja dependências
    for tabela in tabelas:
        db.session.execute(text(f"DROP TABLE IF EXISTS {tabela} CASCADE;"))
        
    db.session.commit()
    print("✅ Banco de dados completamente limpo e exorcizado!")
