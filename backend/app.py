import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta, timezone
import secrets
import smtplib
import random
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

GUARANTEED_ORIGINS = [
    "https://play.provapop.com.br",
    "http://play.provapop.com.br",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:4173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5000"
]

env_origins = os.environ.get('CORS_ORIGINS', '')
if env_origins:
    GUARANTEED_ORIGINS.extend([origin.strip() for origin in env_origins.split(',') if origin.strip()])

final_origins = list(set(GUARANTEED_ORIGINS))

CORS(
    app,
    supports_credentials=True,
    origins=final_origins,
    methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'Accept', 'Origin'],
    expose_headers=['Content-Type', 'Authorization'],
    max_age=3600
)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


def _import_auth():
    from auth import login_required, optional_auth, get_current_user as _get_current_user
    return login_required, optional_auth, _get_current_user


login_required, optional_auth, _get_current_user = _import_auth()


def debug_auth_context(tag="DEBUG"):
    auth_header = request.headers.get("Authorization")
    origin = request.headers.get("Origin")
    current_user = getattr(request, "current_user", None)

    print(f"=== {tag} ===")
    print("Method:", request.method)
    print("Path:", request.path)
    print("Origin:", origin)
    print("Authorization header present?:", bool(auth_header))
    if auth_header:
        print("Authorization header preview:", auth_header[:80] + ("..." if len(auth_header) > 80 else ""))
    else:
        print("Authorization header preview: None")
    print("request.current_user:", current_user)
    print("====================")


class Gamer(db.Model):
    __tablename__ = 'gamers'

    id = db.Column(db.BigInteger, primary_key=True)
    supabase_user_id = db.Column(db.String(36), unique=True, nullable=True, index=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    criado_em = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime(timezone=True), nullable=True)
    ultimo_logout = db.Column(db.DateTime(timezone=True), nullable=True)

    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token_expiry = db.Column(db.DateTime(timezone=True), nullable=True)

    estatisticas = db.relationship(
        'EstatisticaGamer',
        backref='gamer',
        uselist=False,
        lazy=True,
        cascade='all, delete-orphan'
    )

    partidas = db.relationship(
        'Partida',
        backref='gamer',
        lazy=True,
        cascade='all, delete-orphan'
    )

    respostas = db.relationship(
        'Resposta',
        backref='gamer',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def get_estatisticas(self):
        return self.estatisticas

    def to_dict(self, include_email=False):
        stats = self.get_estatisticas()

        ofensiva_exibicao = stats.ofensiva_atual if stats else 0
        data_ultima_partida = stats.data_ultima_missao_concluida if stats else None

        if data_ultima_partida:
            fuso_br = timezone(timedelta(hours=-3))
            hoje = datetime.now(fuso_br).date()
            if (hoje - data_ultima_partida).days > 1:
                ofensiva_exibicao = 0

        data = {
            'id': self.id,
            'nome': self.nome,
            'pontuacao': stats.pontuacao_total if stats else 0,
            'total_respondidas': stats.total_respondidas if stats else 0,
            'total_acertos': stats.total_acertos if stats else 0,
            'ofensiva': ofensiva_exibicao,
            'recorde_ofensiva': stats.recorde_ofensiva if stats else 0,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'ultimo_login': self.ultimo_login.isoformat() if self.ultimo_login else None,
            'data_ultima_partida': data_ultima_partida.isoformat() if data_ultima_partida else None
        }

        if include_email:
            data['email'] = self.email

        return data

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class EstatisticaGamer(db.Model):
    __tablename__ = 'estatisticas_gamer'

    gamer_id = db.Column(db.BigInteger, db.ForeignKey('gamers.id'), primary_key=True)
    pontuacao_total = db.Column(db.Integer, nullable=False, default=0)
    total_respondidas = db.Column(db.Integer, nullable=False, default=0)
    total_acertos = db.Column(db.Integer, nullable=False, default=0)
    ofensiva_atual = db.Column(db.Integer, nullable=False, default=0)
    recorde_ofensiva = db.Column(db.Integer, nullable=False, default=0)
    data_ultima_missao_concluida = db.Column(db.Date, nullable=True)
    criado_em = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'gamer_id': self.gamer_id,
            'pontuacao_total': self.pontuacao_total,
            'total_respondidas': self.total_respondidas,
            'total_acertos': self.total_acertos,
            'ofensiva_atual': self.ofensiva_atual,
            'recorde_ofensiva': self.recorde_ofensiva,
            'data_ultima_missao_concluida': self.data_ultima_missao_concluida.isoformat() if self.data_ultima_missao_concluida else None,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }


class Questao(db.Model):
    __tablename__ = 'questoes'

    id = db.Column(db.BigInteger, primary_key=True)
    autor = db.Column(db.String(150), nullable=False)
    titulo = db.Column(db.String(150), nullable=False)
    trecho_letra = db.Column(db.Text, nullable=False)
    creditos = db.Column(db.String(255), nullable=True)
    enunciado = db.Column(db.Text, nullable=False)

    a = db.Column(db.Text, nullable=True)
    b = db.Column(db.Text, nullable=True)
    c = db.Column(db.Text, nullable=True)
    d = db.Column(db.Text, nullable=True)
    e = db.Column(db.Text, nullable=True)

    alternativa_correta = db.Column(db.String(1), nullable=False)

    musica_url = db.Column(db.String(500), nullable=False)
    ano_lancamento = db.Column(db.Integer, nullable=True)
    ano_prova = db.Column(db.Integer, nullable=True)
    comentario = db.Column(db.Text, nullable=True)
    curiosidade = db.Column(db.Text, nullable=True)

    prova = db.Column(db.String(100), nullable=False)
    matriz_enem = db.Column(db.String(100), nullable=True)
    disciplina = db.Column(db.String(100), nullable=True)
    data_exibicao = db.Column(db.Date, nullable=True)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    criado_em = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    respostas = db.relationship('Resposta', backref='questao', lazy=True)

    def to_dict(self, include_correct_answer=True):
        data = {
            'id': self.id,
            'autor': self.autor,
            'titulo': self.titulo,
            'trecho_letra': self.trecho_letra,
            'creditos': self.creditos,
            'enunciado': self.enunciado,
            'a': self.a,
            'b': self.b,
            'c': self.c,
            'd': self.d,
            'e': self.e,
            'alternativas': {
                'A': self.a,
                'B': self.b,
                'C': self.c,
                'D': self.d,
                'E': self.e
            },
            'musica_url': self.musica_url,
            'ano_lancamento': self.ano_lancamento,
            'ano_prova': self.ano_prova,
            'comentario': self.comentario,
            'curiosidade': self.curiosidade,
            'prova': self.prova,
            'matriz_enem': self.matriz_enem,
            'disciplina': self.disciplina,
            'data_exibicao': self.data_exibicao.isoformat() if self.data_exibicao else None,
            'ativo': self.ativo
        }

        if include_correct_answer:
            data['alternativa_correta'] = self.alternativa_correta

        return data


class Partida(db.Model):
    __tablename__ = 'partidas'

    id = db.Column(db.BigInteger, primary_key=True)
    gamer_id = db.Column(db.BigInteger, db.ForeignKey('gamers.id'), nullable=False)

    tipo = db.Column(db.String(50), nullable=False, default='daily')
    status = db.Column(db.String(30), nullable=False, default='em_andamento')
    origem = db.Column(db.String(50), nullable=True)

    data_referencia = db.Column(db.Date, nullable=False, default=lambda: datetime.utcnow().date())
    iniciada_em = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    finalizada_em = db.Column(db.DateTime(timezone=True), nullable=True)

    questoes_previstas = db.Column(db.Integer, nullable=False, default=4)
    questoes_respondidas = db.Column(db.Integer, nullable=False, default=0)
    questoes_acertadas = db.Column(db.Integer, nullable=False, default=0)

    tempo_total_segundos = db.Column(db.Integer, nullable=False, default=0)
    pontuacao_total = db.Column(db.Integer, nullable=False, default=0)

    missao_concluida = db.Column(db.Boolean, nullable=False, default=False)
    ofensiva_gerada = db.Column(db.Boolean, nullable=False, default=False)

    criado_em = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    respostas = db.relationship(
        'Resposta',
        backref='partida',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'gamer_id': self.gamer_id,
            'tipo': self.tipo,
            'status': self.status,
            'origem': self.origem,
            'data_referencia': self.data_referencia.isoformat() if self.data_referencia else None,
            'iniciada_em': self.iniciada_em.isoformat() if self.iniciada_em else None,
            'finalizada_em': self.finalizada_em.isoformat() if self.finalizada_em else None,
            'questoes_previstas': self.questoes_previstas,
            'questoes_respondidas': self.questoes_respondidas,
            'questoes_acertadas': self.questoes_acertadas,
            'tempo_total_segundos': self.tempo_total_segundos,
            'pontuacao_total': self.pontuacao_total,
            'missao_concluida': self.missao_concluida,
            'ofensiva_gerada': self.ofensiva_gerada
        }


class Resposta(db.Model):
    __tablename__ = 'respostas'

    id = db.Column(db.BigInteger, primary_key=True)
    partida_id = db.Column(db.BigInteger, db.ForeignKey('partidas.id'), nullable=False)
    gamer_id = db.Column(db.BigInteger, db.ForeignKey('gamers.id'), nullable=False)
    questao_id = db.Column(db.BigInteger, db.ForeignKey('questoes.id'), nullable=False)

    alternativa_selecionada = db.Column(db.String(1), nullable=False)
    acertou = db.Column(db.Boolean, nullable=False)
    pontos_ganhos = db.Column(db.Integer, nullable=False, default=0)
    tempo_gasto_segundos = db.Column(db.Integer, nullable=True)

    respondida_em = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    criado_em = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'partida_id': self.partida_id,
            'gamer_id': self.gamer_id,
            'questao_id': self.questao_id,
            'alternativa_selecionada': self.alternativa_selecionada,
            'acertou': self.acertou,
            'pontos_ganhos': self.pontos_ganhos,
            'tempo_gasto_segundos': self.tempo_gasto_segundos,
            'respondida_em': self.respondida_em.isoformat() if self.respondida_em else None
        }


def get_or_create_estatisticas(gamer_id):
    stats = EstatisticaGamer.query.filter_by(gamer_id=gamer_id).first()
    if not stats:
        stats = EstatisticaGamer(gamer_id=gamer_id)
        db.session.add(stats)
        db.session.commit()
    return stats


def get_brazil_today():
    fuso_br = timezone(timedelta(hours=-3))
    return datetime.now(fuso_br).date()


def get_or_create_daily_partida(gamer_id, origem='questoes_do_dia'):
    hoje = get_brazil_today()

    partida = Partida.query.filter_by(
        gamer_id=gamer_id,
        tipo='daily',
        data_referencia=hoje,
        status='em_andamento'
    ).order_by(Partida.id.desc()).first()

    if partida:
        return partida

    partida = Partida(
        gamer_id=gamer_id,
        tipo='daily',
        status='em_andamento',
        origem=origem,
        data_referencia=hoje,
        questoes_previstas=4
    )
    db.session.add(partida)
    db.session.commit()
    return partida


def serialize_question_with_user_context(questao, gamer=None):
    question_dict = questao.to_dict()

    if gamer:
        previous_answer = Resposta.query.filter_by(
            gamer_id=gamer.id,
            questao_id=questao.id
        ).order_by(Resposta.respondida_em.desc()).first()

        if previous_answer:
            question_dict['already_answered'] = True
            question_dict['previous_result'] = previous_answer.acertou
            question_dict['previous_answer'] = previous_answer.alternativa_selecionada
        else:
            question_dict['already_answered'] = False
            question_dict['previous_result'] = None
            question_dict['previous_answer'] = None
    else:
        question_dict['already_answered'] = False
        question_dict['previous_result'] = None
        question_dict['previous_answer'] = None

    return question_dict


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Quiz API is running'}), 200


@app.route('/api/questions', methods=['GET'])
@optional_auth
def get_questions():
    filtro_prova = request.args.get('prova') or request.args.get('categoria') or request.args.get('category')
    query = Questao.query.filter_by(ativo=True)

    if filtro_prova:
        valid_provas = ['Unicamp', 'Fuvest', 'Enem', 'Outros']
        prova_normalized = filtro_prova.capitalize()
        if prova_normalized in valid_provas:
            query = query.filter(Questao.prova == prova_normalized)
        else:
            prova_lower = filtro_prova.lower()
            if prova_lower in ['unicamp', 'unicampo']:
                query = query.filter(Questao.prova == 'Unicamp')
            elif prova_lower == 'fuvest':
                query = query.filter(Questao.prova == 'Fuvest')
            elif prova_lower == 'enem':
                query = query.filter(Questao.prova == 'Enem')
            elif prova_lower in ['outros', 'other', 'others']:
                query = query.filter(Questao.prova == 'Outros')

    questoes = query.order_by(Questao.id.asc()).all()
    gamer = request.current_user if hasattr(request, 'current_user') else None

    questions_list = [serialize_question_with_user_context(q, gamer) for q in questoes]
    return jsonify(questions_list), 200


@app.route('/api/questions/<int:question_id>', methods=['GET'])
@optional_auth
def get_question(question_id):
    questao = Questao.query.filter_by(id=question_id, ativo=True).first_or_404()
    gamer = request.current_user if hasattr(request, 'current_user') else None
    question_dict = serialize_question_with_user_context(questao, gamer)
    return jsonify(question_dict), 200


@app.route('/api/questions/random', methods=['GET'])
def get_random_question():
    questao = Questao.query.filter_by(ativo=True).order_by(db.func.random()).first()
    if not questao:
        return jsonify({'error': 'Nenhuma questão encontrada'}), 404

    question_dict = questao.to_dict(include_correct_answer=False)
    return jsonify(question_dict), 200


@app.route('/api/questions/<int:question_id>/check', methods=['POST'])
@login_required
def check_answer(question_id):
    debug_auth_context("CHECK_ANSWER_ROUTE_ENTERED")

    gamer = request.current_user
    stats = get_or_create_estatisticas(gamer.id)
    data = request.get_json() or {}

    selected_answer = (data.get('selected_answer') or data.get('alternativa_selecionada') or '').strip().upper()
    partida_id = data.get('partida_id')
    time_spent = data.get('time_spent', data.get('tempo_gasto_segundos', 15))

    if not selected_answer:
        return jsonify({'error': 'Alternativa selecionada é obrigatória'}), 400

    if selected_answer not in ['A', 'B', 'C', 'D', 'E']:
        return jsonify({'error': 'Alternativa inválida'}), 400

    questao = Questao.query.filter_by(id=question_id, ativo=True).first_or_404()
    is_correct = selected_answer == questao.alternativa_correta.upper()

    hoje = get_brazil_today()

    partida = None
    if partida_id:
        partida = Partida.query.filter_by(id=partida_id, gamer_id=gamer.id).first()
        if not partida:
            return jsonify({'error': 'Partida não encontrada para este usuário'}), 404
    else:
        partida = get_or_create_daily_partida(gamer.id, origem='check_answer')

    if partida.status != 'em_andamento':
        return jsonify({'error': 'Esta partida já foi encerrada.'}), 400

    if partida.data_referencia != hoje:
        return jsonify({'error': 'Esta partida não pertence ao dia atual.'}), 400

    resposta_existente_na_partida = Resposta.query.filter_by(
        partida_id=partida.id,
        questao_id=question_id
    ).first()

    if resposta_existente_na_partida:
        return jsonify({
            'is_correct': resposta_existente_na_partida.acertou,
            'correct_answer': questao.alternativa_correta,
            'points': 0,
            'total_score': stats.pontuacao_total,
            'already_answered': True,
            'points_earned': False,
            'limite_diario_atingido': partida.questoes_respondidas >= partida.questoes_previstas,
            'missao_cumprida_agora': False,
            'nova_ofensiva': stats.ofensiva_atual,
            'novo_recorde': stats.recorde_ofensiva,
            'previous_result': resposta_existente_na_partida.acertou,
            'partida_id': partida.id
        }), 200

    if partida.questoes_respondidas >= partida.questoes_previstas:
        return jsonify({
            "error": "Você já completou as 4 questões de hoje!",
            "limit_reached": True,
            "partida_id": partida.id
        }), 403

    points = 100 if is_correct else -35

    resposta = Resposta(
        partida_id=partida.id,
        gamer_id=gamer.id,
        questao_id=question_id,
        alternativa_selecionada=selected_answer,
        acertou=is_correct,
        pontos_ganhos=points,
        tempo_gasto_segundos=time_spent
    )
    db.session.add(resposta)

    partida.questoes_respondidas += 1
    if is_correct:
        partida.questoes_acertadas += 1
    partida.pontuacao_total += points
    partida.tempo_total_segundos += max(int(time_spent or 0), 0)

    stats.total_respondidas += 1
    if is_correct:
        stats.total_acertos += 1
    stats.pontuacao_total = max((stats.pontuacao_total or 0) + points, 0)

    missao_cumprida_agora = False

    if partida.questoes_respondidas >= partida.questoes_previstas:
        partida.status = 'finalizada'
        partida.finalizada_em = datetime.utcnow()
        partida.missao_concluida = True

        if stats.data_ultima_missao_concluida == hoje - timedelta(days=1):
            stats.ofensiva_atual += 1
        elif stats.data_ultima_missao_concluida == hoje:
            pass
        else:
            stats.ofensiva_atual = 1

        if stats.data_ultima_missao_concluida != hoje:
            stats.data_ultima_missao_concluida = hoje
            partida.ofensiva_gerada = True
            missao_cumprida_agora = True

        if stats.ofensiva_atual > stats.recorde_ofensiva:
            stats.recorde_ofensiva = stats.ofensiva_atual

    db.session.commit()

    app.logger.info(f'[JOGO] Gamer {gamer.id} respondeu questao {question_id}. Acertou: {is_correct}')

    return jsonify({
        'is_correct': is_correct,
        'correct_answer': questao.alternativa_correta,
        'points': points,
        'total_score': stats.pontuacao_total,
        'already_answered': False,
        'points_earned': True,
        'limite_diario_atingido': partida.questoes_respondidas >= partida.questoes_previstas,
        'missao_cumprida_agora': missao_cumprida_agora,
        'nova_ofensiva': stats.ofensiva_atual,
        'novo_recorde': stats.recorde_ofensiva,
        'previous_result': None,
        'partida_id': partida.id
    }), 200


@app.route('/api/auth/register', methods=['POST'])
def register_user():
    data = request.get_json() or {}

    nome = data.get('nickname') or data.get('nome')
    email = data.get('email')
    password = data.get('password') or data.get('senha')

    if not nome or not email or not password:
        return jsonify({'error': 'Nome, email e senha são obrigatórios'}), 400

    if len(password) < 6:
        return jsonify({'error': 'A senha deve ter pelo menos 6 caracteres'}), 400

    if Gamer.query.filter_by(email=email).first():
        return jsonify({'error': 'Email já cadastrado'}), 400

    if Gamer.query.filter_by(nome=nome).first():
        return jsonify({'error': 'Nickname já em uso'}), 400

    gamer = Gamer(
        nome=nome,
        email=email,
        password_hash=generate_password_hash(password)
    )

    db.session.add(gamer)
    db.session.commit()

    estatisticas = EstatisticaGamer(gamer_id=gamer.id)
    db.session.add(estatisticas)

    gamer.ultimo_login = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'message': 'Gamer criado com sucesso',
        'user': gamer.to_dict()
    }), 201


@app.route('/api/auth/login', methods=['POST'])
def login_user():
    data = request.get_json() or {}

    identificador = data.get('email') or data.get('username') or data.get('nome')
    password = data.get('password') or data.get('senha')

    if not identificador or not password:
        return jsonify({'error': 'Login e senha são obrigatórios'}), 400

    identificador = identificador.strip()
    gamer = Gamer.query.filter(
        (Gamer.email == identificador) | (Gamer.nome == identificador)
    ).first()

    if not gamer or not gamer.check_password(password):
        return jsonify({'error': 'Senha Incorreta ou Jogador não encontrado!'}), 401

    get_or_create_estatisticas(gamer.id)

    gamer.ultimo_login = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'message': 'Login realizado com sucesso',
        'user': gamer.to_dict()
    }), 200


@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout_user():
    gamer = request.current_user
    gamer.ultimo_logout = datetime.utcnow()
    db.session.commit()

    return jsonify({'message': 'Logout efetuado'}), 200


@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user_info():
    gamer = request.current_user
    get_or_create_estatisticas(gamer.id)
    return jsonify({'user': gamer.to_dict(include_email=True)}), 200


@app.route('/api/auth/verify', methods=['GET'])
def verify_auth():
    gamer = _get_current_user()
    if gamer:
        get_or_create_estatisticas(gamer.id)
        return jsonify({'authenticated': True, 'user': gamer.to_dict()}), 200
    return jsonify({'authenticated': False}), 200


@app.route('/api/users/me/stats', methods=['GET'])
@login_required
def get_user_stats():
    gamer = request.current_user
    stats = get_or_create_estatisticas(gamer.id)

    accuracy = (stats.total_acertos / stats.total_respondidas * 100) if stats.total_respondidas > 0 else 0

    return jsonify({
        'user_id': gamer.id,
        'total_quizzes': stats.total_respondidas,
        'correct_answers': stats.total_acertos,
        'accuracy': round(accuracy, 2),
        'total_score': stats.pontuacao_total,
        'total_points_calculated': stats.pontuacao_total,
        'ofensiva': stats.ofensiva_atual,
        'recorde_ofensiva': stats.recorde_ofensiva
    }), 200


@app.route('/api/users/me/attempts', methods=['POST'])
@login_required
def save_attempt():
    data = request.get_json() or {}
    question_id = data.get('question_id')
    if not question_id:
        return jsonify({'error': 'question_id é obrigatório'}), 400
    return check_answer(question_id)


@app.route('/api/users/me/profile', methods=['PUT'])
@login_required
def update_profile():
    gamer = request.current_user
    data = request.get_json() or {}

    if data.get('email'):
        existing = Gamer.query.filter_by(email=data['email']).first()
        if existing and existing.id != gamer.id:
            return jsonify({'error': 'Email já está em uso'}), 400
        gamer.email = data['email']

    if data.get('password') or data.get('senha'):
        senha = data.get('password') or data.get('senha')
        gamer.password_hash = generate_password_hash(senha)

    db.session.commit()
    return jsonify({'message': 'Perfil atualizado', 'user': gamer.to_dict(include_email=True)}), 200


@app.route('/api/partidas', methods=['POST'])
@login_required
def salvar_historico_partida():
    gamer = request.current_user
    data = request.get_json() or {}

    partida = Partida(
        gamer_id=gamer.id,
        tipo=data.get('tipo', 'daily'),
        status=data.get('status', 'finalizada'),
        origem=data.get('origem', 'frontend'),
        data_referencia=get_brazil_today(),
        iniciada_em=datetime.utcnow(),
        finalizada_em=datetime.utcnow(),
        questoes_previstas=data.get('questoes_previstas', 4),
        questoes_respondidas=data.get('questoes_respondidas', 0),
        questoes_acertadas=data.get('questoes_acertadas', 0),
        tempo_total_segundos=data.get('tempo_total_segundos', 0),
        pontuacao_total=data.get('pontos_ganhos', data.get('pontuacao_total', 0)),
        missao_concluida=data.get('missao_concluida', False),
        ofensiva_gerada=data.get('ofensiva_gerada', False)
    )

    db.session.add(partida)
    db.session.commit()

    return jsonify({
        'message': 'Partida salva com sucesso!',
        'partida_id': partida.id
    }), 201


@app.route('/api/ranking', methods=['GET'])
def get_ranking():
    gamers = Gamer.query.all()
    ranking = []

    fuso_br = timezone(timedelta(hours=-3))
    hoje = datetime.now(fuso_br).date()

    for g in gamers:
        stats = g.estatisticas
        total_respondidas = stats.total_respondidas if stats else 0
        total_acertos = stats.total_acertos if stats else 0
        pontuacao_total = stats.pontuacao_total if stats else 0
        recorde_ofensiva = stats.recorde_ofensiva if stats else 0
        ofensiva_atual = stats.ofensiva_atual if stats else 0
        data_ultima = stats.data_ultima_missao_concluida if stats else None

        accuracy = (total_acertos / total_respondidas * 100) if total_respondidas > 0 else 0

        ofensiva_real = ofensiva_atual
        if data_ultima and (hoje - data_ultima).days > 1:
            ofensiva_real = 0

        ranking.append({
            'user_id': g.id,
            'nickname': g.nome,
            'total_quizzes': total_respondidas,
            'correct_answers': total_acertos,
            'accuracy': round(accuracy, 2),
            'total_score': pontuacao_total,
            'ofensiva': ofensiva_real,
            'recorde_ofensiva': recorde_ofensiva
        })

    ranking.sort(key=lambda x: (x['total_score'], x['accuracy'], x['correct_answers']), reverse=True)

    for i, entry in enumerate(ranking, 1):
        entry['position'] = i

    return jsonify(ranking), 200


@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json() or {}
    email = data.get('email')

    if not email:
        return jsonify({'message': 'E-mail é obrigatório'}), 400

    gamer = Gamer.query.filter_by(email=email).first()
    if not gamer:
        return jsonify({'message': 'Se o e-mail estiver cadastrado, você receberá um link de recuperação.'}), 200

    token = secrets.token_urlsafe(32)
    gamer.reset_token = token
    gamer.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
    db.session.commit()

    sender_email = "play@provapop.com.br"
    sender_password = os.getenv("ZOHO_APP_PASSWORD")

    if not sender_password:
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
            <h2>Olá, {gamer.nome}! 🎮</h2>
            <p>Recebemos um pedido para redefinir a senha da sua conta no <strong>ProvaPop!</strong>.</p>
            <p>Para criar uma nova senha, clique no botão abaixo (este link expira em 1 hora):</p>
            <a href="{reset_link}" style="display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">Redefinir Minha Senha</a>
            <p style="margin-top: 30px; font-size: 12px; color: #777;">Se você não solicitou esta alteração, pode ignorar este e-mail tranquilamente.</p>
        </div>
      </body>
    </html>
    """
    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP_SSL("smtp.zoho.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())
    except Exception:
        return jsonify({'message': 'Erro ao tentar enviar o e-mail. Tente novamente mais tarde.'}), 500

    return jsonify({'message': 'Se o e-mail estiver cadastrado, você receberá um link de recuperação.'}), 200


@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json() or {}
    token = data.get('token')
    new_password = data.get('new_password')

    if not token or not new_password:
        return jsonify({'message': 'Token e nova senha são obrigatórios'}), 400

    gamer = Gamer.query.filter_by(reset_token=token).first()

    if not gamer or not gamer.reset_token_expiry or gamer.reset_token_expiry < datetime.utcnow():
        return jsonify({'message': 'Link inválido ou expirado. Por favor, solicite a recuperação novamente.'}), 400

    gamer.password_hash = generate_password_hash(new_password)
    gamer.reset_token = None
    gamer.reset_token_expiry = None
    db.session.commit()

    return jsonify({'message': 'Senha redefinida com sucesso! Você já pode voltar a jogar.'}), 200


@app.route('/api/questoes-do-dia', methods=['GET'])
@optional_auth
def get_questoes_do_dia():
    debug_auth_context("QUESTOES_DO_DIA_ROUTE_ENTERED")

    try:
        hoje = get_brazil_today()
        gamer = request.current_user if hasattr(request, 'current_user') else None

        def format_questions(questoes):
            return [serialize_question_with_user_context(q, gamer) for q in questoes]

        questoes_hoje = Questao.query.filter_by(data_exibicao=hoje, ativo=True).all()

        if questoes_hoje and len(questoes_hoje) >= 4:
            partida_id = None
            if gamer:
                partida = get_or_create_daily_partida(gamer.id, origem='questoes_do_dia_oficial')
                partida_id = partida.id

            return jsonify({
                "status": "sucesso",
                "data": str(hoje),
                "modo": "oficial",
                "partida_id": partida_id,
                "questoes": format_questions(questoes_hoje)
            }), 200

        questoes_ineditas = Questao.query.filter(
            Questao.data_exibicao.is_(None),
            Questao.ativo.is_(True)
        ).limit(4).all()

        if questoes_ineditas and len(questoes_ineditas) >= 4:
            for q in questoes_ineditas:
                q.data_exibicao = hoje
            db.session.commit()

            partida_id = None
            if gamer:
                partida = get_or_create_daily_partida(gamer.id, origem='questoes_do_dia_piloto')
                partida_id = partida.id

            return jsonify({
                "status": "sucesso",
                "data": str(hoje),
                "modo": "piloto-automatico",
                "partida_id": partida_id,
                "questoes": format_questions(questoes_ineditas)
            }), 200

        questoes_antigas = Questao.query.filter(
            Questao.data_exibicao.is_not(None),
            Questao.data_exibicao != hoje,
            Questao.ativo.is_(True)
        ).all()

        if questoes_antigas and len(questoes_antigas) >= 4:
            questoes_flashback = random.sample(questoes_antigas, 4)

            partida_id = None
            if gamer:
                partida = get_or_create_daily_partida(gamer.id, origem='questoes_do_dia_flashback')
                partida_id = partida.id

            return jsonify({
                "status": "sucesso",
                "data": str(hoje),
                "modo": "flashback",
                "partida_id": partida_id,
                "questoes": format_questions(questoes_flashback)
            }), 200

        return jsonify({
            "status": "vazio",
            "mensagem": "Sem questões suficientes. Aguardando o Diretor!"
        }), 200

    except Exception as e:
        erro_detalhado = traceback.format_exc()
        app.logger.error(f'Erro ao buscar questoes do dia: {erro_detalhado}')
        return jsonify({
            "erro_critico": str(e),
            "dica": "Olhe o detalhe abaixo para saber a linha do erro",
            "erro_detalhado": erro_detalhado
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
