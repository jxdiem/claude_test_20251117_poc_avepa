FROM python:3.11-slim

WORKDIR /app

# Installa dipendenze di sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice del servizio
COPY main.py .

# Crea directory per shared e databases
RUN mkdir -p /app/shared /app/databases

# Espone porta
EXPOSE 8003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8003/')" || exit 1

# Avvia applicazione
CMD ["python", "main.py"]
