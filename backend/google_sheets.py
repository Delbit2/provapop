import gspread
import gspread.exceptions
from google.oauth2.service_account import Credentials
import re
import os
import time
import threading
from datetime import datetime
from flask import current_app
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

def process_drive_url(url):
    """
    Processa um link do Google Drive e converte para um link direto utilizável.
    Suporta vários formatos de links do Drive e retorna um link que pode ser usado
    diretamente em players de áudio HTML5.
    
    Formatos suportados:
    - https://drive.google.com/file/d/FILE_ID/view
    - https://drive.google.com/file/d/FILE_ID/edit
    - https://drive.google.com/open?id=FILE_ID
    - https://drive.google.com/drive/folders/FILE_ID (não suportado - retorna None)
    
    Para streaming de áudio, usa o formato uc?export=download que funciona melhor
    com players HTML5 quando o arquivo está compartilhado publicamente.
    """
    if not url or not url.strip():
        return None
    
    url = url.strip()
    
    # Padrões de links do Google Drive
    patterns = [
        r'/file/d/([a-zA-Z0-9_-]+)',  # /file/d/FILE_ID/view ou /file/d/FILE_ID/edit
        r'[?&]id=([a-zA-Z0-9_-]+)',  # ?id=FILE_ID ou &id=FILE_ID
    ]
    
    file_id = None
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            file_id = match.group(1)
            break
    
    if not file_id:
        # Se não conseguir extrair o ID, retornar o link original
        # Pode ser um link já processado ou em formato desconhecido
        return url
    
    # Converter para link direto do Google Drive para streaming de áudio
    # Usar 'export=download' que funciona melhor para streaming quando o arquivo
    # está compartilhado publicamente (qualquer pessoa com o link pode visualizar)
    direct_url = f'https://drive.google.com/uc?export=download&id={file_id}'
    return direct_url

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file"
]

def extract_sheet_id(url):
    pattern = r'/spreadsheets/d/([a-zA-Z0-9-_]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def get_client():
    from flask import current_app
    app = current_app
    credentials_file = app.config.get('GOOGLE_SHEETS_CREDENTIALS_FILE', 'credentials.json')
    
    if not os.path.exists(credentials_file):
        raise FileNotFoundError(
            f"Credentials file not found: {credentials_file}\n"
            "Please download your service account credentials from Google Cloud Console"
        )
    
    creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPE)
    return gspread.authorize(creds)

def get_or_create_worksheet(sheet, worksheet_name):
    try:
        worksheet = sheet.worksheet(worksheet_name)
        # Verificar se a planilha já tem a coluna de pontuação, se não, adicionar
        headers = worksheet.row_values(1)
        if 'Pontuação Total' not in headers:
            # Adicionar coluna de pontuação se não existir
            worksheet.insert_cols([['Pontuação Total']], 7)  # Inserir na coluna G (7)
            # Atualizar cabeçalhos
            headers = ['ID', 'Apelido', 'Email', 'Total de Quizzes', 'Respostas Corretas', 'Taxa de Acerto (%)', 'Pontuação Total', 'Posição', 'Última Atualização']
            worksheet.update('A1:I1', [headers])
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=worksheet_name, rows=1000, cols=10)
        headers = ['ID', 'Apelido', 'Email', 'Total de Quizzes', 'Respostas Corretas', 'Taxa de Acerto (%)', 'Pontuação Total', 'Posição', 'Última Atualização']
        worksheet.append_row(headers)
    return worksheet

def sync_user_to_sheets_with_data(user_id, user_data):
    """
    Sincroniza os dados de um usuário para o Google Sheets usando dados pré-obtidos.
    Esta função não precisa fazer queries no banco, evitando problemas de contexto.
    """
    from flask import current_app
    
    app = current_app
    
    try:
        app.logger.info(f'[SYNC] Starting sync for user_id: {user_id} with pre-fetched data')
        
        sheets_url = app.config.get('GOOGLE_SHEETS_URL')
        if not sheets_url:
            error_msg = 'Google Sheets URL not configured'
            app.logger.error(f'[SYNC] {error_msg}')
            return {'success': False, 'error': error_msg}
        
        sheet_id = extract_sheet_id(sheets_url)
        if not sheet_id:
            error_msg = 'Invalid Google Sheets URL'
            app.logger.error(f'[SYNC] {error_msg}: {sheets_url}')
            return {'success': False, 'error': error_msg}
        
        app.logger.info(f'[SYNC] Connecting to sheet_id: {sheet_id}')
        client = get_client()
        sheet = client.open_by_key(sheet_id)
        app.logger.info(f'[SYNC] Opened sheet: {sheet.title}')
        
        worksheet_name = app.config.get('GOOGLE_SHEETS_WORKSHEET_NAME', 'Ranking')
        app.logger.info(f'[SYNC] Getting/creating worksheet: {worksheet_name}')
        worksheet = get_or_create_worksheet(sheet, worksheet_name)
        
        app.logger.info(f'[SYNC] Syncing user: {user_data["nickname"]} ({user_data["email"]})')
        
        from datetime import datetime
        last_updated = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        app.logger.info(f'[SYNC] Searching for user_id {user_id} in column 1')
        cell = worksheet.find(str(user_id), in_column=1)
        if cell:
            app.logger.info(f'[SYNC] User found at row: {cell.row}')
        else:
            app.logger.info('[SYNC] User not found, will append new row')
        
        row_data = [
            user_data['id'],
            user_data['nickname'],
            user_data['email'],
            user_data['total_attempts'],
            user_data['correct_attempts'],
            user_data['accuracy'],
            max(0, user_data.get('total_score', 0)),  # Pontuação total (garantir >= 0)
            '',  # Posição (será calculada depois)
            last_updated
        ]
        
        if cell:
            app.logger.info(f'[SYNC] Updating row {cell.row} with data: {row_data}')
            worksheet.update(f'A{cell.row}:I{cell.row}', [row_data])
            app.logger.info('[SYNC] Row updated successfully')
        else:
            app.logger.info(f'[SYNC] Appending new row with data: {row_data}')
            worksheet.append_row(row_data)
            app.logger.info('[SYNC] Row appended successfully')
        
        app.logger.info(f'[SYNC] Successfully synced user {user_id} to Google Sheets')
        return {'success': True, 'message': 'User data synced to Google Sheets'}
        
    except FileNotFoundError as e:
        from flask import current_app
        app = current_app
        error_msg = f'Credentials file not found: {e}'
        try:
            app.logger.error(f'[SYNC] {error_msg}', exc_info=True)
        except:
            print(f'[SYNC] {error_msg}')
        return {'success': False, 'error': error_msg}
    except gspread.exceptions.APIError as e:
        from flask import current_app
        app = current_app
        error_msg = f'Google Sheets API error: {e}'
        try:
            app.logger.error(f'[SYNC] {error_msg}', exc_info=True)
        except:
            print(f'[SYNC] {error_msg}')
        return {'success': False, 'error': error_msg}
    except Exception as e:
        from flask import current_app
        app = current_app
        error_msg = f'Unexpected error: {str(e)}'
        try:
            app.logger.error(f'[SYNC] {error_msg}', exc_info=True)
        except:
            print(f'[SYNC] {error_msg}')
        return {'success': False, 'error': error_msg}

def sync_user_to_sheets(user_id):
    """
    Sincroniza os dados de um usuário para o Google Sheets.
    Esta função deve ser chamada dentro do contexto da aplicação Flask.
    """
    from flask import current_app
    
    # Obter app e db do contexto atual
    app = current_app
    # Obter db através do current_app.extensions para garantir contexto correto
    db = app.extensions['sqlalchemy']
    
    # Importar modelos dentro do contexto
    from app import User, QuizAttempt
    
    try:
        app.logger.info(f'[SYNC] Starting sync for user_id: {user_id}')
        
        sheets_url = app.config.get('GOOGLE_SHEETS_URL')
        if not sheets_url:
            error_msg = 'Google Sheets URL not configured'
            app.logger.error(f'[SYNC] {error_msg}')
            return {'success': False, 'error': error_msg}
        
        sheet_id = extract_sheet_id(sheets_url)
        if not sheet_id:
            error_msg = 'Invalid Google Sheets URL'
            app.logger.error(f'[SYNC] {error_msg}: {sheets_url}')
            return {'success': False, 'error': error_msg}
        
        app.logger.info(f'[SYNC] Connecting to sheet_id: {sheet_id}')
        client = get_client()
        sheet = client.open_by_key(sheet_id)
        app.logger.info(f'[SYNC] Opened sheet: {sheet.title}')
        
        worksheet_name = app.config.get('GOOGLE_SHEETS_WORKSHEET_NAME', 'Ranking')
        app.logger.info(f'[SYNC] Getting/creating worksheet: {worksheet_name}')
        worksheet = get_or_create_worksheet(sheet, worksheet_name)
        
        # Usar db.session.get() que funciona corretamente dentro do contexto Flask
        user = db.session.get(User, user_id)
        if not user:
            error_msg = f'User not found: {user_id}'
            app.logger.error(f'[SYNC] {error_msg}')
            return {'success': False, 'error': error_msg}
        
        app.logger.info(f'[SYNC] Syncing user: {user.nickname} ({user.email})')
        
        # Usar db.session.query() em vez de QuizAttempt.query para garantir contexto correto
        attempts = db.session.query(QuizAttempt).filter_by(user_id=user_id).all()
        total_attempts = len(attempts)
        correct_attempts = sum(1 for a in attempts if a.is_correct)
        accuracy = round((correct_attempts / total_attempts * 100) if total_attempts > 0 else 0, 2)
        
        from datetime import datetime
        last_updated = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        app.logger.info(f'[SYNC] Searching for user_id {user_id} in column 1')
        cell = worksheet.find(str(user_id), in_column=1)
        if cell:
            app.logger.info(f'[SYNC] User found at row: {cell.row}')
        else:
            app.logger.info('[SYNC] User not found, will append new row')
        
        row_data = [
            user.id,
            user.nickname,
            user.email,
            total_attempts,
            correct_attempts,
            accuracy,
            max(0, user.total_score or 0),  # Pontuação total (garantir >= 0)
            '',  # Posição (será calculada depois)
            last_updated
        ]
        
        if cell:
            app.logger.info(f'[SYNC] Updating row {cell.row} with data: {row_data}')
            worksheet.update(f'A{cell.row}:I{cell.row}', [row_data])
            app.logger.info('[SYNC] Row updated successfully')
        else:
            app.logger.info(f'[SYNC] Appending new row with data: {row_data}')
            worksheet.append_row(row_data)
            app.logger.info('[SYNC] Row appended successfully')
        
        app.logger.info(f'[SYNC] Successfully synced user {user_id} to Google Sheets')
        return {'success': True, 'message': 'User data synced to Google Sheets'}
        
    except FileNotFoundError as e:
        from flask import current_app
        app = current_app
        error_msg = f'Credentials file not found: {e}'
        try:
            app.logger.error(f'[SYNC] {error_msg}', exc_info=True)
        except:
            print(f'[SYNC] {error_msg}')
        return {'success': False, 'error': error_msg}
    except gspread.exceptions.APIError as e:
        from flask import current_app
        app = current_app
        error_msg = f'Google Sheets API error: {e}'
        try:
            app.logger.error(f'[SYNC] {error_msg}', exc_info=True)
        except:
            print(f'[SYNC] {error_msg}')
        return {'success': False, 'error': error_msg}
    except Exception as e:
        from flask import current_app
        app = current_app
        error_msg = f'Unexpected error: {str(e)}'
        try:
            app.logger.error(f'[SYNC] {error_msg}', exc_info=True)
        except:
            print(f'[SYNC] {error_msg}')
        return {'success': False, 'error': error_msg}

def sync_ranking_to_sheets():
    from app import app, db, User, QuizAttempt
    
    try:
        sheets_url = app.config.get('GOOGLE_SHEETS_URL')
        if not sheets_url:
            return {'success': False, 'error': 'Google Sheets URL not configured'}
        
        sheet_id = extract_sheet_id(sheets_url)
        if not sheet_id:
            return {'success': False, 'error': 'Invalid Google Sheets URL'}
        
        client = get_client()
        sheet = client.open_by_key(sheet_id)
        worksheet_name = app.config.get('GOOGLE_SHEETS_WORKSHEET_NAME', 'Ranking')
        worksheet = get_or_create_worksheet(sheet, worksheet_name)
        
        users = User.query.all()
        ranking_data = []
        
        for user in users:
            attempts = QuizAttempt.query.filter_by(user_id=user.id).all()
            total = len(attempts)
            correct = sum(1 for a in attempts if a.is_correct)
            accuracy = round((correct / total * 100) if total > 0 else 0, 2)
            
            ranking_data.append({
                'id': user.id,
                'nickname': user.nickname,
                'email': user.email,
                'total_quizzes': total,
                'correct_answers': correct,
                'accuracy': accuracy,
                'total_score': max(0, user.total_score or 0)  # Garantir >= 0
            })
        
        # Ordenar por pontuação total (maior primeiro), depois por acurácia, depois por acertos
        # Garantir que todas as pontuações sejam não-negativas antes de ordenar
        for entry in ranking_data:
            if entry['total_score'] < 0:
                entry['total_score'] = 0
        
        ranking_data.sort(key=lambda x: (x['total_score'], x['accuracy'], x['correct_answers']), reverse=True)
        
        for i, entry in enumerate(ranking_data, 1):
            entry['position'] = i
        
        from datetime import datetime
        last_updated = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        worksheet.clear()
        headers = ['ID', 'Apelido', 'Email', 'Total de Quizzes', 'Respostas Corretas', 'Taxa de Acerto (%)', 'Pontuação Total', 'Posição', 'Última Atualização']
        worksheet.append_row(headers)
        
        for entry in ranking_data:
            row = [
                entry['id'],
                entry['nickname'],
                entry['email'],
                entry['total_quizzes'],
                entry['correct_answers'],
                entry['accuracy'],
                entry['total_score'],
                entry['position'],
                last_updated
            ]
            worksheet.append_row(row)
        
        return {'success': True, 'message': f'Ranking synced to Google Sheets ({len(ranking_data)} users)'}
        
    except FileNotFoundError as e:
        return {'success': False, 'error': str(e)}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def read_questions_from_sheets(max_retries=3, retry_delay=10):
    """
    Lê questões da planilha Google Sheets na página "Questoes".
    Retorna uma lista de dicionários com os dados das questões.
    
    Args:
        max_retries: Número máximo de tentativas em caso de rate limit
        retry_delay: Delay inicial entre tentativas (em segundos, aumenta exponencialmente)
    """
    from flask import current_app
    from app import Question
    
    app = current_app
    
    for attempt in range(max_retries):
        try:
            sheets_url = app.config.get('GOOGLE_SHEETS_URL')
            if not sheets_url:
                return {'success': False, 'error': 'Google Sheets URL not configured', 'questions': []}
            
            sheet_id = extract_sheet_id(sheets_url)
            if not sheet_id:
                return {'success': False, 'error': 'Invalid Google Sheets URL', 'questions': []}
            
            client = get_client()
            sheet = client.open_by_key(sheet_id)
            
            # Tentar acessar a página "Questoes"
            try:
                worksheet = sheet.worksheet('Questoes')
            except gspread.exceptions.WorksheetNotFound:
                return {'success': False, 'error': 'Worksheet "Questoes" not found', 'questions': []}
            
            # Ler todas as linhas (primeira linha são os cabeçalhos)
            all_rows = worksheet.get_all_values()
            
            if len(all_rows) < 2:
                return {'success': True, 'questions': [], 'message': 'No questions found in sheet'}
            
            # Extrair cabeçalhos (primeira linha)
            headers = [h.strip() for h in all_rows[0]]
            
            # Mapear índices das colunas
            col_map = {}
            expected_cols = ['ID', 'Autor', 'Titulo', 'Trecho_Letra', 'Enunciado', 'A', 'B', 'C', 'D', 'E', 'Alternativa_Correta', 'Musica_Drive', 'Ano_Composicao', 'Ano_ENEM', 'Comentario', 'Curiosidade', 'Categoria']
            for col in expected_cols:
                try:
                    col_map[col] = headers.index(col)
                except ValueError:
                    # Colunas opcionais (Ano_Composicao, Ano_ENEM, Comentario, Curiosidade, Categoria) não são obrigatórias
                    if col in ['Ano_Composicao', 'Ano_ENEM', 'Comentario', 'Curiosidade', 'Categoria']:
                        app.logger.warning(f'Optional column "{col}" not found in sheet headers, will use empty value')
                        col_map[col] = None
                    else:
                        app.logger.warning(f'Column "{col}" not found in sheet headers: {headers}')
                        return {'success': False, 'error': f'Column "{col}" not found in sheet', 'questions': []}
            
            # Processar linhas de dados
            questions = []
            for row_idx, row in enumerate(all_rows[1:], start=2):  # Começar da linha 2 (após cabeçalho)
                if not row or not any(row):  # Pular linhas vazias
                    continue
                
                try:
                    # Extrair dados da linha (sem processar ainda)
                    external_id = str(row[col_map['ID']]).strip() if col_map['ID'] < len(row) and row[col_map['ID']] else ''
                    artist = row[col_map['Autor']].strip() if col_map['Autor'] < len(row) and row[col_map['Autor']] else ''
                    song_title = row[col_map['Titulo']].strip() if col_map['Titulo'] < len(row) and row[col_map['Titulo']] else ''
                    lyrics = row[col_map['Trecho_Letra']].strip() if col_map['Trecho_Letra'] < len(row) and row[col_map['Trecho_Letra']] else ''
                    statement = row[col_map['Enunciado']].strip() if col_map['Enunciado'] < len(row) and row[col_map['Enunciado']] else ''
                    option_a = row[col_map['A']].strip() if col_map['A'] < len(row) and row[col_map['A']] else ''
                    option_b = row[col_map['B']].strip() if col_map['B'] < len(row) and row[col_map['B']] else ''
                    option_c = row[col_map['C']].strip() if col_map['C'] < len(row) and row[col_map['C']] else ''
                    option_d = row[col_map['D']].strip() if col_map['D'] < len(row) and row[col_map['D']] else ''
                    option_e = row[col_map['E']].strip() if col_map['E'] < len(row) and row[col_map['E']] else ''
                    correct_answer = row[col_map['Alternativa_Correta']].strip().upper() if col_map['Alternativa_Correta'] < len(row) and row[col_map['Alternativa_Correta']] else ''
                    music_drive_raw = row[col_map['Musica_Drive']].strip() if col_map['Musica_Drive'] < len(row) and row[col_map['Musica_Drive']] else ''
                    
                    # Novas colunas opcionais
                    composition_year = None
                    if col_map.get('Ano_Composicao') is not None and col_map['Ano_Composicao'] < len(row) and row[col_map['Ano_Composicao']]:
                        try:
                            composition_year = int(row[col_map['Ano_Composicao']].strip())
                        except (ValueError, AttributeError):
                            composition_year = None
                    
                    enem_year = None
                    if col_map.get('Ano_ENEM') is not None and col_map['Ano_ENEM'] < len(row) and row[col_map['Ano_ENEM']]:
                        try:
                            enem_year = int(row[col_map['Ano_ENEM']].strip())
                        except (ValueError, AttributeError):
                            enem_year = None
                    
                    comment = row[col_map['Comentario']].strip() if col_map.get('Comentario') is not None and col_map['Comentario'] < len(row) and row[col_map['Comentario']] else ''
                    curiosity = row[col_map['Curiosidade']].strip() if col_map.get('Curiosidade') is not None and col_map['Curiosidade'] < len(row) and row[col_map['Curiosidade']] else ''
                    
                    # Categoria (deve ser uma das 4 opções válidas)
                    category_raw = row[col_map['Categoria']].strip() if col_map.get('Categoria') is not None and col_map['Categoria'] < len(row) and row[col_map['Categoria']] else ''
                    category = None
                    if category_raw:
                        # Normalizar categoria: aceitar apenas as 4 opções válidas
                        valid_categories = ['Unicamp', 'Fuvest', 'Enem', 'Outros']
                        category_normalized = category_raw.capitalize()  # Primeira letra maiúscula
                        if category_normalized in valid_categories:
                            category = category_normalized
                        else:
                            # Tentar mapear variações comuns
                            category_lower = category_raw.lower()
                            if category_lower in ['unicamp', 'unicampo']:
                                category = 'Unicamp'
                            elif category_lower in ['fuvest']:
                                category = 'Fuvest'
                            elif category_lower in ['enem']:
                                category = 'Enem'
                            elif category_lower in ['outros', 'other', 'others']:
                                category = 'Outros'
                            else:
                                app.logger.warning(f'[SYNC-QUESTIONS] Invalid category "{category_raw}" in row {row_idx}, will set to None')
                                category = None
                    
                    # Validar que TODAS as colunas obrigatórias estão preenchidas
                    missing_fields = []
                    
                    if not external_id:
                        missing_fields.append('ID')
                    if not artist:
                        missing_fields.append('Autor')
                    if not song_title:
                        missing_fields.append('Titulo')
                    if not lyrics:
                        missing_fields.append('Trecho_Letra')
                    if not statement:
                        missing_fields.append('Enunciado')
                    if not option_a:
                        missing_fields.append('A')
                    if not option_b:
                        missing_fields.append('B')
                    if not option_c:
                        missing_fields.append('C')
                    if not option_d:
                        missing_fields.append('D')
                    if not option_e:
                        missing_fields.append('E')
                    if not correct_answer:
                        missing_fields.append('Alternativa_Correta')
                    if not music_drive_raw:
                        missing_fields.append('Musica_Drive')
                    
                    # Se alguma coluna obrigatória estiver vazia, pular esta linha
                    if missing_fields:
                        app.logger.warning(f'[SYNC-QUESTIONS] Skipping row {row_idx}: missing required fields: {", ".join(missing_fields)}')
                        continue
                    
                    # Validar que a alternativa correta é válida (A, B, C, D ou E)
                    if correct_answer not in ['A', 'B', 'C', 'D', 'E']:
                        app.logger.warning(f'[SYNC-QUESTIONS] Skipping row {row_idx}: invalid correct_answer "{correct_answer}" (must be A, B, C, D, or E)')
                        continue
                    
                    # Processar link do Drive
                    music_drive_url = process_drive_url(music_drive_raw) if music_drive_raw else None
                    
                    # Todos os campos estão preenchidos e válidos, criar objeto de dados
                    question_data = {
                        'external_id': external_id,
                        'artist': artist,
                        'song_title': song_title,
                        'lyrics': lyrics,
                        'statement': statement,
                        'option_a': option_a,
                        'option_b': option_b,
                        'option_c': option_c,
                        'option_d': option_d,
                        'option_e': option_e,
                        'correct_answer': correct_answer,
                        'music_drive_url': music_drive_url,
                        'composition_year': composition_year,
                        'enem_year': enem_year,
                        'comment': comment,
                        'curiosity': curiosity,
                        'category': category
                    }
                    
                    questions.append(question_data)
                    
                except Exception as e:
                    app.logger.error(f'Error processing row {row_idx}: {str(e)}', exc_info=True)
                    continue
            
            app.logger.info(f'[SYNC-QUESTIONS] Read {len(questions)} questions from Google Sheets')
            return {'success': True, 'questions': questions, 'count': len(questions)}
            
        except gspread.exceptions.APIError as e:
            # Extrair informações do erro
            error_code = 0
            error_message = str(e)
            
            if hasattr(e, 'response'):
                if isinstance(e.response, dict):
                    error_code = e.response.get('code', 0)
                    error_message = e.response.get('message', str(e))
                elif hasattr(e.response, 'status_code'):
                    error_code = e.response.status_code
            
            # Verificar se é rate limit (429) ou se a mensagem contém "Quota exceeded"
            is_rate_limit = (error_code == 429 or 
                           '429' in str(e) or 
                           'Quota exceeded' in str(e) or 
                           'RATE_LIMIT' in str(e) or
                           'RESOURCE_EXHAUSTED' in str(e))
            
            # Se for rate limit e ainda temos tentativas, aguardar e tentar novamente
            if is_rate_limit and attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)  # Backoff exponencial: 10s, 20s, 40s
                app.logger.warning(f'[SYNC-QUESTIONS] Rate limit atingido (tentativa {attempt + 1}/{max_retries}). Aguardando {wait_time}s antes de tentar novamente...')
                time.sleep(wait_time)
                continue
            else:
                app.logger.error(f'[SYNC-QUESTIONS] API Error reading questions from sheets: {error_message} (code: {error_code})', exc_info=True)
                return {'success': False, 'error': f'Google Sheets API Error (code {error_code}): {error_message}', 'questions': []}
        
        except Exception as e:
            app.logger.error(f'[SYNC-QUESTIONS] Error reading questions from sheets: {str(e)}', exc_info=True)
            return {'success': False, 'error': str(e), 'questions': []}
    
    # Se chegou aqui, todas as tentativas falharam
    app.logger.error(f'[SYNC-QUESTIONS] Falhou após {max_retries} tentativas')
    return {'success': False, 'error': 'Failed to read questions after multiple attempts', 'questions': []}

# Lock para evitar sincronizações simultâneas (threading lock para mesma thread)
_sync_lock = threading.Lock()

def _acquire_db_lock(db_instance, lock_name='sync_questions', timeout=300, logger=None):
    """
    Adquire um lock no banco de dados usando uma tabela de locks.
    Funciona entre múltiplos processos/workers do Gunicorn.
    Retorna True se conseguiu adquirir o lock, False caso contrário.
    """
    try:
        # Usar uma tabela de locks ou uma query que bloqueia
        # PostgreSQL: SELECT FOR UPDATE NOWAIT bloqueia até conseguir o lock
        # Vamos usar uma abordagem mais simples: tentar inserir em uma tabela de locks
        # Se já existe, significa que outro processo está sincronizando
        
        # Criar tabela de locks se não existir (usando raw SQL)
        db_instance.session.execute(text(
            """CREATE TABLE IF NOT EXISTS sync_locks (
                lock_name VARCHAR(100) PRIMARY KEY,
                acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                process_id INTEGER
            )"""
        ))
        db_instance.session.commit()
        
        # Tentar adquirir o lock
        try:
            # Tentar inserir o lock (se já existir, vai dar erro de integridade)
            db_instance.session.execute(text(
                """INSERT INTO sync_locks (lock_name, process_id) 
                   VALUES (:lock_name, :process_id)"""
            ), {'lock_name': lock_name, 'process_id': os.getpid()})
            db_instance.session.commit()
            return True
        except IntegrityError:
            # Lock já existe, verificar se está expirado (mais de timeout segundos)
            db_instance.session.rollback()
            result = db_instance.session.execute(text(
                """SELECT acquired_at FROM sync_locks 
                   WHERE lock_name = :lock_name"""
            ), {'lock_name': lock_name}).fetchone()
            
            if result:
                acquired_at = result[0]
                # Calcular tempo decorrido
                if isinstance(acquired_at, datetime):
                    elapsed = (datetime.utcnow() - acquired_at).total_seconds()
                else:
                    elapsed = 0
                    
                if elapsed > timeout:
                    # Lock expirado, remover e tentar novamente
                    db_instance.session.execute(text(
                        """DELETE FROM sync_locks WHERE lock_name = :lock_name"""
                    ), {'lock_name': lock_name})
                    db_instance.session.commit()
                    # Tentar inserir novamente
                    try:
                        db_instance.session.execute(text(
                            """INSERT INTO sync_locks (lock_name, process_id) 
                               VALUES (:lock_name, :process_id)"""
                        ), {'lock_name': lock_name, 'process_id': os.getpid()})
                        db_instance.session.commit()
                        return True
                    except IntegrityError:
                        # Ainda não conseguiu (outro processo pegou)
                        db_instance.session.rollback()
                        return False
            return False
    except Exception as e:
        if logger:
            logger.error(f'[SYNC-QUESTIONS] Error acquiring DB lock: {str(e)}', exc_info=True)
        db_instance.session.rollback()
        return False

def _release_db_lock(db_instance, lock_name='sync_questions', logger=None):
    """Libera o lock no banco de dados"""
    try:
        db_instance.session.execute(text(
            """DELETE FROM sync_locks WHERE lock_name = :lock_name"""
        ), {'lock_name': lock_name})
        db_instance.session.commit()
    except Exception as e:
        if logger:
            logger.error(f'[SYNC-QUESTIONS] Error releasing DB lock: {str(e)}', exc_info=True)
        db_instance.session.rollback()

def sync_questions_from_sheets():
    """
    Sincroniza questões da planilha Google Sheets com o banco de dados.
    Adiciona apenas questões novas (comparando por external_id).
    """
    from flask import current_app
    from app import db, Question
    
    app = current_app
    db_instance = app.extensions['sqlalchemy']
    
    # Usar lock de banco de dados para evitar sincronizações simultâneas entre processos
    if not _acquire_db_lock(db_instance, logger=app.logger):
        app.logger.warning('[SYNC-QUESTIONS] Sync already in progress (another worker), skipping...')
        return {'success': False, 'error': 'Sync already in progress'}
    
    try:
        app.logger.info('[SYNC-QUESTIONS] Starting questions synchronization')
        
        # Ler questões da planilha
        result = read_questions_from_sheets()
        if not result.get('success'):
            _release_db_lock(db_instance, logger=app.logger)
            return result
        
        questions_from_sheet = result.get('questions', [])
        
        # Obter todas as questões existentes no banco (por external_id)
        existing_questions = {}
        existing = db_instance.session.query(Question).filter(Question.external_id.isnot(None)).all()
        for q in existing:
            existing_questions[str(q.external_id)] = q
        
        app.logger.info(f'[SYNC-QUESTIONS] Found {len(existing_questions)} existing questions in database')
        
        # Adicionar novas questões
        added_count = 0
        skipped_count = 0
        error_count = 0
        
        # Coletar IDs das questões na planilha
        sheet_external_ids = set()
        
        # Se a planilha estiver vazia, sheet_external_ids ficará vazio e todas as questões serão removidas
        for q_data in questions_from_sheet:
            external_id = q_data['external_id']
            sheet_external_ids.add(str(external_id))
            
            # Verificar se a questão já existe (verificação dupla para evitar race conditions)
            if external_id in existing_questions:
                skipped_count += 1
                continue
            
            # Verificar novamente no banco antes de adicionar (para evitar race conditions)
            existing_q = db_instance.session.query(Question).filter_by(external_id=external_id).first()
            if existing_q:
                skipped_count += 1
                continue
            
            # Criar nova questão
            try:
                # Processar o link do Drive se existir
                drive_url = q_data.get('music_drive_url')
                if drive_url:
                    drive_url = process_drive_url(drive_url)
                
                new_question = Question(
                    external_id=external_id,
                    song_title=q_data['song_title'],
                    artist=q_data['artist'],
                    lyrics=q_data['lyrics'],
                    statement=q_data['statement'],
                    correct_answer=q_data['correct_answer'],
                    option_a=q_data['option_a'],
                    option_b=q_data['option_b'],
                    option_c=q_data['option_c'],
                    option_d=q_data['option_d'],
                    option_e=q_data['option_e'],
                    music_drive_url=drive_url,
                    composition_year=q_data.get('composition_year'),
                    enem_year=q_data.get('enem_year'),
                    comment=q_data.get('comment'),
                    curiosity=q_data.get('curiosity'),
                    category=q_data.get('category')
                )
                
                db_instance.session.add(new_question)
                # Tentar fazer flush para detectar erros de integridade antes do commit
                try:
                    db_instance.session.flush()
                    added_count += 1
                    app.logger.info(f'[SYNC-QUESTIONS] Adding new question: {q_data["song_title"]} by {q_data["artist"]} (ID: {external_id})')
                except IntegrityError as ie:
                    # Rollback do flush e pular esta questão (já existe)
                    db_instance.session.rollback()
                    skipped_count += 1
                    app.logger.warning(f'[SYNC-QUESTIONS] Question {external_id} already exists (duplicate), skipping')
                    continue
            except IntegrityError as ie:
                # Tratar erro de integridade (duplicata)
                db_instance.session.rollback()
                error_count += 1
                skipped_count += 1
                app.logger.warning(f'[SYNC-QUESTIONS] Duplicate question {external_id}, skipping: {str(ie)}')
                continue
            except Exception as e:
                # Outros erros
                db_instance.session.rollback()
                error_count += 1
                skipped_count += 1
                app.logger.error(f'[SYNC-QUESTIONS] Error adding question {external_id}: {str(e)}', exc_info=True)
                continue
        
        # Remover questões que não estão mais na planilha
        removed_count = 0
        for external_id_str, question in existing_questions.items():
            if external_id_str not in sheet_external_ids:
                try:
                    app.logger.info(f'[SYNC-QUESTIONS] Removing question not in sheet: {question.song_title} by {question.artist} (ID: {external_id_str})')
                    # Deletar tentativas relacionadas primeiro (se houver)
                    from app import QuizAttempt
                    attempts = db_instance.session.query(QuizAttempt).filter_by(question_id=question.id).all()
                    for attempt in attempts:
                        db_instance.session.delete(attempt)
                        app.logger.info(f'[SYNC-QUESTIONS] Deleted attempt {attempt.id} for question {question.id}')
                    # Agora deletar a questão
                    db_instance.session.delete(question)
                    removed_count += 1
                except Exception as e:
                    app.logger.error(f'[SYNC-QUESTIONS] Error removing question {external_id_str}: {str(e)}', exc_info=True)
        
        # Commit todas as mudanças
        try:
            if added_count > 0 or removed_count > 0:
                db_instance.session.commit()
                if added_count > 0:
                    app.logger.info(f'[SYNC-QUESTIONS] Successfully added {added_count} new questions')
                if removed_count > 0:
                    app.logger.info(f'[SYNC-QUESTIONS] Successfully removed {removed_count} questions not in sheet')
            else:
                app.logger.info('[SYNC-QUESTIONS] No changes to sync')
        except IntegrityError as ie:
            db_instance.session.rollback()
            app.logger.error(f'[SYNC-QUESTIONS] Integrity error during commit: {str(ie)}', exc_info=True)
            return {
                'success': False,
                'error': f'Database integrity error: {str(ie)}',
                'added': added_count,
                'skipped': skipped_count,
                'removed': removed_count
            }
        except Exception as e:
            db_instance.session.rollback()
            app.logger.error(f'[SYNC-QUESTIONS] Error during commit: {str(e)}', exc_info=True)
            return {
                'success': False,
                'error': f'Error during commit: {str(e)}',
                'added': added_count,
                'skipped': skipped_count,
                'removed': removed_count
            }
        finally:
            # Sempre liberar o lock do banco de dados
            _release_db_lock(db_instance, logger=app.logger)
        
        return {
            'success': True,
            'message': f'Synchronization completed: {added_count} added, {skipped_count} skipped, {removed_count} removed',
            'added': added_count,
            'skipped': skipped_count,
            'removed': removed_count,
            'total_in_sheet': len(questions_from_sheet)
        }
        
    except Exception as e:
        app.logger.error(f'[SYNC-QUESTIONS] Error syncing questions: {str(e)}', exc_info=True)
        return {'success': False, 'error': str(e), 'added': 0, 'skipped': 0}