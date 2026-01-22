# Configuração de Áudio do Google Drive

## Como Funciona

O sistema processa automaticamente links do Google Drive da coluna `Musica_Drive` e os converte para links diretos utilizáveis em players de áudio HTML5.

## Formatos de Links Suportados

O sistema suporta os seguintes formatos de links do Google Drive:

1. **Link de visualização/edição:**
   ```
   https://drive.google.com/file/d/FILE_ID/view
   https://drive.google.com/file/d/FILE_ID/edit
   ```

2. **Link com parâmetro ID:**
   ```
   https://drive.google.com/open?id=FILE_ID
   https://drive.google.com/drive/folders/FILE_ID?usp=sharing
   ```

3. **Link direto (já processado):**
   ```
   https://drive.google.com/uc?export=view&id=FILE_ID
   ```

## Conversão Automática

Quando uma questão é sincronizada da planilha, o sistema:

1. Extrai o `FILE_ID` do link fornecido
2. Converte para o formato: `https://drive.google.com/uc?export=view&id=FILE_ID`
3. Armazena o link processado no banco de dados
4. Retorna o link processado na API (método `to_dict()`)

## Uso no Frontend

O campo `music_drive_url` está disponível na resposta da API e pode ser usado diretamente em um elemento `<audio>`:

```html
<audio controls>
  <source :src="question.music_drive_url" type="audio/mpeg">
  Seu navegador não suporta o elemento de áudio.
</audio>
```

## Importante: Configuração do Google Drive

⚠️ **ATENÇÃO**: Para que os links funcionem corretamente, os arquivos de áudio no Google Drive precisam estar configurados com permissão de "Qualquer pessoa com o link pode visualizar".

### Como Configurar:

1. No Google Drive, clique com o botão direito no arquivo de áudio
2. Selecione "Compartilhar" → "Alterar para qualquer pessoa com o link"
3. Defina a permissão como "Visualizador"
4. Copie o link e cole na coluna `Musica_Drive` da planilha

### Verificar Permissões:

Se o áudio não tocar no frontend, verifique:

1. ✅ O arquivo está compartilhado publicamente (qualquer pessoa com o link)
2. ✅ O link está no formato correto na planilha
3. ✅ O arquivo é um formato de áudio suportado (MP3, OGG, WAV, etc.)

## Exemplo de Uso na Planilha

Na coluna `Musica_Drive`, você pode colar qualquer um destes formatos:

```
https://drive.google.com/file/d/1a2b3c4d5e6f7g8h9i0j/view
https://drive.google.com/open?id=1a2b3c4d5e6f7g8h9i0j
```

O sistema converterá automaticamente para:
```
https://drive.google.com/uc?export=view&id=1a2b3c4d5e6f7g8h9i0j
```

## Limitações

- ⚠️ Links de pastas (`/folders/`) não são suportados - apenas links diretos de arquivos
- ⚠️ Arquivos muito grandes podem ter problemas de carregamento
- ⚠️ O Google Drive pode ter limites de taxa de transferência para arquivos grandes

## Solução de Problemas

### Áudio não toca:
1. Verifique se o arquivo está compartilhado publicamente
2. Verifique se o link está correto na planilha
3. Verifique os logs do servidor para erros de processamento

### Link não é processado:
1. Verifique se o link contém um `FILE_ID` válido
2. Verifique os logs para mensagens de erro
3. Tente usar um formato diferente de link
