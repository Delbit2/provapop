# Quiz Musical API

Backend Flask para o aplicativo Quiz Musical.

## Instalação

1. Crie um ambiente virtual:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o .env com suas configurações
```

4. Inicialize o banco de dados:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

5. Execute o servidor:
```bash
python app.py
```

O servidor estará disponível em `http://localhost:5000`

## Endpoints da API

### Health Check
- `GET /api/health` - Verifica se a API está funcionando

### Questões
- `GET /api/questions` - Lista todas as questões
- `GET /api/questions/<id>` - Obtém uma questão específica (sem resposta correta)
- `GET /api/questions/random` - Obtém uma questão aleatória
- `POST /api/questions/<id>/check` - Verifica se a resposta está correta

### Usuários
- `POST /api/users/register` - Registra um novo usuário
- `POST /api/users/login` - Faz login
- `GET /api/users/<id>/stats` - Obtém estatísticas do usuário
- `POST /api/users/<id>/attempts` - Salva uma tentativa de resposta

### Ranking
- `GET /api/ranking` - Obtém o ranking de usuários

## Estrutura do Banco de Dados

- **users**: Usuários do sistema
- **questions**: Questões do quiz
- **quiz_attempts**: Tentativas de resposta dos usuários