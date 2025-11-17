# 📁 File per Deploy Railway

Questi file sono stati creati per supportare il deploy su Railway in modalità **Single Service** (gratuito).

## File Principali

| File | Descrizione |
|------|-------------|
| `Dockerfile.railway` | Dockerfile che crea un container con tutti i 7 microservizi + frontend |
| `supervisord.conf` | Configurazione Supervisord per gestire i 7 processi Python |
| `railway-start.sh` | Script di avvio che inizializza l'ambiente e lancia Supervisord |
| `railway.toml` | Configurazione Railway (builder, health check, restart policy) |
| `.railwayignore` | File da escludere dal deploy (simile a .dockerignore) |
| `.env.railway.example` | Template delle variabili d'ambiente per Railway |

## Guide Deploy

| Guida | Quando Usarla |
|-------|---------------|
| `DEPLOY_RAILWAY_SINGLE.md` | ⭐ **CONSIGLIATO** - Deploy gratuito di tutto in un container |
| `RAILWAY_DEPLOYMENT.md` | Deploy a pagamento con 7 servizi separati (architettura microservizi) |

## Come Funziona

### Architecture: Single Service

```
┌─────────────────────────────────────────────┐
│          Railway Service Container           │
├─────────────────────────────────────────────┤
│  Supervisord (Process Manager)              │
│  ├── Auth Service (8001)                    │
│  ├── Beneficiary Service (8002)             │
│  ├── Request Service (8003)                 │
│  ├── Calculation Service (8004)             │
│  ├── Admin Service (8005)                   │
│  ├── System Service (8006)                  │
│  ├── API Gateway ($PORT) ← Public           │
│  └── Frontend Server (3000) ← Internal      │
├─────────────────────────────────────────────┤
│  Shared SQLite Databases (/app/databases)   │
└─────────────────────────────────────────────┘
                    │
                    ↓
         Railway Public Domain
  https://your-app.up.railway.app
```

### Comunicazione Interna

- Tutti i servizi girano nello stesso container
- Comunicano via `localhost` (veloce!)
- L'API Gateway (porta $PORT) è esposto pubblicamente
- Il frontend è servito internamente e accessibile via l'API Gateway

## Variabili d'Ambiente Richieste

Su Railway, configura solo:

```bash
SECRET_KEY=<genera-una-chiave-sicura>
```

Railway fornisce automaticamente:
- `PORT` - Porta pubblica (usata dall'API Gateway)
- Altri dettagli di networking

## Testing Locale (Opzionale)

Puoi testare il container localmente:

```bash
# Build
docker build -f Dockerfile.railway -t avepa-railway .

# Run
docker run -p 8000:8000 \
  -e SECRET_KEY=test-key \
  -e PORT=8000 \
  avepa-railway

# Test
curl http://localhost:8000
```

## Deploy Workflow

1. **Push to GitHub** → Railway rileva il push
2. **Build** → Railway usa `Dockerfile.railway`
3. **Deploy** → Supervisord avvia tutti i servizi
4. **Health Check** → Railway verifica che `/` risponda
5. **Live!** → App accessibile al dominio Railway

## Costi

| Scenario | Costo Stimato |
|----------|---------------|
| Sviluppo/Testing | **$0-5/mese** (GRATIS) |
| Demo/POC | $5-10/mese |
| Produzione Leggera | $10-20/mese |

**Nota**: Railway offre $5/mese gratis, quindi il primo mese è completamente gratuito se il traffico è basso.

## Troubleshooting

### Build Failed
- Verifica che tutti i file siano committati su GitHub
- Controlla i logs del build su Railway

### Service Crashed
- Verifica che `SECRET_KEY` sia impostata
- Controlla i logs su Railway Dashboard

### Database Non Persiste
- Aggiungi un Railway Volume: mount path `/app/databases`
- Oppure migra a Railway PostgreSQL

## Prossimi Passi

Dopo il deploy:

1. ✅ Verifica che l'app sia live
2. ✅ Testa login e funzionalità
3. ✅ Cambia password utenti demo
4. ✅ Considera aggiungere un Volume per persistenza database
5. ✅ Configura backup (se necessario)

## Supporto

- 📖 Leggi: `DEPLOY_RAILWAY_SINGLE.md` per la guida completa
- 🐛 Problemi? Apri issue su GitHub
- 📧 Email: jxdiem@gmail.com

---

**Happy Deploying! 🚀**
