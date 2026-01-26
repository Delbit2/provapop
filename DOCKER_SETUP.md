# Docker Setup - Enem Brasil

Este guia explica como configurar e executar a aplicação backend usando Docker e Docker Compose.

## Pré-requisitos

- Docker instalado
- Docker Compose instalado
- Arquivo `credentials.json` do Google Sheets (se usar sincronização)

## Configuração Inicial

### 1. Criar arquivo .env

Copie o arquivo de exemplo e ajuste as variáveis:

```bash
cp .env.example .env
nano .env
```

**Variáveis importantes:**
- `SECRET_KEY`: Gere uma chave secreta aleatória para produção
- `POSTGRES_PASSWORD`: Senha forte para o banco de dados
- `GOOGLE_SHEETS_URL`: URL da planilha do Google Sheets
- `CORS_ORIGINS`: URLs permitidas para CORS (separadas por vírgula)

### 2. Configurar credentials.json

Coloque o arquivo `credentials.json` do Google Sheets na pasta `backend/`:

```bash
cp /caminho/para/seu/credentials.json backend/credentials.json
```

## Executando a Aplicação

### Iniciar todos os serviços

```bash
docker-compose up -d
```

### Ver logs

```bash
# Todos os serviços
docker-compose logs -f

# Apenas backend
docker-compose logs -f backend

# Apenas banco de dados
docker-compose logs -f db
```

### Parar os serviços

```bash
docker-compose down
```

### Parar e remover volumes (apaga dados do banco)

```bash
docker-compose down -v
```

## Comandos Úteis

### Executar migrations manualmente

```bash
docker-compose exec backend flask db upgrade
```

### Criar nova migration

```bash
docker-compose exec backend flask db migrate -m "Descrição da migration"
```

### Acessar shell do backend

```bash
docker-compose exec backend bash
```

### Acessar banco de dados PostgreSQL

```bash
docker-compose exec db psql -U enem_user -d enem_brasil
```

### Rebuild da imagem

```bash
docker-compose build --no-cache backend
docker-compose up -d
```

## Estrutura

```
enem-brasil/
├── backend/
│   ├── Dockerfile
│   ├── credentials.json  # (não commitado)
│   ├── app.py
│   └── ...
├── docker-compose.yml
├── .env                  # (não commitado)
└── .env.example
```

## Troubleshooting

### Erro: "credentials.json not found"

Certifique-se de que o arquivo existe em `backend/credentials.json`:

```bash
ls -la backend/credentials.json
```

### Erro: "Database connection failed"

1. Verifique se o serviço `db` está rodando:
   ```bash
   docker-compose ps
   ```

2. Verifique os logs do banco:
   ```bash
   docker-compose logs db
   ```

3. Verifique as variáveis de ambiente no `.env`

### Erro: "Port already in use"

Altere a porta no `.env`:

```bash
BACKEND_PORT=5001
POSTGRES_PORT=5433
```

### Resetar banco de dados

```bash
# Parar serviços
docker-compose down

# Remover volume do banco
docker volume rm enem-brasil_postgres_data

# Iniciar novamente
docker-compose up -d
```

## Produção

Para produção, considere:

1. **Usar Gunicorn com mais workers:**
   ```yaml
   command: gunicorn --bind 0.0.0.0:5000 --workers 8 --timeout 120 app:app
   ```

2. **Configurar SSL/TLS** (usando nginx como reverse proxy)

3. **Backup automático do banco de dados**

4. **Monitoramento** (logs, métricas)

5. **Variáveis de ambiente seguras** (usar secrets do Docker ou serviço de secrets)

## Desenvolvimento

Para desenvolvimento local sem Docker:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run
```
