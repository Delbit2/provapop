# Troubleshooting Docker - Enem Brasil

## Problema 1: Erro "database 'enem_user' does not exist"

**Causa:** A variável `DATABASE_URL` está sendo construída incorretamente, usando o nome de usuário como nome do banco.

**Solução:**

1. Verifique se o arquivo `.env` existe na raiz do projeto:
```bash
ls -la .env
```

2. Crie o arquivo `.env` com as variáveis corretas:
```bash
cat > .env << 'EOF'
# Database
POSTGRES_USER=enem_user
POSTGRES_PASSWORD=sua-senha-forte-aqui
POSTGRES_DB=enem_brasil
POSTGRES_PORT=5432

# Flask
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=sua-chave-secreta-aqui

# Google Sheets
GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/SEU_SHEET_ID/edit
GOOGLE_SHEETS_WORKSHEET_NAME=Usuarios

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,http://localhost:3000
EOF
```

3. Recrie os containers:
```bash
docker-compose down -v
docker-compose up -d
```

4. Verifique os logs:
```bash
docker-compose logs backend | grep -i "database\|postgres"
```

## Problema 2: Erro Google Sheets 404 "Requested entity was not found"

**Causas possíveis:**

1. **URL da planilha incorreta**
   - Verifique se o `GOOGLE_SHEETS_URL` está correto no `.env`
   - A URL deve ser: `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`
   - O `SHEET_ID` é a parte longa entre `/d/` e `/edit`

2. **credentials.json não está montado**
   ```bash
   # Verificar se o arquivo existe
   ls -la backend/credentials.json
   
   # Verificar se está montado no container
   docker-compose exec backend ls -la /app/credentials.json
   ```

3. **Service Account não tem acesso à planilha**
   - Abra o arquivo `backend/credentials.json`
   - Copie o email do Service Account (campo `client_email`)
   - Compartilhe a planilha do Google Sheets com esse email
   - Dê permissão de "Editor" ou "Visualizador"

4. **Worksheet name incorreto**
   - Verifique o nome da aba na planilha
   - Confirme que `GOOGLE_SHEETS_WORKSHEET_NAME` no `.env` corresponde ao nome exato da aba

**Solução passo a passo:**

```bash
# 1. Verificar variáveis de ambiente no container
docker-compose exec backend env | grep GOOGLE

# 2. Verificar se credentials.json está acessível
docker-compose exec backend cat /app/credentials.json | head -5

# 3. Testar conexão manualmente (dentro do container)
docker-compose exec backend python3 -c "
from google_sheets import get_google_sheets_client
client = get_google_sheets_client()
print('Cliente criado com sucesso')
"

# 4. Verificar logs detalhados
docker-compose logs backend | grep -i "google\|sheet\|sync"
```

## Problema 3: Migrations não rodam

**Solução:**

```bash
# Executar migrations manualmente
docker-compose exec backend flask db upgrade

# Ver status das migrations
docker-compose exec backend flask db current

# Ver histórico
docker-compose exec backend flask db history
```

## Problema 4: Container não inicia

**Verificar:**

1. **Logs do container:**
```bash
docker-compose logs backend
```

2. **Status dos containers:**
```bash
docker-compose ps
```

3. **Rebuild da imagem:**
```bash
docker-compose build --no-cache backend
docker-compose up -d
```

## Comandos Úteis de Debug

```bash
# Ver todas as variáveis de ambiente do backend
docker-compose exec backend env

# Acessar shell do container
docker-compose exec backend bash

# Ver logs em tempo real
docker-compose logs -f backend

# Reiniciar apenas o backend
docker-compose restart backend

# Parar tudo e limpar volumes
docker-compose down -v

# Verificar conexão com banco
docker-compose exec backend python3 -c "
from app import app, db
with app.app_context():
    db.engine.connect()
    print('Conexão OK')
"
```

## Checklist de Configuração

- [ ] Arquivo `.env` existe na raiz com todas as variáveis
- [ ] `POSTGRES_DB` está definido (não usar o mesmo nome de `POSTGRES_USER`)
- [ ] `GOOGLE_SHEETS_URL` está correto (com o SHEET_ID)
- [ ] `backend/credentials.json` existe e está válido
- [ ] Service Account tem acesso à planilha
- [ ] `GOOGLE_SHEETS_WORKSHEET_NAME` corresponde ao nome da aba
- [ ] Containers estão rodando: `docker-compose ps`
- [ ] Banco está saudável: `docker-compose logs db | grep "ready to accept"`
