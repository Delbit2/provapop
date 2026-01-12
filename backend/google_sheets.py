import gspread
from google.oauth2.service_account import Credentials
import re
import os
from app import app, db, User, QuizAttempt

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
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=worksheet_name, rows=1000, cols=10)
        headers = ['ID', 'Apelido', 'Email', 'Total de Quizzes', 'Respostas Corretas', 'Taxa de Acerto (%)', 'Posição', 'Última Atualização']
        worksheet.append_row(headers)
    return worksheet

def sync_user_to_sheets(user_id):
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
        
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'error': 'User not found'}
        
        attempts = QuizAttempt.query.filter_by(user_id=user_id).all()
        total_attempts = len(attempts)
        correct_attempts = sum(1 for a in attempts if a.is_correct)
        accuracy = round((correct_attempts / total_attempts * 100) if total_attempts > 0 else 0, 2)
        
        from datetime import datetime
        last_updated = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        cell = worksheet.find(str(user_id), in_column=1)
        
        row_data = [
            user.id,
            user.nickname,
            user.email,
            total_attempts,
            correct_attempts,
            accuracy,
            '', 
            last_updated
        ]
        
        if cell:
            worksheet.update(f'A{cell.row}:H{cell.row}', [row_data])
        else:
            worksheet.append_row(row_data)
        
        return {'success': True, 'message': 'User data synced to Google Sheets'}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def sync_ranking_to_sheets():
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
                'accuracy': accuracy
            })
        
        ranking_data.sort(key=lambda x: (x['accuracy'], x['correct_answers']), reverse=True)
        
        for i, entry in enumerate(ranking_data, 1):
            entry['position'] = i
        
        from datetime import datetime
        last_updated = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        worksheet.clear()
        headers = ['ID', 'Apelido', 'Email', 'Total de Quizzes', 'Respostas Corretas', 'Taxa de Acerto (%)', 'Posição', 'Última Atualização']
        worksheet.append_row(headers)
        
        for entry in ranking_data:
            row = [
                entry['id'],
                entry['nickname'],
                entry['email'],
                entry['total_quizzes'],
                entry['correct_answers'],
                entry['accuracy'],
                entry['position'],
                last_updated
            ]
            worksheet.append_row(row)
        
        return {'success': True, 'message': f'Ranking synced to Google Sheets ({len(ranking_data)} users)'}
        
    except FileNotFoundError as e:
        return {'success': False, 'error': str(e)}
    except Exception as e:
        return {'success': False, 'error': str(e)}