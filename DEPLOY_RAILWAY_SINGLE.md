# 🚀 Deploy su Railway - Modalità Single Service (GRATUITO)

Questa guida ti permette di deployare **tutti i 7 microservizi + frontend** su Railway usando **UN SOLO servizio**, rimanendo nel piano gratuito ($5/mese di credito).

## ✨ Vantaggi di questa Soluzione

- ✅ **Gratis o quasi**: Rimane nei $5/mese di credito Railway
- ✅ **Tutto incluso**: 7 microservizi + frontend in un solo container
- ✅ **Setup semplice**: Deploy in 5 minuti
- ✅ **Nessun CORS issue**: Frontend e backend sullo stesso dominio
- ✅ **Auto-scaling**: Railway gestisce automaticamente le risorse

## 📋 Prerequisiti

1. Account su [Railway.app](https://railway.app) (gratuito)
2. Repository GitHub del progetto
3. 5 minuti del tuo tempo ⏱️

## 🎯 Step-by-Step Deploy

### Passo 1: Prepara il Repository

Il repository è già pronto! I file necessari sono già stati creati:

```
✅ Dockerfile.railway       # Container multi-servizio
✅ supervisord.conf          # Gestione processi
✅ railway-start.sh          # Script di avvio
✅ railway.toml              # Configurazione Railway
✅ .railwayignore            # File da ignorare
✅ .env.railway.example      # Template variabili
```

### Passo 2: Genera SECRET_KEY

Prima di deployare, genera una chiave segreta sicura:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Salva l'output - lo userai nel prossimo step.

**Esempio output:**
```
vP3kX8mN2qR7sT9uW1yZ4aC6bD8eF0gH1iJ3kL5mN7o
```

### Passo 3: Deploy su Railway

#### 3.1 Accedi a Railway

1. Vai su [railway.app](https://railway.app)
2. Clicca **"Login"** e autenticati con GitHub
3. Autorizza Railway ad accedere ai tuoi repository

#### 3.2 Crea Nuovo Progetto

1. Clicca **"New Project"**
2. Seleziona **"Deploy from GitHub repo"**
3. Cerca e seleziona: `claude_test_20251117_poc_avepa`
4. Railway inizierà automaticamente il primo deploy

#### 3.3 Configura Variabili d'Ambiente

1. Nel tuo progetto Railway, clicca sul servizio
2. Vai su **"Variables"**
3. Aggiungi la variabile:

```bash
SECRET_KEY=vP3kX8mN2qR7sT9uW1yZ4aC6bD8eF0gH1iJ3kL5mN7o
```

(Usa la chiave generata al Passo 2)

4. Clicca **"Add"** o **"Deploy"**

#### 3.4 Abilita Dominio Pubblico

1. Nel servizio, vai su **"Settings"**
2. Trova la sezione **"Networking"** o **"Domains"**
3. Clicca **"Generate Domain"**

Railway ti fornirà un URL tipo:
```
https://your-app-production-xxxx.up.railway.app
```

### Passo 4: Attendi il Deploy

Railway builderà il container (prima volta: ~5-8 minuti).

Puoi monitorare il progresso:
1. Vai su **"Deployments"**
2. Clicca sull'ultimo deployment
3. Vedi i logs in tempo reale

**Log di successo:**
```
✅ Starting all services with Supervisord...

Services:
  - Auth Service (8001)
  - Beneficiary Service (8002)
  - Request Service (8003)
  - Calculation Service (8004)
  - Admin Service (8005)
  - System Service (8006)
  - API Gateway (PORT) ← PUBLIC
  - Frontend (3000) ← Internal

Supervisord started successfully
```

### Passo 5: Testa l'Applicazione

Una volta deployato, apri l'URL del tuo servizio Railway:

```
https://your-app-production-xxxx.up.railway.app
```

Dovresti vedere la pagina di login del frontend! 🎉

#### Test API

Testa che il backend risponda:

```bash
# Health check
curl https://your-app-production-xxxx.up.railway.app/

# Login
curl -X POST https://your-app-production-xxxx.up.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password123"
  }'
```

#### Test Frontend

1. Apri l'URL nel browser
2. Dovresti vedere la pagina di login
3. Prova a loggarti con:
   - Username: `admin`
   - Password: `password123`

## 🎉 Fatto! L'applicazione è Live!

Il sistema è ora completamente operativo su Railway:

- ✅ 7 Microservizi attivi
- ✅ Frontend funzionante
- ✅ Database SQLite persistenti
- ✅ SSL/HTTPS automatico
- ✅ Logs centralizzati
- ✅ Auto-deploy su ogni push GitHub

## 📊 Monitoraggio

### Visualizza Logs

1. Vai sul tuo progetto Railway
2. Clicca sul servizio
3. Vai su **"Logs"**

Vedrai i log di tutti i servizi:
```
[auth-service] Starting on port 8001...
[beneficiary-service] Starting on port 8002...
[api-gateway] Starting on port 8000...
[frontend] Serving HTTP on 0.0.0.0 port 3000...
```

### Verifica Risorse

1. Vai su **"Metrics"**
2. Monitora:
   - CPU Usage
   - Memory Usage
   - Network Traffic

**Nota**: Con traffico basso, dovresti rimanere nei $5/mese gratuiti.

## 🔧 Troubleshooting

### ❌ "Build Failed"

**Problema**: Il build Docker fallisce

**Soluzione**:
1. Verifica che tutti i file siano nel repository
2. Controlla i logs del build
3. Verifica che `Dockerfile.railway` sia presente nella root

### ❌ "Application Crashed"

**Problema**: Il servizio si avvia ma crasha

**Soluzione**:
1. Controlla i logs in Railway
2. Verifica che `SECRET_KEY` sia impostato
3. Controlla che `/app/databases` sia writable

### ❌ "502 Bad Gateway"

**Problema**: L'URL Railway non risponde

**Soluzione**:
1. Il servizio potrebbe essere ancora in avvio (attendi 1-2 minuti)
2. Verifica che il dominio pubblico sia abilitato
3. Controlla i logs per errori

### ❌ Frontend non carica

**Problema**: Il frontend mostra errori API

**Soluzione**:
1. Il frontend usa automaticamente `window.location.origin`
2. Verifica che l'API Gateway risponda su `/`
3. Controlla la Console del browser (F12) per errori CORS

### ❌ Database non persiste

**Problema**: I dati scompaiono dopo restart

**Soluzione**:
1. Railway **NON persiste automaticamente** i file
2. Per persistenza, devi usare **Railway Volumes**:
   - Vai su **Settings** → **Volumes**
   - Aggiungi volume: Mount path = `/app/databases`
3. Oppure migra a Railway PostgreSQL (consigliato per produzione)

## 🔄 Aggiornamenti

Ogni volta che fai push su GitHub:

1. Railway rileva il push automaticamente
2. Rebuilda il container
3. Deploya la nuova versione
4. Zero downtime! 🎉

Per disabilitare auto-deploy:
1. Vai su **Settings** → **Service**
2. Disabilita **"Auto Deploy"**

## 💰 Costi Stimati

| Scenario | Costo/mese |
|----------|------------|
| **Sviluppo/Testing** (poco traffico) | $0-5 (GRATIS) |
| **Demo/POC** (traffico moderato) | $5-10 |
| **Produzione Leggera** | $10-20 |
| **Produzione Media** | $20-50 |

**Tip**: Railway offre $5/mese gratis, quindi pagherai solo l'eccedenza.

## 🚀 Ottimizzazioni Opzionali

### 1. Aggiungi Volume per Database

Per persistenza garantita:

1. **Settings** → **Volumes** → **New Volume**
2. Mount path: `/app/databases`
3. Redeploy

### 2. Migra a PostgreSQL

Per produzione vera, usa Railway PostgreSQL:

1. **New** → **Database** → **PostgreSQL**
2. Railway fornirà `DATABASE_URL`
3. Modifica i servizi per usare PostgreSQL invece di SQLite

### 3. Configura Domain Custom

1. Acquista un dominio (es. `myapp.com`)
2. Railway Settings → **Domains** → **Custom Domain**
3. Configura DNS come indicato da Railway

### 4. Abilita Health Checks Avanzati

Railway usa già `/` per health check, ma puoi personalizzare:

1. Modifica `railway.toml`:
```toml
[deploy]
healthcheckPath = "/api/v1/system/health"
healthcheckTimeout = 100
```

## 📚 Risorse Utili

- [Railway Docs](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)
- [Railway Status](https://status.railway.app)

## 🆘 Supporto

Se hai problemi:

1. Controlla questa guida
2. Vedi i logs su Railway
3. Apri issue su GitHub
4. Email: jxdiem@gmail.com

## 🎯 Prossimi Passi

Ora che l'app è live:

- [ ] Cambia password utenti demo
- [ ] Configura backup database (se usi SQLite)
- [ ] Aggiungi monitoring esterno (UptimeRobot, Pingdom)
- [ ] Configura CI/CD più avanzato
- [ ] Implementa rate limiting per API
- [ ] Aggiungi logging strutturato

---

**🎉 Congratulazioni! Il tuo sistema è ora in produzione su Railway!**

Frontend + Backend: `https://your-app.up.railway.app` 🚀
