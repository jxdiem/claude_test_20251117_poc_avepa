# Frontend - Sistema Gestione Aiuti Agricoltura

Interfaccia web per il sistema di gestione aiuti all'agricoltura.

## Caratteristiche

- ✅ **Single Page Application** (SPA) in vanilla JavaScript
- ✅ **Responsive Design** - Funziona su desktop e mobile
- ✅ **Autenticazione JWT** con localStorage
- ✅ **Dashboard per 4 ruoli utente**:
  - **BENEFICIARIO**: Gestione fascicolo e domande
  - **ISTRUTTORE**: Istruttoria e calcolo contributi
  - **AMMINISTRATORE**: Gestione colture e contributi
  - **SISTEMISTA**: Monitoring e statistiche sistema
- ✅ **UI moderna** con gradienti e animazioni
- ✅ **Nessuna dipendenza esterna** - Solo HTML, CSS, JS

## Quick Start

### 1. Avvia il Backend

```bash
# Opzione A: Sviluppo locale
cd services/auth && python main.py  # Terminal 1
cd api-gateway && python main.py    # Terminal 2

# Opzione B: Docker Compose
docker-compose up
```

### 2. Apri il Frontend

Hai 3 opzioni:

#### Opzione A: Server Python (Consigliata)

```bash
cd frontend
python -m http.server 3000
```

Apri: **http://localhost:3000**

#### Opzione B: Live Server (VS Code)

1. Installa estensione "Live Server" in VS Code
2. Click destro su `index.html` → "Open with Live Server"

#### Opzione C: Direttamente dal filesystem

Apri `frontend/index.html` nel browser (alcune funzionalità potrebbero non funzionare per CORS)

### 3. Login

**Utenti Demo**:
- `admin` / `password123` - Amministratore
- `sistemista` / `password123` - Sistemista
- `istruttore1` / `password123` - Istruttore
- `beneficiario1` / `password123` - Beneficiario

**Tip**: Puoi cliccare direttamente sugli utenti demo per login rapido!

## Configurazione API

Il frontend si connette automaticamente all'API Gateway:

- **Sviluppo locale**: `http://localhost:8000`
- **Produzione**: Automaticamente rileva l'URL corrente

Per cambiare l'URL dell'API, modifica `frontend/js/config.js`:

```javascript
const CONFIG = {
    API_BASE_URL: 'https://your-railway-url.com',
    // ...
};
```

## Struttura File

```
frontend/
├── index.html          # Pagina principale
├── css/
│   └── style.css      # Stili CSS
├── js/
│   ├── config.js      # Configurazione (API URL, costanti)
│   ├── api.js         # Helper per chiamate API
│   ├── auth.js        # Gestione autenticazione
│   ├── dashboard.js   # Logica dashboard
│   └── app.js         # Inizializzazione app
└── README.md
```

## Funzionalità per Ruolo

### BENEFICIARIO

- ✅ Creazione fascicolo aziendale
- ✅ Gestione particelle catastali
- ✅ Visualizzazione domande proprie
- ✅ Presentazione domande

### ISTRUTTORE

- ✅ Visualizzazione tutte le domande
- ✅ Presa in carico domande (avvio istruttoria)
- ✅ Calcolo contributi
- ✅ Approvazione/respingimento domande

### AMMINISTRATORE

- ✅ Visualizzazione colture
- ✅ Gestione contributi unitari
- ✅ Gestione campagne
- ✅ (Aggiunta colture - in sviluppo)

### SISTEMISTA

- ✅ Health check di tutti i servizi
- ✅ Statistiche sistema
- ✅ Monitoring in tempo reale

## Sviluppo

### Aggiungere Nuove Funzionalità

1. **Nuovo Endpoint API**: Aggiungi in `js/api.js`

```javascript
async getMyNewEndpoint() {
    return this.get('/api/v1/my/endpoint');
}
```

2. **Nuova UI**: Aggiungi in `js/dashboard.js`

```javascript
async loadMyNewTab() {
    const data = await API.getMyNewEndpoint();
    // Render UI
}
```

3. **Nuovo Tab**: Aggiungi in `index.html`

```html
<button class="tab-btn" data-tab="mytab">My Tab</button>
<div id="tab-content-mytab" class="tab-content">...</div>
```

### Debug

Apri DevTools (F12) → Console per vedere:
- Chiamate API
- Errori
- Dati ricevuti

### CORS Issues

Se hai problemi CORS in locale:

1. Usa Python HTTP server (opzione consigliata)
2. Oppure aggiungi CORS al backend in `shared/config.py`:

```python
CORS_ORIGINS = ["http://localhost:3000", "*"]
```

## Deploy

### Opzione 1: Deploy con Backend (Railway)

1. Copia `frontend/` nella root del progetto Railway
2. Configura Railway per servire file statici
3. Frontend e backend sullo stesso dominio = no CORS issues

### Opzione 2: Deploy Separato (Netlify/Vercel)

1. **Netlify/Vercel**: Deploy `frontend/` folder
2. **Aggiorna config**: Modifica `API_BASE_URL` con URL Railway del backend
3. **CORS**: Aggiungi il dominio frontend al CORS del backend

### Opzione 3: Servizio Statico Railway

1. Crea nuovo servizio Railway
2. **Build Command**: (vuoto)
3. **Static Files**: `/frontend`

## Personalizzazione

### Cambiare Colori

Modifica in `css/style.css`:

```css
/* Gradiente principale */
background: linear-gradient(135deg, #TUO_COLORE1, #TUO_COLORE2);

/* Colore primario */
.btn-primary {
    background: #TUO_COLORE;
}
```

### Aggiungere Logo

1. Salva logo in `frontend/assets/logo.png`
2. Aggiungi in `index.html`:

```html
<header>
    <img src="assets/logo.png" alt="Logo" height="40">
    <h1>Sistema Gestione Aiuti</h1>
</header>
```

## Browser Supportati

- ✅ Chrome/Edge (versione recente)
- ✅ Firefox (versione recente)
- ✅ Safari (versione recente)
- ⚠️ IE11: Non supportato (usa ES6+)

## Troubleshooting

### "Credenziali non valide"

- Verifica che il backend sia avviato
- Controlla `API_BASE_URL` in `config.js`
- Apri DevTools Network tab per vedere la richiesta

### "Errore nel caricamento"

- Verifica che l'API Gateway risponda: `curl http://localhost:8000`
- Controlla CORS configuration
- Verifica il token in localStorage (DevTools → Application → Local Storage)

### Token scaduto

- Il token JWT scade dopo 30 minuti
- Fai logout e login di nuovo
- (Auto-refresh in sviluppo)

## Roadmap Frontend

- [ ] Auto-refresh token JWT
- [ ] Creazione domanda con wizard
- [ ] Upload documenti
- [ ] Export dati in Excel/PDF
- [ ] Grafici e dashboard analytics
- [ ] Notifiche in-app
- [ ] Dark mode
- [ ] Internazionalizzazione (i18n)
- [ ] PWA support (offline mode)

## Contribuire

Per contribuire al frontend:

1. Fork del repository
2. Crea branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m 'Add my feature'`
4. Push: `git push origin feature/my-feature`
5. Apri Pull Request

## Licenza

Stesso progetto del backend - Open source per scopi didattici.

## Support

Per problemi o domande:
- Apri issue su GitHub
- Email: jxdiem@gmail.com
