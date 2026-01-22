#!/usr/bin/env python3
"""
Script para debugar a leitura da planilha e ver todas as linhas, mesmo as inválidas.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from google_sheets import get_client, extract_sheet_id

def main():
    with app.app_context():
        print("=" * 60)
        print("DEBUG DA PLANILHA")
        print("=" * 60)
        
        sheets_url = app.config.get('GOOGLE_SHEETS_URL')
        if not sheets_url:
            print("❌ Google Sheets URL não configurada")
            return
        
        sheet_id = extract_sheet_id(sheets_url)
        if not sheet_id:
            print(f"❌ URL inválida: {sheets_url}")
            return
        
        try:
            client = get_client()
            sheet = client.open_by_key(sheet_id)
            
            try:
                worksheet = sheet.worksheet('Questoes')
            except Exception as e:
                print(f"❌ Erro ao acessar aba 'Questoes': {e}")
                print(f"\nAbas disponíveis:")
                for ws in sheet.worksheets():
                    print(f"  - {ws.title}")
                return
            
            # Ler todas as linhas
            all_rows = worksheet.get_all_values()
            
            print(f"\n📋 Total de linhas na planilha: {len(all_rows)}")
            
            if len(all_rows) < 2:
                print("⚠️  Planilha vazia ou só tem cabeçalho")
                return
            
            # Mostrar cabeçalhos
            headers = [h.strip() for h in all_rows[0]]
            print(f"\n📑 Cabeçalhos encontrados ({len(headers)} colunas):")
            for i, h in enumerate(headers):
                print(f"  {i+1}. {h}")
            
            # Verificar linhas de dados
            print(f"\n📊 Analisando linhas de dados:")
            required_cols = ['ID', 'Autor', 'Titulo', 'Trecho_Letra', 'Enunciado', 'A', 'B', 'C', 'D', 'E', 'Alternativa_Correta', 'Musica_Drive']
            
            valid_count = 0
            invalid_count = 0
            
            for row_idx, row in enumerate(all_rows[1:], start=2):
                if not row or not any(row):  # Linha vazia
                    continue
                
                # Verificar campos obrigatórios
                missing = []
                row_data = {}
                
                for col in required_cols:
                    try:
                        col_idx = headers.index(col)
                        value = row[col_idx].strip() if col_idx < len(row) and row[col_idx] else ''
                        row_data[col] = value
                        if not value:
                            missing.append(col)
                    except ValueError:
                        missing.append(col)
                
                if missing:
                    invalid_count += 1
                    print(f"\n  ❌ Linha {row_idx} - FALTANDO: {', '.join(missing)}")
                    print(f"     ID: {row_data.get('ID', 'N/A')}, Título: {row_data.get('Titulo', 'N/A')}")
                else:
                    valid_count += 1
                    if valid_count <= 5:  # Mostrar apenas as 5 primeiras válidas
                        print(f"\n  ✅ Linha {row_idx} - VÁLIDA")
                        print(f"     ID: {row_data.get('ID')}, Título: {row_data.get('Titulo')}, Autor: {row_data.get('Autor')}")
            
            print(f"\n📈 RESUMO:")
            print(f"   - Linhas válidas: {valid_count}")
            print(f"   - Linhas inválidas (faltando campos): {invalid_count}")
            
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()
