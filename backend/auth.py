from functools import wraps
from flask import request, jsonify, current_app
from datetime import datetime, timedelta
import jwt

def generate_token(user_id, secret_key, expires_in=3600):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token

def verify_token(token, secret_key):
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_current_user(db=None, User=None):
    token = None
    
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return None
    
    if not token:
        token = request.cookies.get('access_token')
    
    if not token:
        return None
    
    try:
        user_id = verify_token(token, current_app.config['SECRET_KEY'])
    except Exception:
        return None
    
    if not user_id:
        return None
    
    # Sempre usar o db do current_app.extensions para garantir contexto correto
    try:
        # Obter db do current_app.extensions (garantido de estar no contexto correto)
        if hasattr(current_app, 'extensions') and 'sqlalchemy' in current_app.extensions:
            db_to_use = current_app.extensions['sqlalchemy']
        else:
            # Fallback: usar db passado ou importar do módulo app
            if db is None:
                import app as app_module
                db_to_use = app_module.db
            else:
                db_to_use = db
        
        # Obter User do módulo app se não foi passado
        if User is None:
            import app as app_module
            User = app_module.User
        
        # Usar db.session.query() que é mais confiável com o contexto
        return db_to_use.session.query(User).filter(User.id == user_id).first()
    except (RuntimeError, AttributeError, ImportError, Exception) as e:
        if hasattr(current_app, 'logger'):
            current_app.logger.error(f"Error getting user: {e}")
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # get_current_user vai obter db e User automaticamente se não passados
        # Isso garante que sempre usamos as referências corretas do contexto
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function

def optional_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # get_current_user vai obter db e User automaticamente se não passados
        user = get_current_user()
        
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function