// Configurazione API
const CONFIG = {
    // URL base dell'API Gateway
    // Cambia questo con l'URL di Railway in produzione
    API_BASE_URL: window.location.hostname === 'localhost'
        ? 'http://localhost:8000'
        : window.location.origin,

    // Endpoints
    ENDPOINTS: {
        LOGIN: '/api/v1/auth/login',
        REFRESH: '/api/v1/auth/refresh',
        USERS: '/api/v1/auth/users',

        FASCICOLO: '/api/v1/beneficiaries/fascicolo',
        PARTICELLE: '/api/v1/beneficiaries/particelle',
        DATI_BANCARI: '/api/v1/beneficiaries/dati-bancari',
        MACCHINARI: '/api/v1/beneficiaries/macchinari',

        DOMANDE: '/api/v1/requests/domande',

        CALCOLA: '/api/v1/calculations/calcola',
        CALCOLI: '/api/v1/calculations/calcoli',

        COLTURE: '/api/v1/admin/colture',
        CONTRIBUTI: '/api/v1/admin/contributi',
        CAMPAGNE: '/api/v1/admin/campagne',

        HEALTH: '/api/v1/system/health',
        STATS: '/api/v1/system/stats',
    },

    // Storage keys
    STORAGE: {
        ACCESS_TOKEN: 'access_token',
        REFRESH_TOKEN: 'refresh_token',
        USER_DATA: 'user_data',
    },

    // Ruoli utente
    ROLES: {
        BENEFICIARIO: 'BENEFICIARIO',
        ISTRUTTORE: 'ISTRUTTORE',
        AMMINISTRATORE: 'AMMINISTRATORE',
        SISTEMISTA: 'SISTEMISTA',
    },

    // Stati domanda
    STATI_DOMANDA: {
        BOZZA: 'BOZZA',
        PRESENTATA: 'PRESENTATA',
        IN_ISTRUTTORIA: 'IN_ISTRUTTORIA',
        APPROVATA: 'APPROVATA',
        RESPINTA: 'RESPINTA',
        LIQUIDATA: 'LIQUIDATA',
    }
};
