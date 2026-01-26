# Configuração Nginx para Enem Brasil

Este guia explica como configurar o Nginx para servir a aplicação Vue.js e fazer proxy reverso para a API do backend.

## Pré-requisitos

- Nginx instalado
- Build do Vue.js executado (`npm run build`)
- Backend Flask rodando (porta 5000 por padrão)

## Passo a Passo

### 1. Fazer o build do Vue.js

```bash
npm run build
```

Isso criará o diretório `dist/` com os arquivos estáticos.

### 2. Copiar arquivos para o servidor

```bash
# Criar diretório (ajuste o caminho conforme necessário)
sudo mkdir -p /var/www/enem-brasil

# Copiar arquivos do build
sudo cp -r dist/* /var/www/enem-brasil/dist/

# Ajustar permissões
sudo chown -R www-data:www-data /var/www/enem-brasil
sudo chmod -R 755 /var/www/enem-brasil
```

### 3. Configurar Nginx

```bash
# Copiar configuração
sudo cp nginx.conf /etc/nginx/sites-available/enem-brasil

# Editar configuração (ajuste server_name e root conforme necessário)
sudo nano /etc/nginx/sites-available/enem-brasil

# Habilitar site
sudo ln -s /etc/nginx/sites-available/enem-brasil /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Recarregar Nginx
sudo systemctl reload nginx
```

### 4. Ajustar configurações importantes

No arquivo `nginx.conf`, ajuste:

- **server_name**: Seu domínio ou IP
  ```nginx
  server_name seu-dominio.com;
  ```

- **root**: Caminho absoluto para o diretório dist/
  ```nginx
  root /var/www/enem-brasil/dist;
  ```

- **proxy_pass**: Porta do backend (se diferente de 5000)
  ```nginx
  proxy_pass http://localhost:5000;
  ```

## Configuração para Produção com SSL

Para produção, adicione configuração SSL:

```nginx
server {
    listen 443 ssl http2;
    server_name seu-dominio.com;
    
    ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;
    
    # ... resto da configuração
}

# Redirecionar HTTP para HTTPS
server {
    listen 80;
    server_name seu-dominio.com;
    return 301 https://$server_name$request_uri;
}
```

## Verificar se está funcionando

1. Acesse `http://seu-dominio.com` (ou `http://localhost` em desenvolvimento)
2. Verifique os logs:
   ```bash
   sudo tail -f /var/log/nginx/enem-brasil-access.log
   sudo tail -f /var/log/nginx/enem-brasil-error.log
   ```

## Troubleshooting

### Erro 502 Bad Gateway
- Verifique se o backend está rodando na porta correta
- Verifique se o proxy_pass está correto

### Erro 404 em rotas do Vue Router
- Certifique-se de que `try_files $uri $uri/ /index.html;` está configurado

### Arquivos estáticos não carregam
- Verifique as permissões do diretório dist/
- Verifique se o caminho do `root` está correto

### CORS errors
- O proxy reverso deve resolver isso, mas verifique se o backend está configurado corretamente

## Estrutura da Configuração

A configuração inclui:

1. **Servir arquivos estáticos**: HTML, JS, CSS do build Vue.js
2. **Proxy reverso**: `/api` → backend Flask (porta 5000)
3. **Vue Router**: Redireciona todas as rotas para `index.html` (history mode)
4. **Compressão gzip**: Para melhor performance
5. **Cache**: Arquivos estáticos com cache longo
6. **Headers de segurança**: XSS, frame options, etc.
