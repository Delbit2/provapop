FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório para instance (banco de dados SQLite, se usado)
RUN mkdir -p instance

# Criar diretório para migrations
RUN mkdir -p migrations/versions

# Variáveis de ambiente padrão
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Expor porta
EXPOSE 5000

# Comando para rodar a aplicação
# Usa gunicorn em produção, flask run em desenvolvimento
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
