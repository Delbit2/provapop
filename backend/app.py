from flask import Flask, request, jsonify, make_response, Response, stream_with_context
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
import os
import threading
import time
import requests
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

allowed_origins = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:5174,http://localhost:3000').split(',')

CORS(
    app,
    supports_credentials=True,
    origins=allowed_origins,
    methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
    expose_headers=['Content-Type', 'Authorization'],
    max_age=3600
)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

def _import_auth():
    from auth import login_required, optional_auth, get_current_user as _get_current_user
    return login_required, optional_auth, _get_current_user

login_required, optional_auth, _get_current_user = _import_auth()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    total_score = db.Column(db.Integer, default=0, nullable=False)  # Pontuação total do usuário
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # NOVAS COLUNAS: Radar de Engajamento e Ofensivas
    last_login = db.Column(db.DateTime, nullable=True)
    total_play_time = db.Column(db.Integer, default=0)  # Tempo em segundos
    current_streak = db.Column(db.Integer, default=0)   # Dias seguidos jogando
    last_play_date = db.Column(db.Date, nullable=True)  # Data da última jogada para calcular a ofensiva
    # NOVAS COLUNAS: Recuperacao de Senha
    reset_token = db.Column(db.String(100), nullable=True, unique=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    
    quizzes = db.relationship('QuizAttempt', backref='user', lazy=True)
    
    def update_score(self, points):
        """
        Atualiza a pontuação do usuário garantindo que nunca fique negativa.
        Sempre use este método para atualizar a pontuação.
        """
        self.total_score = (self.total_score or 0) + points
        if self.total_score < 0:
            self.total_score = 0
        return self.total_score
    
    def ensure_non_negative_score(self):
        """
        Garante que a pontuação não seja negativa.
        Útil para verificação após operações que podem ter modificado total_score diretamente.
        """
        if self.total_score < 0:
            self.total_score = 0
        return self.total_score
    
    def to_dict(self, include_email=False):
        # Garantir que a pontuação não seja negativa antes de retornar
        self.ensure_non_negative_score()
        
        data = {
            'id': self.id,
            'nickname': self.nickname,
            'total_score': self.total_score,  # Garantir que sempre seja >= 0
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'total_play_time': self.total_play_time,
            'current_streak': self.current_streak
        }
        if include_email:
            data['email'] = self.email
        return data
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(50), nullable=True, unique=True)  # ID da planilha Google Sheets
    song_title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    lyrics = db.Column(db.Text, nullable=False)
    statement = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    option_a = db.Column(db.Text, nullable=False)
    option_b = db.Column(db.Text, nullable=False)
    option_c = db.Column(db.Text, nullable=False)
    option_d = db.Column(db.Text, nullable=False)
    option_e = db.Column(db.Text, nullable=False)
    music_drive_url = db.Column(db.String(500), nullable=True)  # URL do Drive para a música
    composition_year = db.Column(db.Integer, nullable=True)  # Ano da Composição
    enem_year = db.Column(db.Integer, nullable=True)  # Ano ENEM
    comment = db.Column(db.Text, nullable=True)  # Comentário/Dica
    curiosity = db.Column(db.Text, nullable=True)  # Curiosidade
    category = db.Column(db.String(20), nullable=True)  # Categoria: Unicamp, Fuvest, Enem, Outros
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'song_title': self.song_title,
            'artist': self.artist,
            'lyrics': self.lyrics,
            'statement': self.statement,
            'options': {
                'A': self.option_a,
                'B': self.option_b,
                'C': self.option_c,
                'D': self.option_d,
                'E': self.option_e
            },
            'correct_answer': self.correct_answer,
            'music_drive_url': self.get_direct_drive_url() if self.music_drive_url else None,
            'composition_year': self.composition_year,
            'enem_year': self.enem_year,
            'comment': self.comment,
            'curiosity': self.curiosity,
            'category': self.category
        }
    
    def get_direct_drive_url(self):
        """
        Converte um link do Google Drive para um link direto utilizável em players de áudio.
        Suporta vários formatos de links do Drive.
        
        Para streaming de áudio HTML5, usa o formato uc?export=download que funciona
        melhor quando o arquivo está compartilhado publicamente.
        """
        if not self.music_drive_url:
            return None
        
        url = self.music_drive_url.strip()
        
        # Padrões de links do Google Drive
        patterns = [
            r'/file/d/([a-zA-Z0-9_-]+)',  # /file/d/FILE_ID/view ou /file/d/FILE_ID/edit
            r'[?&]id=([a-zA-Z0-9_-]+)',  # ?id=FILE_ID ou &id=FILE_ID
            r'/open\?id=([a-zA-Z0-9_-]+)',  # /open?id=FILE_ID
        ]
        
        import re
        file_id = None
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                file_id = match.group(1)
                break
        
        if not file_id:
            # Se não conseguir extrair o ID, retornar o link original
            return url
        
        # Retornar URL do proxy do backend (evita CORS)
        # O backend fará o proxy para o Google Drive
        proxy_url = f'/api/audio/proxy?id={file_id}'
        return proxy_url

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    selected_answer = db.Column(db.String(1), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    points = db.Column(db.Integer, nullable=False)  # Pontos ganhos ou perdidos nesta tentativa (+100 ou -35)
    answered_at = db.Column(db.DateTime, default=datetime.now)
    
    question = db.relationship('Question', backref='attempts')

def get_current_user():
    # Passar db e User explicitamente
    # Mas get_current_user também pode obtê-los automaticamente se necessário
    return _get_current_user(db, User)

def sync_user_to_sheets_async(user_id, max_retries=3, delay=1):
    """
    Executa a sincronização com Google Sheets de forma assíncrona e com retry.
    Esta função roda em uma thread separada para não bloquear a resposta da API.
    """
    # Obter dados do usuário ANTES de entrar na thread para evitar problemas de contexto
    user_data = None
    try:
        user = User.query.get(user_id)
        if user:
            # Obter estatísticas do usuário
            attempts = QuizAttempt.query.filter_by(user_id=user_id).all()
            total_attempts = len(attempts)
            correct_attempts = sum(1 for a in attempts if a.is_correct)
            accuracy = round((correct_attempts / total_attempts * 100) if total_attempts > 0 else 0, 2)
            
            user_data = {
                'id': user.id,
                'nickname': user.nickname,
                'email': user.email,
                'total_attempts': total_attempts,
                'correct_attempts': correct_attempts,
                'accuracy': accuracy,
                'total_score': user.total_score
            }
    except Exception as e:
        app.logger.warning(f'[SYNC-ASYNC] Could not fetch user data before sync: {e}')
        # Continuar mesmo assim, a função sync_user_to_sheets tentará buscar os dados
    
    def sync_with_retry():
        from google_sheets import sync_user_to_sheets_with_data, sync_user_to_sheets
        from flask import current_app
        
        # Criar um novo contexto da aplicação para a thread
        with app.app_context():
            for attempt in range(1, max_retries + 1):
                try:
                    current_app.logger.info(f'[SYNC-ASYNC] Attempting to sync user {user_id} (attempt {attempt}/{max_retries})')
                    
                    # Se temos os dados, usar a função que não precisa fazer queries
                    if user_data:
                        sync_result = sync_user_to_sheets_with_data(user_id, user_data)
                    else:
                        # Fallback: tentar buscar os dados dentro da thread
                        from google_sheets import sync_user_to_sheets
                        sync_result = sync_user_to_sheets(user_id)
                    
                    if sync_result.get('success'):
                        current_app.logger.info(f'[SYNC-ASYNC] Successfully synced user {user_id} to Google Sheets')
                        return
                    else:
                        error = sync_result.get('error', 'Unknown error')
                        current_app.logger.warning(f'[SYNC-ASYNC] Sync failed for user {user_id} (attempt {attempt}/{max_retries}): {error}')
                        
                        if attempt < max_retries:
                            current_app.logger.info(f'[SYNC-ASYNC] Retrying in {delay} seconds...')
                            time.sleep(delay)
                        else:
                            current_app.logger.error(f'[SYNC-ASYNC] Failed to sync user {user_id} after {max_retries} attempts')
                            
                except Exception as e:
                    current_app.logger.error(f'[SYNC-ASYNC] Exception while syncing user {user_id} (attempt {attempt}/{max_retries}): {str(e)}', exc_info=True)
                    
                    if attempt < max_retries:
                        current_app.logger.info(f'[SYNC-ASYNC] Retrying in {delay} seconds...')
                        time.sleep(delay)
                    else:
                        current_app.logger.error(f'[SYNC-ASYNC] Failed to sync user {user_id} after {max_retries} attempts due to exception')
    
    # Executar em thread separada
    thread = threading.Thread(target=sync_with_retry, daemon=True)
    thread.start()
    app.logger.info(f'[SYNC-ASYNC] Started async sync thread for user {user_id}')

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Quiz API is running'}), 200

@app.route('/api/questions', methods=['GET'])
@optional_auth
def get_questions():
    # Filtrar por categoria se fornecida
    category = request.args.get('category', None)
    query = Question.query
    
    if category:
        # Normalizar categoria para corresponder aos valores válidos
        valid_categories = ['Unicamp', 'Fuvest', 'Enem', 'Outros']
        category_normalized = category.capitalize()
        if category_normalized in valid_categories:
            query = query.filter(Question.category == category_normalized)
        else:
            # Tentar mapear variações
            category_lower = category.lower()
            if category_lower in ['unicamp', 'unicampo']:
                query = query.filter(Question.category == 'Unicamp')
            elif category_lower == 'fuvest':
                query = query.filter(Question.category == 'Fuvest')
            elif category_lower == 'enem':
                query = query.filter(Question.category == 'Enem')
            elif category_lower in ['outros', 'other', 'others']:
                query = query.filter(Question.category == 'Outros')
            # Se categoria inválida, retornar todas as questões (sem filtro)
    
    questions = query.all()
    questions_list = []
    
    # Verificar se o usuário já respondeu cada questão (se autenticado)
    user = request.current_user if hasattr(request, 'current_user') else None
    
    for q in questions:
        question_dict = q.to_dict()
        
        if user:
            previous_attempt = QuizAttempt.query.filter_by(
                user_id=user.id,
                question_id=q.id
            ).order_by(QuizAttempt.answered_at.desc()).first()
            
            if previous_attempt:
                question_dict['already_answered'] = True
                question_dict['previous_result'] = previous_attempt.is_correct
                question_dict['previous_answer'] = previous_attempt.selected_answer
            else:
                question_dict['already_answered'] = False
                question_dict['previous_result'] = None
                question_dict['previous_answer'] = None
        else:
            question_dict['already_answered'] = False
            question_dict['previous_result'] = None
            question_dict['previous_answer'] = None
        
        questions_list.append(question_dict)
    
    return jsonify(questions_list), 200

@app.route('/api/questions/<int:question_id>', methods=['GET'])
@optional_auth
def get_question(question_id):
    question = Question.query.get_or_404(question_id)
    question_dict = question.to_dict()
    question_dict.pop('correct_answer', None)
    
    # Verificar se o usuário já respondeu esta questão (se autenticado)
    user = request.current_user if hasattr(request, 'current_user') else None
    
    if user:
        previous_attempt = QuizAttempt.query.filter_by(
            user_id=user.id,
            question_id=question_id
        ).order_by(QuizAttempt.answered_at.desc()).first()
        
        if previous_attempt:
            question_dict['already_answered'] = True
            question_dict['previous_result'] = previous_attempt.is_correct
            question_dict['previous_answer'] = previous_attempt.selected_answer
        else:
            question_dict['already_answered'] = False
    else:
        question_dict['already_answered'] = False
    
    return jsonify(question_dict), 200

@app.route('/api/questions/random', methods=['GET'])
def get_random_question():
    question = Question.query.order_by(db.func.random()).first()
    if not question:
        return jsonify({'error': 'No questions available'}), 404
    question_dict = question.to_dict()
    question_dict.pop('correct_answer', None)
    return jsonify(question_dict), 200

@app.route('/api/questions/<int:question_id>/check', methods=['POST'])
@login_required
def check_answer(question_id):
    user = request.current_user
    data = request.get_json()
    selected_answer = data.get('selected_answer')
    
    if not selected_answer:
        return jsonify({'error': 'selected_answer is required'}), 400
    
    question = Question.query.get_or_404(question_id)
    is_correct = selected_answer.upper() == question.correct_answer.upper()
    
    # Verificar se o usuário já respondeu esta questão antes
    previous_attempt = QuizAttempt.query.filter_by(
        user_id=user.id,
        question_id=question_id
    ).order_by(QuizAttempt.answered_at.desc()).first()
    
    already_answered = previous_attempt is not None
    points = 0
    points_earned = False
    
    if not already_answered:
        # Primeira vez respondendo - calcular pontos normalmente
        points = 100 if is_correct else -35
        
        # Atualizar pontuação total do usuário (garantindo que nunca fique negativa)
        user.update_score(points)
        
        # Atualizar tempo de jogo (usando o tempo do front, ou 15 segundos padrão)
        time_spent = data.get('time_spent', 15)
        user.total_play_time = (user.total_play_time or 0) + time_spent
        
        # Atualizar Ofensiva (Streak)
        hoje = datetime.now().date()
        if user.last_play_date != hoje:
            if user.last_play_date == hoje - timedelta(days=1):
                user.current_streak = (user.current_streak or 0) + 1
            else:
                user.current_streak = 1
            user.last_play_date = hoje
        
        points_earned = True
        
        # Salvar a tentativa apenas se for a primeira vez
        attempt = QuizAttempt(
            user_id=user.id,
            question_id=question_id,
            selected_answer=selected_answer.upper(),
            is_correct=is_correct,
            points=points
        )
        
        db.session.add(attempt)
        db.session.commit()
        
        # Sincronizar com Google Sheets apenas se ganhou/perdeu pontos
        sync_user_to_sheets_async(user.id)
        
        app.logger.info(f'[ATTEMPT] User {user.id} answered question {question_id} for the first time. Correct: {is_correct}, Points: {points}, Total Score: {user.total_score}')
    else:
        # Já respondeu antes - NÃO salvar tentativa, NÃO atualizar ranking, NÃO fazer nada
        app.logger.info(f'[ATTEMPT] User {user.id} attempting question {question_id} again (already answered before) - NO changes to ranking/score')
        # Não fazer commit, não salvar tentativa, não atualizar nada
    
    return jsonify({
        'is_correct': is_correct,
        'correct_answer': question.correct_answer,
        'points': points,
        'total_score': user.total_score,
        'already_answered': already_answered,
        'points_earned': points_earned,
        'previous_result': previous_attempt.is_correct if previous_attempt else None
    }), 200

@app.route('/api/auth/register', methods=['POST'])
def register_user():
    data = request.get_json()
    
    if not data.get('nickname') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'nickname, email and password are required'}), 400
    
    if len(data.get('password', '')) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    if User.query.filter_by(nickname=data['nickname']).first():
        return jsonify({'error': 'Nickname already taken'}), 400
    
    from werkzeug.security import generate_password_hash
    user = User(
        nickname=data['nickname'],
        email=data['email'],
        password_hash=generate_password_hash(data['password'])
    )
    
    db.session.add(user)
    db.session.commit()
    
    # Registrar último login
    user.last_login = datetime.now()
    db.session.commit()

    from auth import generate_token
    token = generate_token(user.id, app.config['SECRET_KEY'], expires_in=3600 * 24)
    
    # Sincronizar com Google Sheets de forma assíncrona (não bloqueia a resposta)
    app.logger.info(f'[REGISTER] User {user.id} ({user.nickname}) registered, triggering async sync')
    sync_user_to_sheets_async(user.id)
    
    response = make_response(jsonify({
        'message': 'User created successfully',
        'user': user.to_dict()
    }))
    
    response.set_cookie(
        'access_token',
        token,
        max_age=3600 * 24,
        httponly=True,
        samesite='Lax',
        secure=False,
        path='/'
    )
    
    return response, 201

@app.route('/api/auth/login', methods=['POST'])
def login_user():
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'email/username and password are required'}), 400
    
    # Tentar encontrar usuário por email ou nickname
    email_or_username = data['email'].strip()
    user = User.query.filter(
        (User.email == email_or_username) | (User.nickname == email_or_username)
    ).first()
    
    # Sincronizar questões automaticamente após login bem-sucedido (antes de verificar senha)
    # Isso será feito em background após o login ser confirmado
    
    if not user:
        return jsonify({'error': 'Senha Incorreta!'}), 401
    
    if not user.check_password(data['password']):
        return jsonify({'error': 'Senha Incorreta!'}), 401
    
    # Registrar último login
    user.last_login = datetime.now()
    db.session.commit()

    from auth import generate_token
    token = generate_token(user.id, app.config['SECRET_KEY'], expires_in=3600 * 24)
    
    # Sincronizar questões automaticamente após login bem-sucedido (em background)
    def sync_on_login():
        try:
            with app.app_context():
                from google_sheets import sync_questions_from_sheets
                app.logger.info(f'[LOGIN-SYNC] User {user.id} logged in, syncing questions...')
                result = sync_questions_from_sheets()
                if result.get('success'):
                    added = result.get('added', 0)
                    if added > 0:
                        app.logger.info(f'[LOGIN-SYNC] ✓ {added} new question(s) synced after login')
                    else:
                        app.logger.debug(f'[LOGIN-SYNC] No new questions found')
                else:
                    app.logger.warning(f'[LOGIN-SYNC] Sync failed: {result.get("error")}')
        except Exception as e:
            app.logger.error(f'[LOGIN-SYNC] Error syncing questions on login: {str(e)}', exc_info=True)
    
    # Executar sincronização em thread separada para não bloquear o login
    sync_thread = threading.Thread(target=sync_on_login, daemon=True, name='LoginSync')
    sync_thread.start()
    
    response = make_response(jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    }))
    
    response.set_cookie(
        'access_token',
        token,
        max_age=3600 * 24,
        httponly=True,
        samesite='Lax',
        secure=False,
        path='/'
    )
    
    return response, 200

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout_user():
    response = make_response(jsonify({'message': 'Logout successful'}))
    response.set_cookie('access_token', '', expires=0)
    return response, 200

@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user_info():
    user = request.current_user
    return jsonify({'user': user.to_dict(include_email=True)}), 200

@app.route('/api/auth/verify', methods=['GET'])
def verify_auth():
    # Sempre passar db e User explicitamente
    user = get_current_user()
    if user:
        return jsonify({'authenticated': True, 'user': user.to_dict()}), 200
    return jsonify({'authenticated': False}), 200

@app.route('/api/users/me/stats', methods=['GET'])
@login_required
def get_user_stats():
    user = request.current_user
    
    attempts = QuizAttempt.query.filter_by(user_id=user.id).all()
    total_attempts = len(attempts)
    correct_attempts = sum(1 for a in attempts if a.is_correct)
    accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
    # Garantir que a pontuação não seja negativa
    user.ensure_non_negative_score()
    
    # Calcular pontuação total (pode ser diferente de user.total_score se houver inconsistências)
    total_points = sum(a.points for a in attempts) if attempts else 0
    # Garantir que pontos calculados também não sejam negativos
    total_points = max(0, total_points)
    
    return jsonify({
        'user_id': user.id,
        'total_quizzes': total_attempts,
        'correct_answers': correct_attempts,
        'accuracy': round(accuracy, 2),
        'total_score': user.total_score,  # Sempre >= 0
        'total_points_calculated': total_points  # Sempre >= 0
    }), 200

@app.route('/api/users/me/attempts', methods=['POST'])
@login_required
def save_attempt():
    user = request.current_user
    data = request.get_json()
    
    if not data.get('question_id') or not data.get('selected_answer'):
        return jsonify({'error': 'question_id and selected_answer are required'}), 400
    
    question = Question.query.get_or_404(data['question_id'])
    is_correct = data['selected_answer'].upper() == question.correct_answer.upper()
    
    # Calcular pontuação: +100 para acertos, -35 para erros
    points = 100 if is_correct else -35
    
    # Atualizar pontuação total do usuário (garantindo que nunca fique negativa)
    user.update_score(points)
    
    # Atualizar tempo de jogo (usando o tempo do front, ou 15 segundos padrão)
    time_spent = data.get('time_spent', 15)
    user.total_play_time = (user.total_play_time or 0) + time_spent
    
    # Atualizar Ofensiva (Streak)
    hoje = datetime.now().date()
    if user.last_play_date != hoje:
        if user.last_play_date == hoje - timedelta(days=1):
            user.current_streak = (user.current_streak or 0) + 1
        else:
            user.current_streak = 1
        user.last_play_date = hoje
    
    attempt = QuizAttempt(
        user_id=user.id,
        question_id=data['question_id'],
        selected_answer=data['selected_answer'].upper(),
        is_correct=is_correct,
        points=points
    )
    
    db.session.add(attempt)
    db.session.commit()
    
    app.logger.info(f'[ATTEMPT] User {user.id} answered question. Correct: {is_correct}, Points: {points}, Total Score: {user.total_score}')
    
    # Sincronizar com Google Sheets de forma assíncrona (não bloqueia a resposta)
    app.logger.info(f'[ATTEMPT] User {user.id} answered question, triggering async sync')
    sync_user_to_sheets_async(user.id)
    
    return jsonify({
        'message': 'Attempt saved',
        'is_correct': is_correct,
        'correct_answer': question.correct_answer,
        'points': points,
        'total_score': user.total_score
    }), 201

@app.route('/api/users/me/profile', methods=['PUT'])
@login_required
def update_profile():
    user = request.current_user
    data = request.get_json()
    
    if data.get('email'):
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user.id:
            return jsonify({'error': 'Email already in use'}), 400
        user.email = data['email']
    
    if data.get('password'):
        from werkzeug.security import generate_password_hash
        user.password_hash = generate_password_hash(data['password'])
    
    db.session.commit()
    
    # Sincronizar com Google Sheets de forma assíncrona (não bloqueia a resposta)
    app.logger.info(f'[PROFILE] User {user.id} updated profile, triggering async sync')
    sync_user_to_sheets_async(user.id)
    
    return jsonify({'message': 'Profile updated', 'user': user.to_dict(include_email=True)}), 200

@app.route('/api/ranking', methods=['GET'])
def get_ranking():
    from datetime import datetime, timedelta
    
    period = request.args.get('period', 'all')  # all, week, month
    
    # Calcular data de corte baseada no período
    cutoff_date = None
    if period == 'week':
        cutoff_date = datetime.now() - timedelta(days=7)
    elif period == 'month':
        cutoff_date = datetime.now() - timedelta(days=30)
    
    users = User.query.all()
    ranking = []
    
    for user in users:
        # Garantir que a pontuação não seja negativa
        user.ensure_non_negative_score()
        
        # Filtrar tentativas por período se necessário
        if cutoff_date:
            attempts = QuizAttempt.query.filter_by(user_id=user.id).filter(
                QuizAttempt.answered_at >= cutoff_date
            ).all()
            # Para períodos específicos, mostrar usuários mesmo sem tentativas (com pontuação 0)
        else:
            attempts = QuizAttempt.query.filter_by(user_id=user.id).all()
            # Para "all", mostrar todos os usuários, mesmo sem tentativas
        
        total = len(attempts)
        correct = sum(1 for a in attempts if a.is_correct)
        accuracy = (correct / total * 100) if total > 0 else 0
        
        # Calcular pontuação do período ou usar total_score
        if cutoff_date:
            # Para períodos específicos, calcular apenas os pontos das tentativas no período
            if attempts:
                period_score = sum(a.points for a in attempts)
                if period_score < 0:
                    period_score = 0
                total_score = period_score
            else:
                # Sem tentativas no período, pontuação 0
                total_score = 0
        else:
            # Para "all", usar o total_score do usuário (mesmo que seja 0)
            total_score = user.total_score if user.total_score else 0
        
        ranking.append({
            'user_id': user.id,
            'nickname': user.nickname,
            'total_quizzes': total,
            'correct_answers': correct,
            'accuracy': round(accuracy, 2),
            'total_score': total_score
        })
    
    # Garantir que todas as pontuações sejam não-negativas antes de ordenar
    for entry in ranking:
        if entry['total_score'] < 0:
            entry['total_score'] = 0
    
    # Ordenar por pontuação total (maior primeiro), depois por acurácia, depois por acertos
    ranking.sort(key=lambda x: (x['total_score'], x['accuracy'], x['correct_answers']), reverse=True)
    
    for i, entry in enumerate(ranking, 1):
        entry['position'] = i
    
    return jsonify(ranking), 200

@app.route('/api/sheets/sync-user', methods=['POST'])
@login_required
def sync_user_to_sheets_endpoint():
    user = request.current_user
    from google_sheets import sync_user_to_sheets
    result = sync_user_to_sheets(user.id)
    
    app.logger.info(f'Sync result for user {user.id}: {result}')
    
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 400

@app.route('/api/sheets/sync-ranking', methods=['POST'])
@login_required
def sync_ranking_to_sheets_endpoint():
    from google_sheets import sync_ranking_to_sheets
    result = sync_ranking_to_sheets()
    
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 400

@app.route('/api/sheets/test', methods=['GET'])
@login_required
def test_sheets_connection():
    from google_sheets import extract_sheet_id, get_client
    from flask import jsonify
    
    sheets_url = app.config.get('GOOGLE_SHEETS_URL')
    if not sheets_url:
        return jsonify({'error': 'Google Sheets URL not configured'}), 400
    
    sheet_id = extract_sheet_id(sheets_url)
    if not sheet_id:
        return jsonify({'error': 'Invalid Google Sheets URL'}), 400
    
    try:
        client = get_client()
        sheet = client.open_by_key(sheet_id)
        return jsonify({
            'success': True,
            'message': 'Connection successful',
            'sheet_title': sheet.title,
            'sheet_id': sheet_id
        }), 200
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/questions/sync', methods=['POST'])
@login_required
def sync_questions():
    """
    Sincroniza questões da planilha Google Sheets com o banco de dados.
    Adiciona apenas questões novas.
    """
    from google_sheets import sync_questions_from_sheets
    
    try:
        result = sync_questions_from_sheets()
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        app.logger.error(f'Error in sync_questions endpoint: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/questions/read-sheet', methods=['GET'])
@login_required
def read_questions_from_sheet():
    """
    Lê questões da planilha Google Sheets sem adicionar ao banco.
    Útil para debug e verificação.
    """
    from google_sheets import read_questions_from_sheets
    
    try:
        result = read_questions_from_sheets()
        return jsonify(result), 200 if result.get('success') else 400
        
    except Exception as e:
        app.logger.error(f'Error in read_questions_from_sheet endpoint: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/questions/auto-sync-status', methods=['GET'])
def get_auto_sync_status():
    """
    Retorna o status da sincronização automática de questões.
    """
    sheets_url = app.config.get('GOOGLE_SHEETS_URL')
    sync_interval = int(os.getenv('QUESTIONS_SYNC_INTERVAL', '900'))  # Padrão: 15 minutos
    
    # Verificar se há threads de sincronização ativas
    sync_threads = [t for t in threading.enumerate() if 'AutoSync' in t.name]
    is_running = len(sync_threads) > 0
    
    return jsonify({
        'enabled': bool(sheets_url),
        'running': is_running,
        'sync_interval_seconds': sync_interval,
        'sync_interval_minutes': sync_interval / 60,
        'sheets_configured': bool(sheets_url),
        'message': 'Auto-sync is running' if (is_running and sheets_url) else 'Auto-sync is disabled or not configured'
    }), 200

@app.route('/api/audio/proxy', methods=['GET'])
def proxy_audio():
    """
    Proxy para servir áudio do Google Drive, evitando problemas de CORS.
    Recebe o file_id como parâmetro e retorna o stream do áudio.
    """
    file_id = request.args.get('id')
    
    if not file_id:
        return jsonify({'error': 'File ID is required'}), 400
    
    # Construir URL do Google Drive
    drive_url = f'https://drive.google.com/uc?export=download&id={file_id}'
    
    try:
        # Fazer requisição para o Google Drive com stream=True para não carregar tudo na memória
        response = requests.get(
            drive_url,
            stream=True,
            timeout=30,
            allow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        # Verificar se a requisição foi bem-sucedida
        if response.status_code != 200:
            app.logger.error(f'[AUDIO-PROXY] Failed to fetch audio from Google Drive. Status: {response.status_code}')
            return jsonify({'error': f'Failed to fetch audio. Status: {response.status_code}'}), response.status_code
        
        # Obter content-type do arquivo
        content_type = response.headers.get('Content-Type', 'audio/mpeg')
        
        # Se o Google Drive retornar HTML (página de aviso), tentar extrair o link direto
        if 'text/html' in content_type:
            # Tentar usar o formato alternativo
            drive_url_alt = f'https://drive.google.com/uc?export=download&id={file_id}&confirm=t'
            response = requests.get(
                drive_url_alt,
                stream=True,
                timeout=30,
                allow_redirects=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            content_type = response.headers.get('Content-Type', 'audio/mpeg')
        
        # Criar resposta streaming
        def generate():
            try:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
            except Exception as e:
                app.logger.error(f'[AUDIO-PROXY] Error streaming audio: {str(e)}')
        
        # Retornar resposta com headers apropriados
        return Response(
            stream_with_context(generate()),
            mimetype=content_type,
            headers={
                'Content-Type': content_type,
                'Accept-Ranges': 'bytes',
                'Cache-Control': 'public, max-age=3600',
                'Access-Control-Allow-Origin': 'http://localhost:5173',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        )
        
    except requests.exceptions.Timeout:
        app.logger.error('[AUDIO-PROXY] Timeout while fetching audio from Google Drive')
        return jsonify({'error': 'Timeout while fetching audio'}), 504
    except requests.exceptions.RequestException as e:
        app.logger.error(f'[AUDIO-PROXY] Error fetching audio from Google Drive: {str(e)}')
        return jsonify({'error': f'Error fetching audio: {str(e)}'}), 500
    except Exception as e:
        app.logger.error(f'[AUDIO-PROXY] Unexpected error: {str(e)}', exc_info=True)
        return jsonify({'error': 'Unexpected error'}), 500

# ============================================================================
# Sincronização Automática de Questões
# ============================================================================

def auto_sync_questions_worker():
    """
    Worker thread que sincroniza questões automaticamente em intervalos regulares.
    Verifica a planilha Google Sheets e adiciona novas questões ao banco de dados.
    """
    # Intervalo de sincronização em segundos (padrão: 15 minutos = 900 segundos)
    # Aumentado para evitar rate limiting (limite: 60 requisições/minuto)
    sync_interval = int(os.getenv('QUESTIONS_SYNC_INTERVAL', '900'))
    
    app.logger.info(f'[AUTO-SYNC] Starting automatic questions sync worker (interval: {sync_interval}s = {sync_interval/60:.1f}min)')
    
    while True:
        try:
            # Criar contexto da aplicação para esta thread
            with app.app_context():
                from google_sheets import sync_questions_from_sheets
                
                app.logger.info('[AUTO-SYNC] Starting automatic sync check...')
                
                try:
                    result = sync_questions_from_sheets()
                    
                    if result.get('success'):
                        added = result.get('added', 0)
                        skipped = result.get('skipped', 0)
                        removed = result.get('removed', 0)
                        
                        if added > 0 or removed > 0:
                            app.logger.info(f'[AUTO-SYNC] ✓ Sync completed: {added} added, {skipped} skipped, {removed} removed')
                        else:
                            app.logger.debug(f'[AUTO-SYNC] No changes ({skipped} already exist)')
                    else:
                        error = result.get('error', 'Unknown error')
                        # Se for rate limit, aumentar o intervalo temporariamente
                        if '429' in str(error) or 'RATE_LIMIT' in str(error) or 'Quota exceeded' in str(error):
                            extended_wait = sync_interval * 3  # Aguardar 3x o intervalo normal
                            app.logger.warning(f'[AUTO-SYNC] Rate limit atingido. Próxima sincronização em {extended_wait}s ({extended_wait/60:.1f}min)')
                            time.sleep(extended_wait)
                            continue
                        else:
                            app.logger.warning(f'[AUTO-SYNC] Sync failed: {error}')
                        
                except Exception as e:
                    app.logger.error(f'[AUTO-SYNC] Error during sync: {str(e)}', exc_info=True)
                
                # Aguardar antes da próxima verificação
                app.logger.debug(f'[AUTO-SYNC] Waiting {sync_interval}s before next sync check...')
                time.sleep(sync_interval)
                
        except Exception as e:
            app.logger.error(f'[AUTO-SYNC] Fatal error in sync worker: {str(e)}', exc_info=True)
            # Em caso de erro fatal, aguardar antes de tentar novamente
            time.sleep(sync_interval)

def start_auto_sync():
    """
    Inicia a thread de sincronização automática.
    Esta função deve ser chamada quando a aplicação Flask inicia.
    """
    try:
        # Verificar se a URL do Google Sheets está configurada
        sheets_url = app.config.get('GOOGLE_SHEETS_URL')
        if not sheets_url:
            app.logger.warning('[AUTO-SYNC] Google Sheets URL not configured. Auto-sync disabled.')
            return
        
        # Fazer uma sincronização imediata ao iniciar
        def initial_sync():
            try:
                with app.app_context():
                    from google_sheets import sync_questions_from_sheets
                    app.logger.info('[AUTO-SYNC] Performing initial sync on startup...')
                    result = sync_questions_from_sheets()
                    if result.get('success'):
                        added = result.get('added', 0)
                        app.logger.info(f'[AUTO-SYNC] ✓ Initial sync completed: {added} new question(s) added')
                    else:
                        app.logger.warning(f'[AUTO-SYNC] Initial sync failed: {result.get("error")}')
            except Exception as e:
                app.logger.error(f'[AUTO-SYNC] Error in initial sync: {str(e)}', exc_info=True)
        
        # Executar sincronização inicial em thread separada
        initial_thread = threading.Thread(target=initial_sync, daemon=True, name='InitialSync')
        initial_thread.start()
        
        # Iniciar thread de sincronização automática periódica
        sync_thread = threading.Thread(target=auto_sync_questions_worker, daemon=True, name='AutoSyncQuestions')
        sync_thread.start()
        app.logger.info('[AUTO-SYNC] ✓ Automatic questions sync started successfully')
        
    except Exception as e:
        app.logger.error(f'[AUTO-SYNC] Failed to start auto-sync: {str(e)}', exc_info=True)

# Flag para controlar se a sincronização automática já foi iniciada
_auto_sync_started = False

# Iniciar sincronização automática quando o módulo é importado
# Isso garante que a sincronização comece mesmo quando o app roda com gunicorn/uwsgi
def init_auto_sync():
    """Inicializa a sincronização automática com delay para garantir que o app está pronto"""
    global _auto_sync_started
    
    if _auto_sync_started:
        return
    
    def delayed_start():
        # Aguardar alguns segundos para garantir que o app está totalmente inicializado
        time.sleep(3)
        try:
            start_auto_sync()
            _auto_sync_started = True
        except Exception as e:
            app.logger.warning(f'[AUTO-SYNC] Could not start auto-sync: {str(e)}')
    
    try:
        init_thread = threading.Thread(target=delayed_start, daemon=True, name='AutoSyncInit')
        init_thread.start()
    except Exception as e:
        app.logger.warning(f'[AUTO-SYNC] Could not start auto-sync thread: {str(e)}')

# Iniciar em uma thread separada para não bloquear
init_auto_sync()

if __name__ == '__main__':
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    with app.app_context():
        db.create_all()
        # Garantir que a sincronização automática seja iniciada quando rodar diretamente
        if not _auto_sync_started:
            time.sleep(1)  # Pequeno delay para garantir que tudo está inicializado
            start_auto_sync()
    
    app.logger.info('Starting Flask application...')
    # Usar debug apenas se FLASK_DEBUG estiver ativado
    debug_mode = app.config.get('FLASK_DEBUG', False)
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)

# --- ROTAS DE RECUPERAÇÃO DE SENHA ---
import os
import secrets
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash
from flask import request, jsonify

@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'message': 'E-mail é obrigatório'}), 400
        
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'Se o e-mail estiver cadastrado, você receberá um link de recuperação.'}), 200
        
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expiry = datetime.now() + timedelta(hours=1)
    db.session.commit()
    
    sender_email = "play@provapop.com.br"
    sender_password = os.getenv("ZOHO_APP_PASSWORD") # Lendo do arquivo .env com segurança!
    
    if not sender_password:
        print("ERRO GRAVE: Senha ZOHO_APP_PASSWORD não encontrada no .env!")
        return jsonify({'message': 'Erro interno do servidor. Contate o suporte.'}), 500
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Recuperação de Senha - ProvaPop!"
    msg['From'] = f"ProvaPop! <{sender_email}>"
    msg['To'] = email
    
    reset_link = f"https://play.provapop.com.br/nova-senha?token={token}"
    
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2>Olá, {user.nickname}! 🎮</h2>
            <p>Recebemos um pedido para redefinir a senha da sua conta no <strong>ProvaPop!</strong>.</p>
            <p>Para criar uma nova senha, clique no botão abaixo (este link expira em 1 hora):</p>
            <a href="{reset_link}" style="display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">Redefinir Minha Senha</a>
            <p style="margin-top: 30px; font-size: 12px; color: #777;">Se você não solicitou esta alteração, pode ignorar este e-mail tranquilamente. Sua senha atual continuará funcionando.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin-top: 30px;">
            <p style="font-size: 12px; color: #aaa;">Equipe ProvaPop!</p>
        </div>
      </body>
    </html>
    """
    msg.attach(MIMEText(html_content, 'html'))
    
    try:
        with smtplib.SMTP_SSL("smtp.zoho.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())
            
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return jsonify({'message': 'Erro ao tentar enviar o e-mail. Tente novamente mais tarde.'}), 500
        
    return jsonify({'message': 'Se o e-mail estiver cadastrado, você receberá um link de recuperação.'}), 200

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    
    if not token or not new_password:
        return jsonify({'message': 'Token e nova senha são obrigatórios'}), 400
        
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.now():
        return jsonify({'message': 'Link inválido ou expirado. Por favor, solicite a recuperação novamente.'}), 400
        
    user.password_hash = generate_password_hash(new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.session.commit()
    
    return jsonify({'message': 'Senha redefinida com sucesso! Você já pode voltar a jogar.'}), 200

