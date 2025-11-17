# Guida Deployment su Railway

## Configurazione Servizi

Railway richiede **7 servizi separati** (uno per ogni microservizio).

### Porte e Networking

**IMPORTANTE**: Railway fornisce automaticamente la variabile d'ambiente `PORT` per ogni servizio.
- I servizi sono già configurati per usare `PORT` automaticamente
- Railway assegna un dominio pubblico a ogni servizio
- La comunicazione tra servizi avviene tramite **Private Networking** di Railway

## Step by Step Deployment

### 1. Preparazione Repository

Il repository è già pronto! Tutti i servizi supportano la variabile `PORT` di Railway.

### 2. Creazione Progetto Railway

1. Vai su [Railway.app](https://railway.app)
2. **New Project** → **Deploy from GitHub repo**
3. Seleziona: `jxdiem/claude_test_20251117_poc_avepa`

### 3. Creazione dei 7 Servizi

Crea **7 servizi separati** con questa configurazione:

#### Servizio 1: API Gateway

**Settings:**
- **Name**: `api-gateway`
- **Root Directory**: `/api-gateway`
- **Start Command**: `python main.py`
- **Watch Paths**: `api-gateway/**`

**Variables:**
```bash
SECRET_KEY=<genera-chiave-sicura-random>
DATABASE_DIR=/app/databases
AUTH_SERVICE_URL=${{auth-service.RAILWAY_PRIVATE_DOMAIN}}
BENEFICIARY_SERVICE_URL=${{beneficiary-service.RAILWAY_PRIVATE_DOMAIN}}
REQUEST_SERVICE_URL=${{request-service.RAILWAY_PRIVATE_DOMAIN}}
CALCULATION_SERVICE_URL=${{calculation-service.RAILWAY_PRIVATE_DOMAIN}}
ADMIN_SERVICE_URL=${{admin-service.RAILWAY_PRIVATE_DOMAIN}}
SYSTEM_SERVICE_URL=${{system-service.RAILWAY_PRIVATE_DOMAIN}}
```

**Public Domain**: ✅ ENABLE (questo è l'entry point pubblico)

---

#### Servizio 2: Auth Service

**Settings:**
- **Name**: `auth-service`
- **Root Directory**: `/services/auth`
- **Start Command**: `python main.py`
- **Watch Paths**: `services/auth/**`, `shared/**`, `databases/**`

**Variables:**
```bash
SECRET_KEY=<stessa-chiave-del-gateway>
DATABASE_DIR=/app/databases
```

**Public Domain**: ❌ DISABLE (usa private networking)

---

#### Servizio 3: Beneficiary Service

**Settings:**
- **Name**: `beneficiary-service`
- **Root Directory**: `/services/beneficiary`
- **Start Command**: `python main.py`
- **Watch Paths**: `services/beneficiary/**`, `shared/**`, `databases/**`

**Variables:**
```bash
SECRET_KEY=<stessa-chiave-del-gateway>
DATABASE_DIR=/app/databases
```

**Public Domain**: ❌ DISABLE

---

#### Servizio 4: Request Service

**Settings:**
- **Name**: `request-service`
- **Root Directory**: `/services/request`
- **Start Command**: `python main.py`
- **Watch Paths**: `services/request/**`, `shared/**`, `databases/**`

**Variables:**
```bash
SECRET_KEY=<stessa-chiave-del-gateway>
DATABASE_DIR=/app/databases
```

**Public Domain**: ❌ DISABLE

---

#### Servizio 5: Calculation Service

**Settings:**
- **Name**: `calculation-service`
- **Root Directory**: `/services/calculation`
- **Start Command**: `python main.py`
- **Watch Paths**: `services/calculation/**`, `shared/**`, `databases/**`

**Variables:**
```bash
SECRET_KEY=<stessa-chiave-del-gateway>
DATABASE_DIR=/app/databases
```

**Public Domain**: ❌ DISABLE

---

#### Servizio 6: Admin Service

**Settings:**
- **Name**: `admin-service`
- **Root Directory**: `/services/admin`
- **Start Command**: `python main.py`
- **Watch Paths**: `services/admin/**`, `shared/**`, `databases/**`

**Variables:**
```bash
SECRET_KEY=<stessa-chiave-del-gateway>
DATABASE_DIR=/app/databases
```

**Public Domain**: ❌ DISABLE

---

#### Servizio 7: System Service

**Settings:**
- **Name**: `system-service`
- **Root Directory**: `/services/system`
- **Start Command**: `python main.py`
- **Watch Paths**: `services/system/**`, `shared/**`, `databases/**`

**Variables:**
```bash
SECRET_KEY=<stessa-chiave-del-gateway>
DATABASE_DIR=/app/databases
AUTH_SERVICE_URL=${{auth-service.RAILWAY_PRIVATE_DOMAIN}}
BENEFICIARY_SERVICE_URL=${{beneficiary-service.RAILWAY_PRIVATE_DOMAIN}}
REQUEST_SERVICE_URL=${{request-service.RAILWAY_PRIVATE_DOMAIN}}
CALCULATION_SERVICE_URL=${{calculation-service.RAILWAY_PRIVATE_DOMAIN}}
ADMIN_SERVICE_URL=${{admin-service.RAILWAY_PRIVATE_DOMAIN}}
```

**Public Domain**: ❌ DISABLE

---

## 4. Configurazione Volumi (Importante!)

Per condividere i database SQLite tra i servizi, devi configurare un **Volume condiviso**:

1. Vai in ogni servizio
2. **Settings** → **Volumes**
3. **Add Volume**:
   - **Mount Path**: `/app/databases`
   - **Name**: `shared-databases`

**IMPORTANTE**: Usa lo **stesso nome volume** (`shared-databases`) per tutti i servizi.

## 5. Networking Privato

Railway fornisce automaticamente il **Private Networking**:

- Ogni servizio ha una variabile `RAILWAY_PRIVATE_DOMAIN`
- Formato: `<service-name>.railway.internal`
- Usala per la comunicazione tra servizi (già configurato nelle variabili)

## 6. Deploy

1. Dopo aver configurato tutti i servizi, fai **Deploy All**
2. Railway builderà automaticamente ogni servizio
3. I servizi si avvieranno e si connetteranno tra loro

## 7. Testing

Una volta deployato, testa l'API Gateway:

```bash
# Ottieni l'URL pubblico del gateway
GATEWAY_URL=<url-api-gateway-railway>

# Test health check
curl $GATEWAY_URL

# Test login
curl -X POST $GATEWAY_URL/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password123"
  }'
```

## 8. Monitoring

Railway fornisce automaticamente:
- **Logs** per ogni servizio
- **Metrics** (CPU, RAM, Network)
- **Deployments history**

## Note Importanti

### Porte
- ✅ Railway gestisce automaticamente le porte tramite la variabile `PORT`
- ✅ Non devi configurare manualmente le porte
- ✅ Il codice è già configurato per usare `os.getenv("PORT")`

### Database
- SQLite è OK per demo/testing
- Per produzione, considera PostgreSQL (Railway lo supporta nativamente)
- I database sono persistenti tramite Volumes

### Costi
- Railway offre un **tier gratuito** con limiti
- Monitora l'uso nella dashboard
- 7 servizi potrebbero superare il tier gratuito

### Alternative

Se vuoi risparmiare risorse Railway:

**Opzione 1**: Deploya solo API Gateway + 1-2 servizi essenziali
**Opzione 2**: Usa Docker Compose su un singolo servizio Railway (meno microservizi, più monolitico)
**Opzione 3**: Usa le immagini Docker pre-built dalla GitHub Actions

## Troubleshooting

### Servizio non si avvia
1. Controlla i **Logs** del servizio
2. Verifica che `shared/` sia accessibile
3. Verifica le variabili d'ambiente

### Database non trovato
1. Verifica che il Volume sia montato correttamente
2. Verifica `DATABASE_DIR=/app/databases`
3. I database si creano automaticamente al primo avvio

### Servizi non comunicano
1. Verifica che le variabili `*_SERVICE_URL` usino `RAILWAY_PRIVATE_DOMAIN`
2. Abilita **Private Networking** nel progetto
3. Usa il formato: `http://${{service-name.RAILWAY_PRIVATE_DOMAIN}}`

## Generazione SECRET_KEY

Per generare una chiave sicura:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Usa la stessa chiave per **tutti i servizi**.

## Domain Pubblico

Solo l'**API Gateway** deve avere un dominio pubblico.

L'URL sarà tipo: `https://api-gateway-production-xxxx.up.railway.app`

Tutti gli altri servizi comunicano tramite private networking.
