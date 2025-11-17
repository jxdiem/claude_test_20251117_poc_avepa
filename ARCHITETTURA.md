# Architettura Sistema Gestione Aiuti Agricoltura

## 1. Overview del Sistema

Sistema a microservizi per la gestione delle domande di aiuto all'agricoltura, con gestione fascicoli aziendali, richieste di contributo e calcolo automatico degli aiuti basati su normativa.

## 2. Stack Tecnologico

- **Linguaggio**: Python 3.11+
- **Framework API**: FastAPI
- **Database**: SQLite
- **API Gateway**: FastAPI con routing centralizzato
- **Autenticazione**: JWT (JSON Web Tokens)
- **Deployment**: Railway (containerizzato)
- **Version Control**: GitHub

## 3. Architettura Microservizi

### 3.1 API Gateway (Port: 8000)
**Responsabilità**:
- Entry point unico per tutte le richieste
- Routing verso i microservizi
- Rate limiting
- Logging centralizzato
- CORS management
- JWT validation

**Endpoints principali**:
- `/api/v1/auth/*` → Auth Service
- `/api/v1/beneficiaries/*` → Beneficiary Service
- `/api/v1/requests/*` → Request Service
- `/api/v1/calculations/*` → Calculation Service
- `/api/v1/admin/*` → Admin Service
- `/api/v1/system/*` → System Service

### 3.2 Auth Service (Port: 8001)
**Responsabilità**:
- Autenticazione utenti
- Gestione token JWT
- Gestione ruoli (BENEFICIARIO, ISTRUTTORE, AMMINISTRATORE, SISTEMISTA)
- Password hashing
- Refresh token

**Database**: `auth.db`
- Tabella `users` (id, username, email, password_hash, role, active, created_at)
- Tabella `refresh_tokens` (token, user_id, expires_at)

### 3.3 Beneficiary Service (Port: 8002)
**Responsabilità**:
- Gestione fascicoli aziendali
- CRUD dati anagrafici
- Gestione dati bancari
- Gestione consistenza territoriale (grafica/alfanumerica)
- Gestione macchinari agricoli

**Database**: `beneficiaries.db`
- Tabella `fascicoli` (id, user_id, ragione_sociale, cf_piva, indirizzo, ...)
- Tabella `dati_bancari` (id, fascicolo_id, iban, bic, intestatario, ...)
- Tabella `particelle_catastali` (id, fascicolo_id, comune, foglio, particella, superficie_mq, coordinate_geojson, ...)
- Tabella `macchinari` (id, fascicolo_id, tipo, marca, modello, anno, targa, ...)

### 3.4 Request Service (Port: 8003)
**Responsabilità**:
- Creazione domande di aiuto
- Gestione stati domanda (BOZZA, PRESENTATA, IN_ISTRUTTORIA, APPROVATA, RESPINTA, LIQUIDATA)
- Associazione colture a particelle
- Workflow istruttoria

**Database**: `requests.db`
- Tabella `domande` (id, fascicolo_id, anno_campagna, stato, data_presentazione, istruttore_id, ...)
- Tabella `colture_dichiarate` (id, domanda_id, particella_id, coltura_id, superficie_mq, ...)
- Tabella `note_istruttoria` (id, domanda_id, istruttore_id, nota, data, ...)

### 3.5 Calculation Service (Port: 8004)
**Responsabilità**:
- Calcolo contributi in base a normativa
- Validazione superfici dichiarate
- Generazione prospetti di liquidazione
- Storico calcoli

**Database**: `calculations.db`
- Tabella `calcoli` (id, domanda_id, importo_totale, data_calcolo, dettaglio_json, ...)
- Tabella `dettaglio_calcolo` (id, calcolo_id, coltura_id, superficie_mq, importo_unitario, importo_totale, ...)

### 3.6 Admin Service (Port: 8005)
**Responsabilità**:
- Gestione parametri normativi
- CRUD colture ammissibili
- Impostazione contributi unitari (€/mq o €/ha)
- Gestione campagne
- Configurazione massimali e vincoli

**Database**: `admin.db`
- Tabella `campagne` (id, anno, descrizione, data_inizio, data_fine, attiva, ...)
- Tabella `colture` (id, codice, descrizione, attiva, ...)
- Tabella `contributi_unitari` (id, campagna_id, coltura_id, importo_per_mq, massimale_superficie, massimale_importo, ...)
- Tabella `parametri_normativi` (chiave, valore, descrizione, tipo_dato, ...)

### 3.7 System Service (Port: 8006)
**Responsabilità**:
- Health check di tutti i servizi
- Monitoring performance
- Logs aggregati
- Statistiche utilizzo
- Backup database

**Database**: `system.db`
- Tabella `health_checks` (id, servizio, status, response_time, timestamp, ...)
- Tabella `audit_logs` (id, user_id, servizio, azione, dettagli_json, timestamp, ...)
- Tabella `statistiche` (id, metrica, valore, timestamp, ...)

## 4. Schema Database Dettagliato

### 4.1 Relazioni tra Database
Ogni microservizio ha il proprio database SQLite, ma le relazioni logiche sono mantenute tramite ID:
- `beneficiaries.fascicoli.user_id` → `auth.users.id`
- `requests.domande.fascicolo_id` → `beneficiaries.fascicoli.id`
- `requests.colture_dichiarate.coltura_id` → `admin.colture.id`
- `calculations.calcoli.domanda_id` → `requests.domande.id`

### 4.2 Indici Principali
- Indici su chiavi esterne per performance
- Indici su campi di ricerca frequente (cf_piva, anno_campagna, stato)
- Indici su timestamp per query temporali

## 5. Gestione Autorizzazioni

### 5.1 Ruoli e Permessi

| Ruolo | Permessi |
|-------|----------|
| **BENEFICIARIO** | - Gestione proprio fascicolo<br>- Creazione/modifica domande proprie (solo stato BOZZA)<br>- Visualizzazione proprie domande<br>- Visualizzazione calcoli propri |
| **ISTRUTTORE** | - Visualizzazione tutti i fascicoli<br>- Visualizzazione tutte le domande<br>- Istruttoria domande (cambio stato, note)<br>- Visualizzazione calcoli<br>- Esecuzione calcoli |
| **AMMINISTRATORE** | - Gestione colture<br>- Gestione contributi unitari<br>- Gestione campagne<br>- Gestione parametri normativi<br>- Visualizzazione statistiche<br>- Gestione utenti |
| **SISTEMISTA** | - Accesso health checks<br>- Accesso logs<br>- Accesso monitoring<br>- Backup/restore<br>- Tutti i permessi di visualizzazione |

## 6. Flussi Principali

### 6.1 Flusso Creazione Domanda
1. Beneficiario crea/completa fascicolo aziendale
2. Beneficiario crea nuova domanda (stato: BOZZA)
3. Beneficiario associa colture a particelle catastali
4. Sistema valida consistenza territoriale
5. Beneficiario presenta domanda (stato: PRESENTATA)
6. Sistema blocca modifiche fascicolo/domanda

### 6.2 Flusso Istruttoria
1. Istruttore prende in carico domanda (stato: IN_ISTRUTTORIA)
2. Istruttore verifica dati fascicolo
3. Istruttore verifica colture dichiarate
4. Sistema calcola contributo spettante
5. Istruttore approva o respinge (stato: APPROVATA/RESPINTA)
6. Se approvata, genera prospetto liquidazione

### 6.3 Flusso Calcolo Contributo
1. Request Service richiede calcolo a Calculation Service
2. Calculation Service recupera colture dichiarate
3. Calculation Service recupera contributi unitari da Admin Service
4. Per ogni coltura: importo = superficie_mq × contributo_per_mq
5. Verifica massimali per coltura e totali
6. Salva dettaglio calcolo
7. Ritorna importo totale

## 7. API Gateway - Struttura Routing

```python
# Esempio struttura routing in API Gateway
routes = {
    "/api/v1/auth/login": ("POST", "auth-service:8001"),
    "/api/v1/auth/refresh": ("POST", "auth-service:8001"),
    "/api/v1/beneficiaries/fascicolo": ("GET/POST/PUT", "beneficiary-service:8002"),
    "/api/v1/beneficiaries/particelle": ("GET/POST", "beneficiary-service:8002"),
    "/api/v1/requests/domande": ("GET/POST", "request-service:8003"),
    "/api/v1/requests/domande/{id}/presenta": ("POST", "request-service:8003"),
    "/api/v1/calculations/calcola/{domanda_id}": ("POST", "calculation-service:8004"),
    "/api/v1/admin/colture": ("GET/POST/PUT", "admin-service:8005"),
    "/api/v1/admin/contributi": ("GET/POST/PUT", "admin-service:8005"),
    "/api/v1/system/health": ("GET", "system-service:8006"),
}
```

## 8. Deployment su Railway

### 8.1 Struttura Progetto
```
/
├── api-gateway/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── services/
│   ├── auth/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── main.py
│   ├── beneficiary/
│   ├── request/
│   ├── calculation/
│   ├── admin/
│   └── system/
├── shared/
│   ├── models.py
│   ├── schemas.py
│   └── utils.py
├── databases/
│   └── init_scripts/
├── docker-compose.yml (per sviluppo locale)
├── railway.json
└── README.md
```

### 8.2 Configurazione Railway
- Ogni microservizio come servizio separato
- Database SQLite persistenti tramite volumi Railway
- Variabili d'ambiente per configurazione
- API Gateway esposto pubblicamente
- Microservizi in rete privata

## 9. Sicurezza

### 9.1 Misure di Sicurezza
- Password hashing con bcrypt
- JWT con expiration (access token: 30min, refresh token: 7 giorni)
- HTTPS only in produzione
- Validazione input con Pydantic
- SQL injection protection (SQLAlchemy ORM)
- Rate limiting su API Gateway
- CORS configurato per frontend specifico

### 9.2 Audit Trail
- Logging di tutte le operazioni critiche
- Timestamp su tutte le modifiche
- User tracking su ogni azione
- Retention logs: 2 anni

## 10. Considerazioni Tecniche

### 10.1 Gestione Dati Geografici
- Particelle catastali: coordinate in formato GeoJSON
- Visualizzazione grafica: integrazione con librerie mapping (Leaflet/Folium)
- Calcolo superficie: da coordinate o da dato catastale

### 10.2 Performance
- Indici database ottimizzati
- Caching con Redis (opzionale per future ottimizzazioni)
- Pagination su liste
- Query ottimizzate con join minimi (denormalizzazione selettiva)

### 10.3 Scalabilità Futura
- Possibilità di migrare a PostgreSQL mantenendo struttura
- Microservizi indipendenti scalabili separatamente
- API versioning (v1, v2, ...)
- Message queue per operazioni asincrone (future)

## 11. Sviluppo e Testing

### 11.1 Approccio di Sviluppo
1. Setup struttura progetto e repository GitHub
2. Implementazione Auth Service + API Gateway base
3. Implementazione Beneficiary Service
4. Implementazione Request Service
5. Implementazione Calculation Service
6. Implementazione Admin Service
7. Implementazione System Service
8. Testing integrazione
9. Deployment Railway

### 11.2 Testing
- Unit test per ogni microservizio (pytest)
- Integration test per flussi completi
- Test API con pytest + httpx
- Test coverage minimo: 70%

## 12. Prossimi Passi

1. Approvazione architettura
2. Setup repository GitHub
3. Creazione struttura progetto
4. Implementazione microservizi in ordine di dipendenza
5. Testing
6. Configurazione Railway
7. Deployment

---

**Note**: Questa architettura è progettata per essere modulare, scalabile e facilmente manutenibile. Ogni microservizio è indipendente ma collabora attraverso API ben definite gestite centralmente dall'API Gateway.
