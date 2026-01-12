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

def get_current_user():
    from app import db, User
    
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
    
    user_id = verify_token(token, current_app.config['SECRET_KEY'])
    if not user_id:
        return None
    
    return User.query.get(user_id)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function

def optional_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function