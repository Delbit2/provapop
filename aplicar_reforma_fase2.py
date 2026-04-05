with open('backend/app.py', 'r') as f:
    content = f.read()

# 1. Registrar a data/hora do Login
login_antigo = """    from auth import generate_token
    token = generate_token(user.id, app.config['SECRET_KEY'], expires_in=3600 * 24)"""

login_novo = """    # Registrar último login
    user.last_login = datetime.now()
    db.session.commit()

    from auth import generate_token
    token = generate_token(user.id, app.config['SECRET_KEY'], expires_in=3600 * 24)"""

content = content.replace(login_antigo, login_novo)

# 2. Atualizar Tempo de Jogo e Ofensiva (na rota check_answer)
check_antigo = """        # Atualizar pontuação total do usuário (garantindo que nunca fique negativa)
        user.update_score(points)
        
        points_earned = True"""

check_novo = """        # Atualizar pontuação total do usuário (garantindo que nunca fique negativa)
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
        
        points_earned = True"""

content = content.replace(check_antigo, check_novo)

# 3. Atualizar Tempo de Jogo e Ofensiva (na rota save_attempt)
attempt_antigo = """    # Atualizar pontuação total do usuário (garantindo que nunca fique negativa)
    user.update_score(points)
    
    attempt = QuizAttempt("""

attempt_novo = """    # Atualizar pontuação total do usuário (garantindo que nunca fique negativa)
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
    
    attempt = QuizAttempt("""

content = content.replace(attempt_antigo, attempt_novo)

with open('backend/app.py', 'w') as f:
    f.write(content)

print("✅ Lógicas de Ofensiva e Tempo inseridas no app.py com sucesso!")
