# Sistema Gestione Aiuti Agricoltura

Sistema a microservizi per la gestione delle domande di aiuto all'agricoltura, con gestione fascicoli aziendali, richieste di contributo e calcolo automatico degli aiuti basati su normativa.

## Architettura

Il sistema è composto da 7 microservizi:

1. **API Gateway** (porta 8000) - Entry point centralizzato
2. **Auth Service** (porta 8001) - Autenticazione e autorizzazione
3. **Beneficiary Service** (porta 8002) - Gestione fascicoli aziendali
4. **Request Service** (porta 8003) - Gestione domande di aiuto
5. **Calculation Service** (porta 8004) - Calcolo contributi
6. **Admin Service** (porta 8005) - Parametri normativi
7. **System Service** (porta 8006) - Monitoring e diagnostica

### Ruoli Utente

- **BENEFICIARIO**: Gestione proprio fascicolo e domande
- **ISTRUTTORE**: Istruttoria domande e calcolo contributi
- **AMMINISTRATORE**: Gestione parametri normativi e utenti
- **SISTEMISTA**: Monitoring e diagnostica sistema

## Stack Tecnologico

- **Backend**: Python 3.11+ con FastAPI
- **Database**: SQLite (un database per servizio)
- **Autenticazione**: JWT
- **API Gateway**: FastAPI con routing centralizzato
- **Deployment**: Docker Compose (sviluppo) / Railway (produzione)

## Installazione e Avvio

### Prerequisiti

- Python 3.11+
- pip
- Git

### Installazione Locale

1. **Clona il repository**:
```bash
git clone https://github.com/jxdiem/claude_test_20251117_poc_avepa.git
cd claude_test_20251117_poc_avepa
```

2. **Crea ambiente virtuale**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure
venv\Scripts\activate  # Windows
```

3. **Installa dipendenze per ogni servizio**:
```bash
# Shared dependencies
pip install pydantic fastapi uvicorn PyJWT httpx

# Oppure installa per ogni servizio
cd services/auth && pip install -r requirements.txt && cd ../..
cd services/beneficiary && pip install -r requirements.txt && cd ../..
# ... e così via per tutti i servizi
```

4. **Crea directory database**:
```bash
mkdir -p databases
```

5. **Avvia i servizi** (in terminali separati):

```bash
# Terminal 1 - Auth Service
cd services/auth
python main.py

# Terminal 2 - Beneficiary Service
cd services/beneficiary
python main.py

# Terminal 3 - Request Service
cd services/request
python main.py

# Terminal 4 - Calculation Service
cd services/calculation
python main.py

# Terminal 5 - Admin Service
cd services/admin
python main.py

# Terminal 6 - System Service
cd services/system
python main.py

# Terminal 7 - API Gateway
cd api-gateway
python main.py
```

6. **Accedi all'API**: `http://localhost:8000`

### Avvio con Docker Compose (Consigliato)

```bash
# Copia file ambiente
cp .env.example .env

# Avvia tutti i servizi
docker-compose up --build

# In background
docker-compose up -d --build
```

Tutti i servizi saranno disponibili:
- API Gateway: http://localhost:8000
- Auth Service: http://localhost:8001
- Beneficiary Service: http://localhost:8002
- Request Service: http://localhost:8003
- Calculation Service: http://localhost:8004
- Admin Service: http://localhost:8005
- System Service: http://localhost:8006

## Utilizzo

### 1. Login

**Utenti di default** (password: `password123`):
- `admin` - AMMINISTRATORE
- `sistemista` - SISTEMISTA
- `istruttore1` - ISTRUTTORE
- `beneficiario1` - BENEFICIARIO

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "beneficiario1",
    "password": "password123"
  }'
```

Risposta:
```json
{
  "success": true,
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_id": 4,
  "username": "beneficiario1",
  "role": "BENEFICIARIO"
}
```

### 2. Creare un Fascicolo

```bash
curl -X POST http://localhost:8000/api/v1/beneficiaries/fascicolo \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ragione_sociale": "Azienda Agricola Rossi",
    "cf_piva": "12345678901",
    "indirizzo": "Via Roma 1",
    "cap": "00100",
    "comune": "Roma",
    "provincia": "RM",
    "telefono": "0612345678",
    "email": "info@agricolarossi.it"
  }'
```

### 3. Aggiungere Particelle Catastali

```bash
curl -X POST "http://localhost:8000/api/v1/beneficiaries/particelle?fascicolo_id=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "comune": "Roma",
    "foglio": "10",
    "particella": "250",
    "superficie_mq": 50000
  }'
```

### 4. Creare una Domanda di Aiuto

```bash
curl -X POST "http://localhost:8000/api/v1/requests/domande?fascicolo_id=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "anno_campagna": 2024,
    "colture": [
      {
        "particella_id": 1,
        "coltura_id": 1,
        "superficie_mq": 30000
      }
    ]
  }'
```

### 5. Presentare la Domanda

```bash
curl -X POST http://localhost:8000/api/v1/requests/domande/1/presenta \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 6. Calcolare il Contributo (Istruttore)

```bash
curl -X POST http://localhost:8000/api/v1/calculations/calcola/1 \
  -H "Authorization: Bearer ISTRUTTORE_TOKEN"
```

### 7. Verificare Salute del Sistema (Sistemista)

```bash
curl -X GET http://localhost:8000/api/v1/system/health \
  -H "Authorization: Bearer SISTEMISTA_TOKEN"
```

## Documentazione API

Ogni servizio espone la documentazione Swagger:

- API Gateway: http://localhost:8000/docs
- Auth Service: http://localhost:8001/docs
- Beneficiary Service: http://localhost:8002/docs
- Request Service: http://localhost:8003/docs
- Calculation Service: http://localhost:8004/docs
- Admin Service: http://localhost:8005/docs
- System Service: http://localhost:8006/docs

## Deployment su Railway

### 1. Preparazione

1. Crea account su [Railway](https://railway.app)
2. Installa Railway CLI:
```bash
npm i -g @railway/cli
```

3. Login:
```bash
railway login
```

### 2. Deploy

```bash
# Inizializza progetto Railway
railway init

# Imposta variabili d'ambiente
railway variables set SECRET_KEY=your-production-secret-key

# Deploy
railway up
```

### 3. Configurazione Servizi

Crea un servizio Railway per ogni microservizio:
- api-gateway
- auth-service
- beneficiary-service
- request-service
- calculation-service
- admin-service
- system-service

Configura le variabili d'ambiente per ogni servizio con gli URL interni Railway.

## Struttura Database

### Auth DB (`auth.db`)
- `users` - Utenti del sistema
- `refresh_tokens` - Token di refresh

### Beneficiaries DB (`beneficiaries.db`)
- `fascicoli` - Fascicoli aziendali
- `dati_bancari` - IBAN e coordinate bancarie
- `particelle_catastali` - Particelle catastali con coordinate
- `macchinari` - Macchinari agricoli

### Requests DB (`requests.db`)
- `domande` - Domande di aiuto
- `colture_dichiarate` - Colture associate alle domande
- `note_istruttoria` - Note degli istruttori

### Calculations DB (`calculations.db`)
- `calcoli` - Calcoli contributi
- `dettaglio_calcolo` - Dettaglio per coltura

### Admin DB (`admin.db`)
- `campagne` - Campagne annuali
- `colture` - Colture ammissibili
- `contributi_unitari` - Contributi per coltura e campagna
- `parametri_normativi` - Parametri configurabili

### System DB (`system.db`)
- `health_checks` - Log health check servizi
- `audit_logs` - Log audit azioni utente
- `statistiche` - Metriche sistema

## Sicurezza

- Password hashate con PBKDF2-HMAC-SHA256
- JWT con expiration (access: 30min, refresh: 7 giorni)
- Validazione input con Pydantic
- CORS configurabile
- Rate limiting su API Gateway (da implementare)

## Testing

```bash
# Installa pytest
pip install pytest pytest-asyncio httpx

# Esegui test
pytest tests/
```

## Contribuire

1. Fork del progetto
2. Crea branch feature (`git checkout -b feature/AmazingFeature`)
3. Commit modifiche (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri Pull Request

## Licenza

Progetto open source per scopi didattici e amministrativi.

## Contatti

- Repository: https://github.com/jxdiem/claude_test_20251117_poc_avepa
- Email: jxdiem@gmail.com

## Roadmap

- [ ] Frontend web con React
- [ ] Export dati in Excel/PDF
- [ ] Notifiche email
- [ ] Integrazione con sistemi catastali
- [ ] Dashboard analytics
- [ ] API rate limiting
- [ ] Migrazione a PostgreSQL (opzionale)
- [ ] Message queue per operazioni asincrone
- [ ] Caching con Redis
