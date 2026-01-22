# Troubleshooting - Google Sheets Sincronização

## Problema: Planilha está vazia (apenas colunas, sem dados)

### 1. Verificar Configuração Básica

Execute o script de teste:
```bash
cd backend
python3 test_sync.py
```

Este script vai verificar:
- ✅ Se o arquivo `credentials.json` existe
- ✅ Se a URL da planilha está configurada
- ✅ Se a conexão com Google Sheets funciona
- ✅ Se há usuários no banco de dados
- ✅ Se a sincronização funciona

### 2. Verificar Compartilhamento da Planilha

**⚠️ CRÍTICO:** A planilha DEVE estar compartilhada com o email da Service Account!

1. Abra o arquivo `credentials.json`
2. Copie o valor do campo `"client_email"` (algo como: `quiz-musical@projeto.iam.gserviceaccount.com`)
3. Abra sua planilha do Google Sheets
4. Clique em **"Share"** (Compartilhar)
5. Cole o email da Service Account
6. Dê permissão de **"Editor"**
7. Clique em **"Send"**

**Sem este passo, a sincronização NÃO funcionará!**

### 3. Verificar Variáveis de Ambiente

Verifique se o arquivo `.env` na pasta `backend/` contém:

```env
GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/SEU_SHEET_ID/edit
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEETS_WORKSHEET_NAME=Ranking
```

**Importante:** 
- A URL deve ser a URL completa da planilha
- O nome da worksheet deve corresponder ao nome da aba na planilha

### 4. Verificar Logs do Servidor

Quando o servidor Flask está rodando, os logs mostrarão informações sobre a sincronização:

```bash
cd backend
python3 app.py
```

Procure por mensagens como:
- `Starting sync for user_id: X`
- `Successfully synced user X to Google Sheets`
- Ou mensagens de erro

### 5. Testar Sincronização Manual

Você pode testar a sincronização manualmente através da API:

**Sincronizar um usuário específico:**
```bash
curl -X POST http://localhost:5000/api/sheets/sync-user \
  -H "Cookie: access_token=SEU_TOKEN"
```

**Sincronizar todo o ranking:**
```bash
curl -X POST http://localhost:5000/api/sheets/sync-ranking \
  -H "Cookie: access_token=SEU_TOKEN"
```

### 6. Verificar se Há Usuários no Banco de Dados

A sincronização só funciona se houver usuários cadastrados:

```bash
cd backend
python3 -c "from app import app, db, User; app.app_context().push(); print(f'Usuários: {User.query.count()}')"
```

### 7. Problemas Comuns

#### Erro: "Credentials file not found"
- ✅ Verifique se o arquivo `credentials.json` está na pasta `backend/`
- ✅ Verifique se o nome do arquivo está correto no `.env`

#### Erro: "Invalid Google Sheets URL"
- ✅ Verifique se a URL está completa (não apenas o ID)
- ✅ A URL deve ter o formato: `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`

#### Erro: "Google Sheets API error: 403"
- ✅ A planilha não está compartilhada com a Service Account
- ✅ A Service Account não tem permissão de Editor
- ✅ As APIs não estão ativadas no Google Cloud Console

#### Erro: "Worksheet not found"
- ✅ Verifique se o nome da worksheet no `.env` corresponde ao nome da aba na planilha
- ✅ A worksheet será criada automaticamente se não existir

#### Dados não aparecem na planilha
- ✅ Verifique os logs do servidor para ver se há erros
- ✅ Execute o script `test_sync.py` para diagnosticar
- ✅ Verifique se a planilha está compartilhada corretamente
- ✅ Verifique se há usuários no banco de dados

### 8. Forçar Sincronização Completa

Se os dados não estão aparecendo, você pode forçar uma sincronização completa:

```bash
cd backend
python3 -c "
from app import app, db
from google_sheets import sync_ranking_to_sheets
with app.app_context():
    result = sync_ranking_to_sheets()
    print(result)
"
```

### 9. Verificar Estrutura da Planilha

A planilha deve ter estas colunas (criadas automaticamente):
- ID
- Apelido
- Email
- Total de Quizzes
- Respostas Corretas
- Taxa de Acerto (%)
- Posição
- Última Atualização

Se as colunas estão diferentes, pode haver um problema na criação da worksheet.

### 10. Contato e Suporte

Se nenhuma das soluções acima funcionar:
1. Execute `python3 test_sync.py` e copie a saída completa
2. Verifique os logs do servidor Flask
3. Verifique se a planilha está compartilhada corretamente
4. Verifique se as APIs estão ativadas no Google Cloud Console
