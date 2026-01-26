# Troubleshooting Nginx - Erro "unknown directive GNU"

## Problema

O erro `unknown directive "GNU"` geralmente ocorre quando há um cabeçalho de licença ou comentário mal formatado no arquivo de configuração do nginx.

## Solução Rápida

### Opção 1: Remover o arquivo default (Recomendado)

Se você vai usar apenas a configuração do projeto, pode remover o arquivo default:

```bash
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
```

### Opção 2: Corrigir o arquivo default

1. Edite o arquivo:
```bash
sudo nano /etc/nginx/sites-enabled/default
```

2. Procure por linhas que contenham "GNU" ou cabeçalhos de licença (geralmente no início do arquivo)

3. Remova essas linhas ou comente-as com `#`

4. Certifique-se de que o arquivo começa com uma diretiva válida do nginx, como:
```nginx
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    # ... resto da configuração
}
```

### Opção 3: Verificar o conteúdo do arquivo

```bash
# Ver as primeiras 30 linhas
sudo head -30 /etc/nginx/sites-enabled/default

# Ver a linha 22 especificamente (onde está o erro)
sudo sed -n '22p' /etc/nginx/sites-enabled/default

# Ver todo o arquivo
sudo cat /etc/nginx/sites-enabled/default
```

## Depois de corrigir

1. Teste a configuração:
```bash
sudo nginx -t
```

2. Se estiver OK, recarregue o nginx:
```bash
sudo systemctl reload nginx
```

## Configuração Recomendada

Para este projeto, recomendo usar apenas a configuração customizada:

```bash
# 1. Remover o default
sudo rm /etc/nginx/sites-enabled/default

# 2. Copiar nossa configuração
sudo cp /home/debian/enem-brasil/nginx.conf /etc/nginx/sites-available/enem-brasil

# 3. Ajustar o caminho do root no arquivo (edite conforme necessário)
sudo nano /etc/nginx/sites-available/enem-brasil

# 4. Habilitar o site
sudo ln -s /etc/nginx/sites-available/enem-brasil /etc/nginx/sites-enabled/

# 5. Testar
sudo nginx -t

# 6. Recarregar
sudo systemctl reload nginx
```
