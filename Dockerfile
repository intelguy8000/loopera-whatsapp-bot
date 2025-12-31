# Dockerfile para WhatsApp Bot con soporte de audio
FROM python:3.11-slim

# Instalar ffmpeg (necesario para procesar audio de WhatsApp)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Copiar requirements primero (para cache de Docker)
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

CMD ["sh", "-c", "uvicorn app.main:app --host '::' --port ${PORT:-8080}"]
