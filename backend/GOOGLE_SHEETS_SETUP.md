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

**⚠️ IMPORTANTE:** 
- Um arquivo `credentials.json` de exemplo foi criado na pasta `backend/` com a estrutura esperada
- **SUBSTITUA** todos os valores marcados com `SUBSTITUA_...` pelos valores reais do arquivo JSON baixado do Google Cloud Console
- **OU** simplesmente substitua o conteúdo do arquivo `credentials.json` pelo conteúdo completo do arquivo JSON baixado
- O arquivo `credentials.json` está no `.gitignore` e não será commitado no Git

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

## Trocar de Planilha ou Conta Google

### Trocar de Planilha

1. **Criar nova planilha** no Google Sheets
2. **Compartilhar** a nova planilha com o email da Service Account (mesmo email do `credentials.json`)
3. **Atualizar** a variável `GOOGLE_SHEETS_URL` no arquivo `.env`:
   ```env
   GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/NOVO_SHEET_ID/edit
   ```
4. **Reiniciar** o servidor Flask

**⚠️ Importante:** Os dados antigos permanecerão na planilha antiga. Apenas novos dados serão sincronizados na nova planilha.

### Trocar de Conta Google (Service Account)

1. **Criar nova Service Account** no Google Cloud Console
2. **Baixar novo arquivo** `credentials.json`
3. **Compartilhar a planilha** com o email da NOVA Service Account
4. **Atualizar** a variável `GOOGLE_SHEETS_CREDENTIALS_FILE` no arquivo `.env` (se usar nome diferente):
   ```env
   GOOGLE_SHEETS_CREDENTIALS_FILE=credentials-nova.json
   ```
5. **Substituir** o arquivo `credentials.json` ou usar o novo arquivo
6. **Reiniciar** o servidor Flask

**⚠️ Importante:** A nova Service Account precisa ter acesso à planilha (compartilhamento).

### Trocar de Worksheet (Aba)

1. **Atualizar** a variável `GOOGLE_SHEETS_WORKSHEET_NAME` no arquivo `.env`:
   ```env
   GOOGLE_SHEETS_WORKSHEET_NAME=NomeDaNovaAba
   ```
2. **Reiniciar** o servidor Flask

**⚠️ Importante:** Se a worksheet não existir, será criada automaticamente. Dados antigos permanecerão na worksheet anterior.

### Migrar Dados Antigos

Para migrar dados de uma planilha antiga para uma nova:

1. Use o endpoint `/api/sheets/sync-ranking` que sincroniza TODOS os usuários
2. Ou exporte manualmente os dados da planilha antiga e importe na nova