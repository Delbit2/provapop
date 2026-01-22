# Sincronização Automática de Questões

## Visão Geral

O sistema agora possui sincronização automática de questões da planilha Google Sheets. Isso significa que você **não precisa mais executar scripts manualmente** - o backend verifica automaticamente a planilha em intervalos regulares e adiciona novas questões ao banco de dados.

## Como Funciona

1. **Thread em Background**: Uma thread separada roda continuamente em background
2. **Verificação Periódica**: A planilha é verificada automaticamente a cada X minutos
3. **Adição Automática**: Novas questões completas são automaticamente adicionadas ao banco
4. **Validação Completa**: Apenas questões com todas as colunas preenchidas são sincronizadas

## Configuração

### Variável de Ambiente (Opcional)

Você pode configurar o intervalo de sincronização através da variável de ambiente:

```bash
# Sincronizar a cada 5 minutos (padrão)
QUESTIONS_SYNC_INTERVAL=300

# Sincronizar a cada 10 minutos
QUESTIONS_SYNC_INTERVAL=600

# Sincronizar a cada 1 minuto (para testes)
QUESTIONS_SYNC_INTERVAL=60
```

**Valor padrão**: 300 segundos (5 minutos)

### Requisitos

Para que a sincronização automática funcione, você precisa ter configurado:

1. ✅ `GOOGLE_SHEETS_URL` no arquivo `.env` ou variável de ambiente
2. ✅ `credentials.json` no diretório do backend
3. ✅ Planilha com a página "Questoes" criada

## Inicialização Automática

A sincronização automática inicia automaticamente quando:

- ✅ O servidor Flask é iniciado
- ✅ O app é executado com `python app.py`
- ✅ O app é executado com gunicorn/uwsgi
- ✅ O app é executado em qualquer servidor WSGI

**Não é necessário fazer nada** - ela inicia sozinha!

## Verificação de Status

### Via API

Você pode verificar o status da sincronização automática através do endpoint:

```bash
GET /api/questions/auto-sync-status
```

Resposta de exemplo:

```json
{
  "enabled": true,
  "running": true,
  "sync_interval_seconds": 300,
  "sync_interval_minutes": 5,
  "sheets_configured": true,
  "message": "Auto-sync is running"
}
```

### Via Logs

Os logs do servidor mostrarão mensagens como:

```
[AUTO-SYNC] Starting automatic questions sync worker (interval: 300s)
[AUTO-SYNC] ✓ Automatic questions sync started successfully
[AUTO-SYNC] Starting automatic sync check...
[AUTO-SYNC] ✓ Sync completed: 2 new question(s) added, 0 skipped
[AUTO-SYNC] Waiting 300s before next sync check...
```

## Comportamento

### Quando uma Nova Questão é Adicionada na Planilha

1. A questão é detectada na próxima verificação automática (máximo 5 minutos)
2. O sistema valida que **todas as colunas estão preenchidas**:
   - ID
   - Autor
   - Titulo
   - Trecho_Letra
   - Enunciado
   - A, B, C, D, E (todas as alternativas)
   - Alternativa_Correta
   - Musica_Drive
3. Se todas as colunas estiverem preenchidas, a questão é adicionada
4. Se alguma coluna estiver vazia, a questão é ignorada e um aviso é registrado

### Questões Duplicadas

- Questões com o mesmo `external_id` (ID da planilha) não são duplicadas
- O sistema verifica se a questão já existe antes de adicionar

## Sincronização Manual (Ainda Disponível)

A sincronização manual ainda está disponível se você quiser forçar uma sincronização imediata:

```bash
POST /api/questions/sync
```

**Requer autenticação** (login necessário)

## Troubleshooting

### Sincronização não está funcionando

1. **Verifique os logs**: Procure por mensagens `[AUTO-SYNC]` nos logs do servidor
2. **Verifique a configuração**: Confirme que `GOOGLE_SHEETS_URL` está configurado
3. **Verifique o status**: Use o endpoint `/api/questions/auto-sync-status`
4. **Verifique as credenciais**: Confirme que `credentials.json` existe e está válido

### Questões não estão sendo adicionadas

1. **Verifique se todas as colunas estão preenchidas**: O sistema só adiciona questões completas
2. **Verifique os logs**: Procure por mensagens de aviso sobre campos faltando
3. **Verifique se a questão já existe**: Questões com o mesmo ID não são duplicadas

### Intervalo muito longo/curto

Ajuste a variável de ambiente `QUESTIONS_SYNC_INTERVAL`:

```bash
# No arquivo .env
QUESTIONS_SYNC_INTERVAL=60  # 1 minuto
QUESTIONS_SYNC_INTERVAL=300  # 5 minutos (padrão)
QUESTIONS_SYNC_INTERVAL=600  # 10 minutos
```

**Nota**: Intervalos muito curtos (menos de 60 segundos) podem sobrecarregar a API do Google Sheets.

## Desabilitar Sincronização Automática

Para desabilitar a sincronização automática, simplesmente não configure a `GOOGLE_SHEETS_URL`. O sistema detectará isso e não iniciará a sincronização automática.

## Logs

Todas as operações de sincronização automática são registradas nos logs com o prefixo `[AUTO-SYNC]`:

- `[AUTO-SYNC] Starting...` - Início da sincronização
- `[AUTO-SYNC] ✓ Sync completed` - Sincronização bem-sucedida
- `[AUTO-SYNC] Sync failed` - Erro na sincronização
- `[AUTO-SYNC] Skipping row X` - Linha ignorada (campos faltando)
