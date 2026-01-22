#!/usr/bin/env python3
"""
Script para verificar questões no banco de dados e na planilha.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Question
from google_sheets import read_questions_from_sheets

def main():
    with app.app_context():
        print("=" * 60)
        print("VERIFICAÇÃO DE QUESTÕES")
        print("=" * 60)
        
        # Verificar questões no banco
        db_instance = app.extensions['sqlalchemy']
        questions_in_db = db_instance.session.query(Question).all()
        questions_with_external_id = db_instance.session.query(Question).filter(Question.external_id.isnot(None)).all()
        
        print(f"\n📊 QUESTÕES NO BANCO DE DADOS:")
        print(f"   - Total: {len(questions_in_db)} questões")
        print(f"   - Com external_id: {len(questions_with_external_id)} questões")
        print(f"   - Sem external_id: {len(questions_in_db) - len(questions_with_external_id)} questões")
        
        if questions_with_external_id:
            print(f"\n   Questões com external_id:")
            for q in questions_with_external_id[:10]:  # Mostrar apenas as 10 primeiras
                print(f"   - ID: {q.id}, External ID: {q.external_id}, Título: {q.song_title}")
            if len(questions_with_external_id) > 10:
                print(f"   ... e mais {len(questions_with_external_id) - 10} questões")
        
        # Verificar questões na planilha
        print(f"\n📋 QUESTÕES NA PLANILHA:")
        try:
            result = read_questions_from_sheets()
            if result.get('success'):
                questions_in_sheet = result.get('questions', [])
                print(f"   - Total encontradas: {len(questions_in_sheet)} questões")
                
                if questions_in_sheet:
                    print(f"\n   Questões na planilha:")
                    sheet_ids = set()
                    for q in questions_in_sheet[:10]:  # Mostrar apenas as 10 primeiras
                        ext_id = q.get('external_id', 'N/A')
                        sheet_ids.add(str(ext_id))
                        print(f"   - External ID: {ext_id}, Título: {q.get('song_title', 'N/A')}")
                    if len(questions_in_sheet) > 10:
                        print(f"   ... e mais {len(questions_in_sheet) - 10} questões")
                    
                    # Comparar
                    print(f"\n🔍 COMPARAÇÃO:")
                    db_ids = {str(q.external_id) for q in questions_with_external_id}
                    missing_in_sheet = db_ids - sheet_ids
                    missing_in_db = sheet_ids - db_ids
                    
                    if missing_in_sheet:
                        print(f"\n   ⚠️  Questões no banco que NÃO estão na planilha (serão removidas):")
                        for ext_id in list(missing_in_sheet)[:10]:
                            q = db_instance.session.query(Question).filter(Question.external_id == ext_id).first()
                            if q:
                                print(f"   - External ID: {ext_id}, Título: {q.song_title}")
                        if len(missing_in_sheet) > 10:
                            print(f"   ... e mais {len(missing_in_sheet) - 10} questões")
                    
                    if missing_in_db:
                        print(f"\n   ➕ Questões na planilha que NÃO estão no banco (serão adicionadas):")
                        for ext_id in list(missing_in_db)[:10]:
                            q_data = next((q for q in questions_in_sheet if str(q.get('external_id')) == ext_id), None)
                            if q_data:
                                print(f"   - External ID: {ext_id}, Título: {q_data.get('song_title', 'N/A')}")
                        if len(missing_in_db) > 10:
                            print(f"   ... e mais {len(missing_in_db) - 10} questões")
                    
                    if not missing_in_sheet and not missing_in_db:
                        print(f"\n   ✅ Banco e planilha estão sincronizados!")
                else:
                    print(f"   ⚠️  Nenhuma questão encontrada na planilha!")
                    print(f"   Verifique se:")
                    print(f"   1. A planilha tem dados")
                    print(f"   2. Todas as colunas obrigatórias estão preenchidas")
                    print(f"   3. O nome da aba está correto: 'Questoes'")
            else:
                print(f"   ❌ Erro ao ler planilha: {result.get('error', 'Erro desconhecido')}")
        except Exception as e:
            print(f"   ❌ Erro ao verificar planilha: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()
