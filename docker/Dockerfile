# Główny Dockerfile
# docker/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Instalacja zależności systemowych
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ghostscript \
    curl \
    git \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Kopiowanie plików wymagań
COPY requirements.txt ./

# Instalacja zależności Pythona
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie kodu źródłowego
COPY . .

# Tworzenie potrzebnych katalogów
RUN mkdir -p /app/data /app/output /app/models /app/reports /app/logs

# Ekspozycja portów
EXPOSE 5000 8080

# Ustawienie zmiennych środowiskowych
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DATA_DIR=/app/data \
    OUTPUT_DIR=/app/output \
    MODELS_DIR=/app/models \
    REPORTS_DIR=/app/reports \
    LOG_LEVEL=INFO

# Skrypt wejściowy
ENTRYPOINT ["/app/docker/entrypoint.sh"]

# Domyślna komenda
CMD ["api"]