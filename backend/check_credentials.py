#!/usr/bin/env python3
"""
Script para verificar se o arquivo credentials.json existe e está configurado corretamente.
"""

import os
import json
import sys

def check_credentials():
    credentials_file = 'credentials.json'
    
    print("🔍 Verificando arquivo credentials.json...\n")
    
    # Verificar se o arquivo existe
    if not os.path.exists(credentials_file):
        print("❌ Arquivo credentials.json NÃO encontrado!")
        print("\n📋 Para obter o arquivo:")
        print("   1. Acesse: https://console.cloud.google.com/")
        print("   2. Crie uma Service Account")
        print("   3. Baixe as credenciais em formato JSON")
        print("   4. Renomeie para 'credentials.json' e coloque nesta pasta")
        print("\n📖 Veja o arquivo COMO_OBTER_CREDENTIALS.md para instruções detalhadas")
        return False
    
    print("✅ Arquivo credentials.json encontrado!")
    
    # Verificar se é um JSON válido
    try:
        with open(credentials_file, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print("❌ Arquivo credentials.json não é um JSON válido!")
        return False
    
    print("✅ Arquivo é um JSON válido")
    
    # Verificar campos obrigatórios
    required_fields = [
        'type',
        'project_id',
        'private_key',
        'client_email',
        'client_id'
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ Campos obrigatórios faltando: {', '.join(missing_fields)}")
        return False
    
    print("✅ Todos os campos obrigatórios estão presentes")
    
    # Verificar tipo
    if data.get('type') != 'service_account':
        print("⚠️  Campo 'type' não é 'service_account'")
        return False
    
    print("✅ Tipo de credencial correto (service_account)")
    
    # Verificar se não são valores de placeholder
    placeholder_values = ['SUBSTITUA', 'SEU', 'SUA']
    has_placeholder = False
    
    for key, value in data.items():
        if isinstance(value, str):
            for placeholder in placeholder_values:
                if placeholder in value.upper():
                    has_placeholder = True
                    print(f"⚠️  Campo '{key}' contém valores de placeholder!")
                    break
    
    if has_placeholder:
        print("\n⚠️  ATENÇÃO: O arquivo contém valores de placeholder!")
        print("   Você precisa substituir pelos valores reais do Google Cloud Console")
        return False
    
    print("\n✅ Arquivo credentials.json está configurado corretamente!")
    print(f"   📧 Service Account Email: {data.get('client_email')}")
    print(f"   🆔 Project ID: {data.get('project_id')}")
    
    # Tentar testar a conexão (opcional)
    try:
        from google_sheets import get_client
        client = get_client()
        print("\n✅ Conexão com Google Sheets API testada com sucesso!")
    except Exception as e:
        print(f"\n⚠️  Não foi possível testar a conexão: {e}")
        print("   Isso pode ser normal se as APIs não estiverem ativadas ainda")
    
    return True

if __name__ == '__main__':
    success = check_credentials()
    sys.exit(0 if success else 1)
