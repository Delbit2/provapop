#!/usr/bin/env python3
"""
Script para forçar sincronização de questões da planilha Google Sheets.
Remove questões que não estão mais na planilha.
"""
import sys
import os

# Adicionar o diretório do backend ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from google_sheets import sync_questions_from_sheets

def main():
    with app.app_context():
        print("=" * 60)
        print("Forçando sincronização de questões...")
        print("=" * 60)
        
        try:
            result = sync_questions_from_sheets()
            
            if result.get('success'):
                print(f"\n✅ Sincronização concluída com sucesso!")
                print(f"   - Adicionadas: {result.get('added', 0)} questões")
                print(f"   - Ignoradas: {result.get('skipped', 0)} questões")
                print(f"   - Removidas: {result.get('removed', 0)} questões")
                print(f"   - Total na planilha: {result.get('total_in_sheet', 0)} questões")
            else:
                print(f"\n❌ Erro na sincronização:")
                print(f"   {result.get('error', 'Erro desconhecido')}")
                sys.exit(1)
                
        except Exception as e:
            print(f"\n❌ Erro ao executar sincronização:")
            print(f"   {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    main()
