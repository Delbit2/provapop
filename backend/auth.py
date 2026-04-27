from functools import wraps
from flask import request, jsonify, current_app
import requests


def get_token_from_request():
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return None

    parts = auth_header.split(' ')
    if len(parts) == 2 and parts[0].lower() == 'bearer':
        return parts[1]

    return None


def get_app_db_and_models(db=None, User=None, StatsModel=None):
    if hasattr(current_app, 'extensions') and 'sqlalchemy' in current_app.extensions:
        db_to_use = current_app.extensions['sqlalchemy']
    else:
        if db is None:
            import app as app_module
            db_to_use = app_module.db
        else:
            db_to_use = db

    if User is None or StatsModel is None:
        import app as app_module
        if User is None:
            User = app_module.Gamer
        if StatsModel is None:
            StatsModel = app_module.EstatisticaGamer

    return db_to_use, User, StatsModel


def ensure_user_stats(user, db_to_use, StatsModel):
    if not user:
        return None

    stats = db_to_use.session.query(StatsModel).filter(StatsModel.gamer_id == user.id).first()
    if not stats:
        stats = StatsModel(gamer_id=user.id)
        db_to_use.session.add(stats)
        db_to_use.session.commit()

        if hasattr(current_app, 'logger'):
            current_app.logger.info(f'Estatísticas criadas automaticamente para gamer.id={user.id}')

    return stats


def get_user_from_supabase_token(token, db=None, User=None, StatsModel=None):
    supabase_url = current_app.config.get('SUPABASE_URL') or current_app.config.get('VITE_SUPABASE_URL')
    supabase_anon_key = current_app.config.get('SUPABASE_ANON_KEY') or current_app.config.get('VITE_SUPABASE_ANON_KEY')

    if hasattr(current_app, 'logger'):
        current_app.logger.info(f'SUPABASE_URL presente? {bool(supabase_url)}')
        current_app.logger.info(f'SUPABASE_ANON_KEY presente? {bool(supabase_anon_key)}')

    if not supabase_url or not supabase_anon_key:
        if hasattr(current_app, 'logger'):
            current_app.logger.warning('SUPABASE_URL ou SUPABASE_ANON_KEY não configurados.')
        return None

    db_to_use, User, StatsModel = get_app_db_and_models(db, User, StatsModel)

    try:
        response = requests.get(
            f"{supabase_url.rstrip('/')}/auth/v1/user",
            headers={
                'Authorization': f'Bearer {token}',
                'apikey': supabase_anon_key
            },
            timeout=10
        )

        if hasattr(current_app, 'logger'):
            current_app.logger.info(f'Supabase /auth/v1/user status={response.status_code}')
            current_app.logger.info(f'Supabase /auth/v1/user body={response.text[:500]}')

        if response.status_code != 200:
            return None

        supabase_user = response.json()
        supabase_user_id = supabase_user.get('id')
        email = supabase_user.get('email')
        raw_nome = (
            supabase_user.get('user_metadata', {}).get('nome')
            or supabase_user.get('user_metadata', {}).get('name')
            or supabase_user.get('user_metadata', {}).get('nickname')
            or (email.split('@')[0] if email else None)
            or 'Jogador'
        )

        if hasattr(current_app, 'logger'):
            current_app.logger.info(
                f'Supabase user recebido: id={supabase_user_id}, email={email}, raw_nome={raw_nome}'
            )

        if not supabase_user_id:
            return None

        gamer = db_to_use.session.query(User).filter(User.supabase_user_id == supabase_user_id).first()

        if gamer and hasattr(current_app, 'logger'):
            current_app.logger.info(f'Gamer encontrado por supabase_user_id: gamer.id={gamer.id}')

        if not gamer and email:
            gamer = db_to_use.session.query(User).filter(User.email == email).first()
            if gamer and not gamer.supabase_user_id:
                gamer.supabase_user_id = supabase_user_id
                db_to_use.session.commit()
                if hasattr(current_app, 'logger'):
                    current_app.logger.info(f'Gamer vinculado por email: gamer.id={gamer.id}')

        if not gamer:
            base_nome = raw_nome[:100]
            nome_final = base_nome

            contador = 1
            while db_to_use.session.query(User).filter(User.nome == nome_final).first():
                sufixo = f"_{contador}"
                nome_final = f"{base_nome[:100 - len(sufixo)]}{sufixo}"
                contador += 1

            gamer = User(
                supabase_user_id=supabase_user_id,
                nome=nome_final,
                email=email or f'{supabase_user_id}@supabase.local',
                password_hash='SUPABASE_AUTH'
            )
            db_to_use.session.add(gamer)
            db_to_use.session.commit()

            stats = StatsModel(gamer_id=gamer.id)
            db_to_use.session.add(stats)
            db_to_use.session.commit()

            if hasattr(current_app, 'logger'):
                current_app.logger.info(
                    f'Novo gamer criado via Supabase: gamer.id={gamer.id}, nome={gamer.nome}'
                )
        else:
            ensure_user_stats(gamer, db_to_use, StatsModel)

        return gamer

    except Exception as e:
        if hasattr(current_app, 'logger'):
            current_app.logger.error(f'Erro validando token Supabase: {e}')
        return None


def get_current_user(db=None, User=None, StatsModel=None):
    token = get_token_from_request()

    if hasattr(current_app, 'logger'):
        current_app.logger.info(f'Token presente na request? {bool(token)}')
        if token:
            current_app.logger.info(f'Token preview: {token[:40]}...')

    if not token:
        return None

    try:
        user = get_user_from_supabase_token(token, db, User, StatsModel)
        if user:
            if hasattr(current_app, 'logger'):
                current_app.logger.info(f'Usuário autenticado por Supabase: id={user.id}')
            return user
    except Exception as e:
        if hasattr(current_app, 'logger'):
            current_app.logger.error(f'Erro na autenticação Supabase: {e}')

    if hasattr(current_app, 'logger'):
        current_app.logger.warning('Falha final de autenticação: nenhum usuário resolvido.')

    return None


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
