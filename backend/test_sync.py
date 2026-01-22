#!/usr/bin/env python3
"""
Script para testar a sincronização com Google Sheets manualmente.
Execute este script para diagnosticar problemas de sincronização.
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_sync():
    print("🧪 Testando sincronização com Google Sheets...\n")
    
    try:
        from app import app, db, User
        from google_sheets import sync_user_to_sheets, sync_ranking_to_sheets
        
        with app.app_context():
            # Verificar configuração
            print("1️⃣ Verificando configuração...")
            sheets_url = app.config.get('GOOGLE_SHEETS_URL')
            if not sheets_url:
                print("❌ GOOGLE_SHEETS_URL não configurado no .env")
                return False
            print(f"   ✅ GOOGLE_SHEETS_URL: {sheets_url}")
            
            credentials_file = app.config.get('GOOGLE_SHEETS_CREDENTIALS_FILE', 'credentials.json')
            if not os.path.exists(credentials_file):
                print(f"❌ Arquivo de credenciais não encontrado: {credentials_file}")
                return False
            print(f"   ✅ Credentials file: {credentials_file}")
            
            worksheet_name = app.config.get('GOOGLE_SHEETS_WORKSHEET_NAME', 'Ranking')
            print(f"   ✅ Worksheet name: {worksheet_name}\n")
            
            # Testar conexão básica
            print("2️⃣ Testando conexão com Google Sheets...")
            try:
                from google_sheets import get_client, extract_sheet_id
                sheet_id = extract_sheet_id(sheets_url)
                client = get_client()
                sheet = client.open_by_key(sheet_id)
                print(f"   ✅ Conectado à planilha: {sheet.title}")
                print(f"   ✅ Sheet ID: {sheet_id}\n")
            except Exception as e:
                print(f"   ❌ Erro ao conectar: {e}")
                return False
            
            # Listar usuários
            print("3️⃣ Usuários no banco de dados:")
            users = User.query.all()
            if not users:
                print("   ⚠️  Nenhum usuário encontrado no banco de dados")
                print("   💡 Crie um usuário primeiro através do frontend\n")
                return False
            
            for user in users:
                print(f"   - ID: {user.id}, Nickname: {user.nickname}, Email: {user.email}")
            print()
            
            # Testar sincronização de um usuário
            print("4️⃣ Testando sincronização de um usuário...")
            test_user = users[0]
            print(f"   Testando com usuário: {test_user.nickname} (ID: {test_user.id})")
            
            result = sync_user_to_sheets(test_user.id)
            if result['success']:
                print(f"   ✅ {result['message']}")
            else:
                print(f"   ❌ Erro: {result['error']}")
                return False
            print()
            
            # Testar sincronização completa do ranking
            print("5️⃣ Testando sincronização completa do ranking...")
            result = sync_ranking_to_sheets()
            if result['success']:
                print(f"   ✅ {result['message']}")
            else:
                print(f"   ❌ Erro: {result['error']}")
                return False
            print()
            
            print("✅ Todos os testes passaram!")
            print("\n💡 Verifique sua planilha do Google Sheets agora.")
            return True
            
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("   Certifique-se de estar na pasta backend/ e que todas as dependências estão instaladas")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_sync()
    sys.exit(0 if success else 1)
