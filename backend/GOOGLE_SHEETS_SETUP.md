# Configuração do Google Sheets

## Passo 1: Criar Projeto no Google Cloud Console

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Ative a API do Google Sheets:
   - Vá em "APIs & Services" > "Library"
   - Procure por "Google Sheets API"
   - Clique em "Enable"
   - Procure por "Google Drive API"
   - Clique em "Enable"

## Passo 2: Criar Service Account

1. Vá em "APIs & Services" > "Credentials"
2. Clique em "Create Credentials" > "Service Account"
3. Preencha:
   - Service account name: `quiz-musical`
   - Service account ID: será gerado automaticamente
   - Clique em "Create and Continue"
4. Pule a etapa de "Grant this service account access to project" (opcional)
5. Clique em "Done"

## Passo 3: Criar e Baixar Credentials

1. Na lista de Service Accounts, clique no que você criou
2. Vá na aba "Keys"
3. Clique em "Add Key" > "Create new key"
4. Selecione "JSON"
5. Clique em "Create"
6. O arquivo JSON será baixado automaticamente
7. Renomeie o arquivo para `credentials.json`
8. Coloque o arquivo na pasta `backend/`

## Passo 4: Criar Planilha no Google Sheets

1. Acesse [Google Sheets](https://sheets.google.com/)
2. Crie uma nova planilha
3. Copie o link da planilha (URL completa)
4. Exemplo: `https://docs.google.com/spreadsheets/d/1ABC123.../edit#gid=0`

## Passo 5: Compartilhar Planilha com Service Account

1. Na planilha criada, clique em "Share" (Compartilhar)
2. Copie o email do Service Account (está no arquivo `credentials.json`, campo `client_email`)
3. Cole o email no campo de compartilhamento
4. Dê permissão de "Editor"
5. Clique em "Send"

## Passo 6: Configurar Variáveis de Ambiente

Crie ou edite o arquivo `.env` na pasta `backend/`:

```env
GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/SEU_SHEET_ID_AQUI/edit
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEETS_WORKSHEET_NAME=Ranking
```

Substitua `SEU_SHEET_ID_AQUI` pelo ID da sua planilha (extraído da URL).

## Estrutura da Planilha

A planilha será criada automaticamente com as seguintes colunas:

| ID | Apelido | Email | Total de Quizzes | Respostas Corretas | Taxa de Acerto (%) | Posição | Última Atualização |
|----|---------|-------|------------------|---------------------|---------------------|---------|-------------------|

## Endpoints Disponíveis

- `POST /api/sheets/sync-user` - Sincroniza dados do usuário atual
- `POST /api/sheets/sync-ranking` - Sincroniza todo o ranking
- `GET /api/sheets/test` - Testa a conexão com Google Sheets

## Sincronização Automática

Os dados são sincronizados automaticamente quando:
- Um novo usuário se registra
- Um usuário responde uma questão
- Um usuário atualiza seu perfil

## Notas Importantes

- O arquivo `credentials.json` contém informações sensíveis - NÃO commite no Git
- Mantenha o arquivo seguro e não compartilhe
- A planilha será atualizada automaticamente conforme os usuários interagem com o sistema