# Configuração CORS

## Backend (Flask)

A configuração CORS está configurada para permitir requisições do frontend com suporte a cookies e credenciais.

### Configuração Atual

- **supports_credentials**: `True` - Permite envio de cookies
- **origins**: Configurável via variável de ambiente `CORS_ORIGINS`
- **methods**: GET, POST, PUT, DELETE, OPTIONS
- **allow_headers**: Content-Type, Authorization, X-Requested-With
- **expose_headers**: Content-Type, Authorization
- **max_age**: 3600 segundos (1 hora)

### Variáveis de Ambiente

No arquivo `.env` do backend:

```env
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,http://localhost:3000
```

Para produção, adicione a URL do seu frontend:

```env
CORS_ORIGINS=https://seu-dominio.com,https://www.seu-dominio.com
```

## Frontend (Vite)

### Configuração Atual

- **credentials**: `include` - Envia cookies em todas as requisições
- **mode**: `cors` - Modo CORS explícito
- **headers**: Content-Type e Accept configurados

### Proxy do Vite (Opcional)

O Vite está configurado com proxy para `/api` que redireciona para `http://localhost:5000`. Isso permite usar URLs relativas no frontend.

### Variáveis de Ambiente

No arquivo `.env` do frontend (raiz do projeto):

```env
VITE_API_URL=http://localhost:5000/api
```

Para produção:

```env
VITE_API_URL=https://api.seu-dominio.com/api
```

## Cookies

Os cookies de autenticação são configurados com:
- **httponly**: `True` - Não acessível via JavaScript (segurança)
- **samesite**: `Lax` - Proteção CSRF
- **secure**: `False` (desenvolvimento) / `True` (produção com HTTPS)
- **path**: `/` - Disponível em todas as rotas

## Testando a Configuração

1. Inicie o backend:
```bash
cd backend
python app.py
```

2. Inicie o frontend:
```bash
npm run dev
```

3. Teste o login - os cookies devem ser enviados automaticamente

## Troubleshooting

### Erro: "CORS policy blocked"

- Verifique se a URL do frontend está na lista de `CORS_ORIGINS`
- Certifique-se de que `supports_credentials=True` está configurado
- Verifique se o frontend está usando `credentials: 'include'`

### Cookies não são enviados

- Verifique se `credentials: 'include'` está nas requisições fetch
- Certifique-se de que o backend está configurado com `supports_credentials=True`
- Verifique se as URLs do frontend e backend correspondem (mesmo domínio ou CORS configurado)

### Preflight requests falhando

- O CORS está configurado para aceitar OPTIONS requests
- Verifique se os headers permitidos incluem os que você está usando