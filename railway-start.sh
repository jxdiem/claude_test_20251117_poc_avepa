#!/bin/bash

# Script di avvio per Railway

echo "🚀 Starting Sistema Gestione Aiuti Agricoltura on Railway..."
echo "📦 PORT: $PORT"
echo "🔐 SECRET_KEY: ${SECRET_KEY:0:10}..."

# Crea directory databases se non esiste
mkdir -p /app/databases

# Imposta DATABASE_DIR per tutti i servizi
export DATABASE_DIR="/app/databases"

# Verifica che gli script di inizializzazione esistano
echo "🔍 Checking database initialization scripts..."
if [ -d "/app/databases/init_scripts" ]; then
    echo "✅ Init scripts directory found"
    ls -la /app/databases/init_scripts/
else
    echo "❌ Init scripts directory NOT found!"
fi

# Verifica che SECRET_KEY sia impostato
if [ -z "$SECRET_KEY" ]; then
    echo "⚠️  WARNING: SECRET_KEY not set, using default (NOT SECURE)"
    export SECRET_KEY="insecure-default-key-change-me"
fi

# Railway fornisce PORT automaticamente
if [ -z "$PORT" ]; then
    echo "⚠️  PORT not set, using default 8000"
    export PORT=8000
fi

echo "✅ Starting all services with Supervisord..."
echo ""
echo "Services:"
echo "  - Auth Service (8001)"
echo "  - Beneficiary Service (8002)"
echo "  - Request Service (8003)"
echo "  - Calculation Service (8004)"
echo "  - Admin Service (8005)"
echo "  - System Service (8006)"
echo "  - API Gateway ($PORT) ← PUBLIC (includes static frontend)"
echo ""

# Avvia supervisord
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
