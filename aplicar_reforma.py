with open('backend/app.py', 'r') as f:
    content = f.read()

# 1. Adicionando as colunas no modelo de Usuario
colunas_antigas = """    total_score = db.Column(db.Integer, default=0, nullable=False)  # Pontuação total do usuário
    created_at = db.Column(db.DateTime, default=datetime.now)"""

colunas_novas = """    total_score = db.Column(db.Integer, default=0, nullable=False)  # Pontuação total do usuário
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # NOVAS COLUNAS: Radar de Engajamento e Ofensivas
    last_login = db.Column(db.DateTime, nullable=True)
    total_play_time = db.Column(db.Integer, default=0)  # Tempo em segundos
    current_streak = db.Column(db.Integer, default=0)   # Dias seguidos jogando
    last_play_date = db.Column(db.Date, nullable=True)  # Data da última jogada para calcular a ofensiva"""

content = content.replace(colunas_antigas, colunas_novas)

# 2. Atualizando a exportação de dados para o painel
dict_antigo = """            'total_score': self.total_score,  # Garantir que sempre seja >= 0
            'created_at': self.created_at.isoformat()
        }"""

dict_novo = """            'total_score': self.total_score,  # Garantir que sempre seja >= 0
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'total_play_time': self.total_play_time,
            'current_streak': self.current_streak
        }"""

content = content.replace(dict_antigo, dict_novo)

with open('backend/app.py', 'w') as f:
    f.write(content)

print("✅ Cirurgia no app.py realizada com sucesso!")
