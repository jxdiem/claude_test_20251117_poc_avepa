# Security Policy

## Pipeline di Sicurezza

Questo progetto implementa controlli di sicurezza automatizzati tramite GitHub Actions:

### 1. SAST (Static Application Security Testing)

#### Bandit
- **Scopo**: Analisi statica del codice Python per vulnerabilità comuni
- **Esecuzione**: Ad ogni push e pull request
- **Controlli**:
  - SQL injection
  - Hardcoded passwords
  - Unsafe cryptographic functions
  - Shell injection
  - XML vulnerabilities

#### Semgrep
- **Scopo**: Pattern matching per vulnerabilità di sicurezza
- **Esecuzione**: Ad ogni push e pull request
- **Controlli**:
  - OWASP Top 10
  - Best practices di sicurezza
  - Code smells di sicurezza

### 2. Dependency Scanning

#### Safety
- **Scopo**: Controllo dipendenze Python per CVE noti
- **Esecuzione**: Ad ogni push
- **Database**: PyPI Advisory Database

### 3. Code Quality

#### Flake8
- **Scopo**: Linting Python per qualità del codice
- **Standard**: PEP 8

#### Black
- **Scopo**: Formattazione consistente del codice
- **Configurazione**: 120 caratteri per riga

#### Pylint
- **Scopo**: Analisi statica approfondita
- **Controlli**: Code smells, errori logici, convenzioni

## Vulnerabilità Note Accettate

Per scopi dimostrativi, alcune vulnerabilità minori sono accettate:

1. **B101** - Use of assert detected
   - Motivo: Utilizzato in test e validazioni

2. **Hardcoded SECRET_KEY in config.py**
   - Motivo: Valore di default, sovrascritto in produzione via env

## Reporting Vulnerabilità

Se trovi una vulnerabilità di sicurezza, per favore:

1. **NON** aprire una issue pubblica
2. Invia email a: jxdiem@gmail.com
3. Include:
   - Descrizione della vulnerabilità
   - Passi per riprodurla
   - Impatto potenziale
   - Eventuale fix suggerito

## Best Practices Implementate

### Autenticazione
- JWT con expiration time
- Password hashing con PBKDF2-HMAC-SHA256
- Refresh token separati

### Database
- Prepared statements (SQLite con parametri)
- Input validation con Pydantic
- Nessuna query dinamica non sanitizzata

### API
- CORS configurabile
- Rate limiting (da implementare in produzione)
- Validazione input su tutti gli endpoint

### Docker
- Immagini base ufficiali Python slim
- User non-root (da implementare)
- Health checks configurati
- Secrets via environment variables

## Configurazione Produzione

Per un ambiente di produzione sicuro:

1. **Environment Variables**:
   ```bash
   SECRET_KEY=<genera-chiave-forte-random>
   DATABASE_DIR=/var/lib/app/databases
   ```

2. **HTTPS Only**:
   - Configura reverse proxy (nginx/traefik)
   - Forza HTTPS redirect

3. **Rate Limiting**:
   - Implementa a livello API Gateway
   - Limite consigliato: 100 req/min per IP

4. **Database**:
   - Backup automatici
   - Encryption at rest
   - Considera migrazione a PostgreSQL

5. **Monitoring**:
   - Log centralizati
   - Alerting su comportamenti anomali
   - Audit trail completo

## Checklist Deployment

- [ ] SECRET_KEY randomizzato
- [ ] HTTPS abilitato
- [ ] CORS limitato a domini specifici
- [ ] Database backup configurato
- [ ] Logs monitoring attivo
- [ ] Health checks configurati
- [ ] Rate limiting abilitato
- [ ] Firewall configurato
- [ ] Secrets non committati in git
- [ ] Dipendenze aggiornate

## Versioni Supportate

| Versione | Supporto         |
| -------- | ---------------- |
| 1.0.x    | :white_check_mark: |
| < 1.0    | :x:              |

## Aggiornamenti di Sicurezza

Gli aggiornamenti di sicurezza vengono rilasciati:
- **Critical**: Entro 24 ore
- **High**: Entro 7 giorni
- **Medium**: Prossimo release
- **Low**: Valutazione caso per caso
