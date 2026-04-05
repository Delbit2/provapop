# ProvaPoP API

Backend Flask para o aplicativo ProvaPoP.

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

### Autenticação
- `POST /api/auth/register` - Registra um novo usuário
- `POST /api/auth/login` - Faz login
- `POST /api/auth/logout` - Faz logout
- `GET /api/auth/me` - Obtém informações do usuário autenticado
- `GET /api/auth/verify` - Verifica se está autenticado

### Questões
- `GET /api/questions` - Lista todas as questões
- `GET /api/questions/<id>` - Obtém uma questão específica (sem resposta correta)
- `GET /api/questions/random` - Obtém uma questão aleatória
- `POST /api/questions/<id>/check` - Verifica se a resposta está correta (requer autenticação)

### Usuários
- `GET /api/users/me/stats` - Obtém estatísticas do usuário autenticado
- `POST /api/users/me/attempts` - Salva uma tentativa de resposta
- `PUT /api/users/me/profile` - Atualiza perfil do usuário

### Ranking
- `GET /api/ranking` - Obtém o ranking de usuários

### Google Sheets
- `POST /api/sheets/sync-user` - Sincroniza dados do usuário atual com Google Sheets
- `POST /api/sheets/sync-ranking` - Sincroniza todo o ranking com Google Sheets
- `GET /api/sheets/test` - Testa a conexão com Google Sheets

## Integração com Google Sheets

O sistema está configurado para sincronizar automaticamente dados com Google Sheets. Veja o arquivo `GOOGLE_SHEETS_SETUP.md` para instruções detalhadas de configuração.

## Estrutura do Banco de Dados

- **users**: Usuários do sistema
- **questions**: Questões do quiz
- **quiz_attempts**: Tentativas de resposta dos usuários