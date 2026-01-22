#!/usr/bin/env python3
"""
Script para remover questões mock e sincronizar com a planilha Google Sheets.
"""

from app import app, db, Question
from google_sheets import sync_questions_from_sheets

def clean_mock_questions():
    """
    Remove todas as questões que não têm external_id (questões mock/demo).
    """
    with app.app_context():
        # Buscar questões sem external_id
        mock_questions = Question.query.filter(Question.external_id.is_(None)).all()
        
        if not mock_questions:
            print("Nenhuma questão mock encontrada.")
            return 0
        
        count = len(mock_questions)
        print(f"Encontradas {count} questão(ões) mock para remover:")
        
        for q in mock_questions:
            print(f"  - {q.song_title} por {q.artist} (ID: {q.id})")
        
        # Remover questões mock
        for q in mock_questions:
            db.session.delete(q)
        
        db.session.commit()
        print(f"\n✓ {count} questão(ões) mock removida(s) com sucesso!")
        return count

def sync_questions():
    """
    Sincroniza questões da planilha Google Sheets.
    """
    with app.app_context():
        print("\n" + "="*50)
        print("Iniciando sincronização com Google Sheets...")
        print("="*50)
        
        try:
            result = sync_questions_from_sheets()
            
            if result.get('success'):
                added = result.get('added', 0)
                skipped = result.get('skipped', 0)
                print(f"\n✓ Sincronização concluída!")
                print(f"  - {added} questão(ões) adicionada(s)")
                print(f"  - {skipped} questão(ões) ignorada(s) (já existentes)")
                
                # Listar questões sincronizadas
                if added > 0:
                    print("\nQuestões sincronizadas:")
                    questions = Question.query.filter(Question.external_id.isnot(None)).order_by(Question.id.desc()).limit(added).all()
                    for q in questions:
                        print(f"  - {q.song_title} por {q.artist} (ID externo: {q.external_id})")
            else:
                error = result.get('error', 'Erro desconhecido')
                print(f"\n✗ Erro na sincronização: {error}")
                return False
                
        except Exception as e:
            print(f"\n✗ Erro ao sincronizar: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        return True

def main():
    """
    Executa a limpeza de questões mock e a sincronização.
    """
    print("="*50)
    print("Limpeza e Sincronização de Questões")
    print("="*50)
    
    # Passo 1: Remover questões mock
    print("\n[1/2] Removendo questões mock...")
    clean_mock_questions()
    
    # Passo 2: Sincronizar com a planilha
    print("\n[2/2] Sincronizando com Google Sheets...")
    sync_questions()
    
    # Resumo final
    with app.app_context():
        total_questions = Question.query.count()
        synced_questions = Question.query.filter(Question.external_id.isnot(None)).count()
        
        print("\n" + "="*50)
        print("Resumo Final")
        print("="*50)
        print(f"Total de questões no banco: {total_questions}")
        print(f"Questões sincronizadas (com external_id): {synced_questions}")
        print("="*50)

if __name__ == '__main__':
    main()
