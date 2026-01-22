# Como Obter o arquivo credentials.json

## ⚠️ IMPORTANTE
O arquivo `credentials.json` contém credenciais sensíveis e **NÃO pode ser criado manualmente**. Ele deve ser baixado do Google Cloud Console.

## Passos para Obter o credentials.json

### 1. Acesse o Google Cloud Console
- Vá para: https://console.cloud.google.com/
- Faça login com sua conta Google

### 2. Crie ou Selecione um Projeto
- Se não tiver um projeto, clique em "Create Project"
- Dê um nome ao projeto (ex: "quiz-musical")
- Clique em "Create"

### 3. Ative as APIs Necessárias
- Vá em "APIs & Services" > "Library"
- Procure e ative:
  - **Google Sheets API**
  - **Google Drive API**

### 4. Crie uma Service Account
- Vá em "APIs & Services" > "Credentials"
- Clique em "Create Credentials" > "Service Account"
- Preencha:
  - **Service account name**: `quiz-musical` (ou qualquer nome)
  - **Service account ID**: será gerado automaticamente
- Clique em "Create and Continue"
- Pule a etapa de permissões (opcional)
- Clique em "Done"

### 5. Baixe as Credenciais
- Na lista de Service Accounts, clique na que você criou
- Vá na aba **"Keys"**
- Clique em **"Add Key"** > **"Create new key"**
- Selecione **"JSON"**
- Clique em **"Create"**
- O arquivo JSON será **baixado automaticamente** pelo navegador

### 6. Coloque o Arquivo no Projeto
- O arquivo baixado terá um nome como: `seu-projeto-xxxxx-xxxxx.json`
- **Renomeie** o arquivo para: `credentials.json`
- **Mova** o arquivo para a pasta `backend/`

### 7. Compartilhe a Planilha com a Service Account
- Abra o arquivo `credentials.json`
- Copie o valor do campo `"client_email"` (algo como: `quiz-musical@projeto.iam.gserviceaccount.com`)
- Abra sua planilha do Google Sheets
- Clique em **"Share"** (Compartilhar)
- Cole o email da Service Account
- Dê permissão de **"Editor"**
- Clique em **"Send"**

## Estrutura do Arquivo credentials.json

O arquivo baixado terá esta estrutura:

```json
{
  "type": "service_account",
  "project_id": "seu-projeto-id",
  "private_key_id": "chave-id-aleatoria",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "nome@projeto.iam.gserviceaccount.com",
  "client_id": "numero-aleatorio",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

## Verificação

Após colocar o arquivo `credentials.json` na pasta `backend/`, você pode testar a conexão:

```bash
cd backend
python3 -c "from google_sheets import get_client; print('✅ Credenciais válidas!')"
```

Ou use o endpoint de teste do backend:
```
GET http://localhost:5000/api/sheets/test
```

## Segurança

- ✅ O arquivo `credentials.json` está no `.gitignore` e **NÃO será commitado**
- ⚠️ **NUNCA** compartilhe este arquivo publicamente
- ⚠️ **NUNCA** commite este arquivo no Git
- ⚠️ Mantenha este arquivo seguro e privado
