#!/usr/bin/env python3
"""
Script de diagnóstico para verificar a sincronização automática com Google Sheets.
Execute este script para verificar se a configuração está correta e se a sincronização funciona.
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_sync_config():
    """Testa a configuração do Google Sheets"""
    print("=" * 60)
    print("TESTE DE CONFIGURAÇÃO DO GOOGLE SHEETS")
    print("=" * 60)
    
    # Verificar variáveis de ambiente
    sheets_url = os.getenv('GOOGLE_SHEETS_URL')
    credentials_file = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE', 'credentials.json')
    worksheet_name = os.getenv('GOOGLE_SHEETS_WORKSHEET_NAME', 'Ranking')
    
    print(f"\n1. Variáveis de ambiente:")
    print(f"   GOOGLE_SHEETS_URL: {'✓ Configurado' if sheets_url else '✗ NÃO CONFIGURADO'}")
    if sheets_url:
        print(f"      URL: {sheets_url}")
    print(f"   GOOGLE_SHEETS_CREDENTIALS_FILE: {credentials_file}")
    print(f"   GOOGLE_SHEETS_WORKSHEET_NAME: {worksheet_name}")
    
    # Verificar arquivo de credenciais
    print(f"\n2. Arquivo de credenciais:")
    if os.path.exists(credentials_file):
        print(f"   ✓ Arquivo encontrado: {credentials_file}")
    else:
        print(f"   ✗ Arquivo NÃO encontrado: {credentials_file}")
        print(f"     Caminho absoluto: {os.path.abspath(credentials_file)}")
        return False
    
    # Testar importação
    print(f"\n3. Testando importações:")
    try:
        from app import app, db, User
        print("   ✓ app, db, User importados com sucesso")
    except Exception as e:
        print(f"   ✗ Erro ao importar: {e}")
        return False
    
    try:
        from google_sheets import sync_user_to_sheets, get_client, extract_sheet_id
        print("   ✓ google_sheets importado com sucesso")
    except Exception as e:
        print(f"   ✗ Erro ao importar google_sheets: {e}")
        return False
    
    # Testar conexão com Google Sheets
    print(f"\n4. Testando conexão com Google Sheets:")
    try:
        with app.app_context():
            client = get_client()
            sheet_id = extract_sheet_id(sheets_url) if sheets_url else None
            if sheet_id:
                sheet = client.open_by_key(sheet_id)
                print(f"   ✓ Conexão bem-sucedida!")
                print(f"     Planilha: {sheet.title}")
                print(f"     ID: {sheet_id}")
            else:
                print(f"   ✗ Não foi possível extrair o ID da planilha")
                return False
    except Exception as e:
        print(f"   ✗ Erro na conexão: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Testar sincronização de um usuário
    print(f"\n5. Testando sincronização de usuário:")
    try:
        with app.app_context():
            # Pegar o primeiro usuário do banco
            user = User.query.first()
            if user:
                print(f"   Testando com usuário: {user.nickname} (ID: {user.id})")
                result = sync_user_to_sheets(user.id)
                if result.get('success'):
                    print(f"   ✓ Sincronização bem-sucedida!")
                    print(f"     Mensagem: {result.get('message')}")
                else:
                    print(f"   ✗ Sincronização falhou:")
                    print(f"     Erro: {result.get('error')}")
                    return False
            else:
                print(f"   ⚠ Nenhum usuário encontrado no banco de dados")
                print(f"     Registre um usuário primeiro para testar a sincronização")
    except Exception as e:
        print(f"   ✗ Erro na sincronização: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\n" + "=" * 60)
    print("✓ TODOS OS TESTES PASSARAM!")
    print("=" * 60)
    print("\nA sincronização automática deve estar funcionando.")
    print("Quando você registrar um novo usuário, ele deve aparecer automaticamente na planilha.")
    print("\nPara ver os logs em tempo real, execute o servidor Flask com:")
    print("  python3 app.py")
    print("\nOu verifique os logs do servidor para mensagens com [SYNC]")
    
    return True

if __name__ == '__main__':
    success = test_sync_config()
    sys.exit(0 if success else 1)
