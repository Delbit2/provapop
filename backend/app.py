from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
from config import Config
from auth import login_required, optional_auth, get_current_user

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=['http://localhost:5173', 'http://localhost:5174', 'http://localhost:3000'])
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    quizzes = db.relationship('QuizAttempt', backref='user', lazy=True)
    
    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'nickname': self.nickname,
            'created_at': self.created_at.isoformat()
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
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
            'correct_answer': self.correct_answer
        }

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    selected_answer = db.Column(db.String(1), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    question = db.relationship('Question', backref='attempts')

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Quiz API is running'}), 200

@app.route('/api/questions', methods=['GET'])
def get_questions():
    questions = Question.query.all()
    return jsonify([q.to_dict() for q in questions]), 200

@app.route('/api/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    question = Question.query.get_or_404(question_id)
    question_dict = question.to_dict()
    question_dict.pop('correct_answer', None)
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
    
    attempt = QuizAttempt(
        user_id=user.id,
        question_id=question_id,
        selected_answer=selected_answer.upper(),
        is_correct=is_correct
    )
    
    db.session.add(attempt)
    db.session.commit()
    
    return jsonify({
        'is_correct': is_correct,
        'correct_answer': question.correct_answer
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
    
    from auth import generate_token
    token = generate_token(user.id, app.config['SECRET_KEY'], expires_in=3600 * 24)
    
    from google_sheets import sync_user_to_sheets
    sync_user_to_sheets(user.id)
    
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
        secure=False
    )
    
    return response, 201

@app.route('/api/auth/login', methods=['POST'])
def login_user():
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'email and password are required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    from auth import generate_token
    token = generate_token(user.id, app.config['SECRET_KEY'], expires_in=3600 * 24)
    
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
        secure=False
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
    user = get_current_user()
    if user:
        return jsonify({'authenticated': True, 'user': user.to_dict()}), 200
    return jsonify({'authenticated': False}), 401

@app.route('/api/users/me/stats', methods=['GET'])
@login_required
def get_user_stats():
    user = request.current_user
    
    attempts = QuizAttempt.query.filter_by(user_id=user.id).all()
    total_attempts = len(attempts)
    correct_attempts = sum(1 for a in attempts if a.is_correct)
    accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
    return jsonify({
        'user_id': user.id,
        'total_quizzes': total_attempts,
        'correct_answers': correct_attempts,
        'accuracy': round(accuracy, 2)
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
    
    attempt = QuizAttempt(
        user_id=user.id,
        question_id=data['question_id'],
        selected_answer=data['selected_answer'].upper(),
        is_correct=is_correct
    )
    
    db.session.add(attempt)
    db.session.commit()
    
    from google_sheets import sync_user_to_sheets
    sync_user_to_sheets(user.id)
    
    return jsonify({
        'message': 'Attempt saved',
        'is_correct': is_correct,
        'correct_answer': question.correct_answer
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
    
    from google_sheets import sync_user_to_sheets
    sync_user_to_sheets(user.id)
    
    return jsonify({'message': 'Profile updated', 'user': user.to_dict(include_email=True)}), 200

@app.route('/api/ranking', methods=['GET'])
def get_ranking():
    users = User.query.all()
    ranking = []
    
    for user in users:
        attempts = QuizAttempt.query.filter_by(user_id=user.id).all()
        total = len(attempts)
        correct = sum(1 for a in attempts if a.is_correct)
        accuracy = (correct / total * 100) if total > 0 else 0
        
        ranking.append({
            'user_id': user.id,
            'nickname': user.nickname,
            'total_quizzes': total,
            'correct_answers': correct,
            'accuracy': round(accuracy, 2)
        })
    
    ranking.sort(key=lambda x: (x['accuracy'], x['correct_answers']), reverse=True)
    
    for i, entry in enumerate(ranking, 1):
        entry['position'] = i
    
    return jsonify(ranking), 200

@app.route('/api/sheets/sync-user', methods=['POST'])
@login_required
def sync_user_to_sheets_endpoint():
    user = request.current_user
    from google_sheets import sync_user_to_sheets
    result = sync_user_to_sheets(user.id)
    
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)