// API Helper Functions
const API = {
    // Ottieni token da localStorage
    getToken() {
        return localStorage.getItem(CONFIG.STORAGE.ACCESS_TOKEN);
    },

    // Salva token in localStorage
    saveToken(accessToken, refreshToken) {
        localStorage.setItem(CONFIG.STORAGE.ACCESS_TOKEN, accessToken);
        localStorage.setItem(CONFIG.STORAGE.REFRESH_TOKEN, refreshToken);
    },

    // Rimuovi token da localStorage
    clearToken() {
        localStorage.removeItem(CONFIG.STORAGE.ACCESS_TOKEN);
        localStorage.removeItem(CONFIG.STORAGE.REFRESH_TOKEN);
        localStorage.removeItem(CONFIG.STORAGE.USER_DATA);
    },

    // Headers per le richieste
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json',
        };

        if (includeAuth) {
            const token = this.getToken();
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
        }

        return headers;
    },

    // Richiesta generica
    async request(endpoint, options = {}) {
        const url = `${CONFIG.API_BASE_URL}${endpoint}`;
        const config = {
            ...options,
            headers: this.getHeaders(options.auth !== false),
        };

        try {
            UI.showLoading();
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || data.error || 'Errore nella richiesta');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        } finally {
            UI.hideLoading();
        }
    },

    // GET request
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },

    // POST request
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    // PUT request
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    // DELETE request
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    },

    // Login
    async login(username, password) {
        return this.request(CONFIG.ENDPOINTS.LOGIN, {
            method: 'POST',
            body: JSON.stringify({ username, password }),
            auth: false,
        });
    },

    // Fascicolo
    async getFascicolo() {
        return this.get(CONFIG.ENDPOINTS.FASCICOLO);
    },

    async createFascicolo(data) {
        return this.post(CONFIG.ENDPOINTS.FASCICOLO, data);
    },

    // Particelle
    async getParticelle(fascicoloId) {
        const params = fascicoloId ? `?fascicolo_id=${fascicoloId}` : '';
        return this.get(CONFIG.ENDPOINTS.PARTICELLE + params);
    },

    async createParticella(data, fascicoloId) {
        return this.post(CONFIG.ENDPOINTS.PARTICELLE + `?fascicolo_id=${fascicoloId}`, data);
    },

    // Domande
    async getDomande() {
        return this.get(CONFIG.ENDPOINTS.DOMANDE);
    },

    async getDomanda(id) {
        return this.get(`${CONFIG.ENDPOINTS.DOMANDE}/${id}`);
    },

    async createDomanda(data, fascicoloId) {
        return this.post(CONFIG.ENDPOINTS.DOMANDE + `?fascicolo_id=${fascicoloId}`, data);
    },

    async presentaDomanda(id) {
        return this.post(`${CONFIG.ENDPOINTS.DOMANDE}/${id}/presenta`, {});
    },

    async avviaIstruttoria(id) {
        return this.post(`${CONFIG.ENDPOINTS.DOMANDE}/${id}/istruttoria`, {});
    },

    async approvaDomanda(id) {
        return this.post(`${CONFIG.ENDPOINTS.DOMANDE}/${id}/approva`, {});
    },

    async respingiDomanda(id, motivo) {
        return this.post(`${CONFIG.ENDPOINTS.DOMANDE}/${id}/respingi?motivo=${encodeURIComponent(motivo)}`, {});
    },

    // Calcoli
    async calcolaContributo(domandaId) {
        return this.post(`${CONFIG.ENDPOINTS.CALCOLA}/${domandaId}`, {});
    },

    async getCalcolo(domandaId) {
        return this.get(`${CONFIG.ENDPOINTS.CALCOLI}/${domandaId}`);
    },

    // Colture
    async getColture() {
        return this.get(CONFIG.ENDPOINTS.COLTURE);
    },

    async createColtura(data) {
        return this.post(CONFIG.ENDPOINTS.COLTURE, data);
    },

    // Contributi
    async getContributi(campagnaId) {
        const params = campagnaId ? `?campagna_id=${campagnaId}` : '';
        return this.get(CONFIG.ENDPOINTS.CONTRIBUTI + params);
    },

    async createContributo(data) {
        return this.post(CONFIG.ENDPOINTS.CONTRIBUTI, data);
    },

    // Campagne
    async getCampagne() {
        return this.get(CONFIG.ENDPOINTS.CAMPAGNE);
    },

    // System
    async getHealth() {
        return this.get(CONFIG.ENDPOINTS.HEALTH);
    },

    async getStats() {
        return this.get(CONFIG.ENDPOINTS.STATS);
    },
};

// UI Helper Functions
const UI = {
    showLoading() {
        document.getElementById('loading').classList.remove('hidden');
    },

    hideLoading() {
        document.getElementById('loading').classList.add('hidden');
    },

    showError(message, elementId = 'login-error') {
        const errorEl = document.getElementById(elementId);
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.classList.remove('hidden');
        } else {
            alert(message);
        }
    },

    hideError(elementId = 'login-error') {
        const errorEl = document.getElementById(elementId);
        if (errorEl) {
            errorEl.classList.add('hidden');
        }
    },

    showModal(title, content) {
        document.getElementById('modal-title').textContent = title;
        document.getElementById('modal-body').innerHTML = content;
        document.getElementById('modal-overlay').classList.remove('hidden');
    },

    hideModal() {
        document.getElementById('modal-overlay').classList.add('hidden');
    },

    formatDate(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleDateString('it-IT');
    },

    formatCurrency(amount) {
        if (!amount && amount !== 0) return '-';
        return new Intl.NumberFormat('it-IT', {
            style: 'currency',
            currency: 'EUR'
        }).format(amount);
    },

    getStatusClass(status) {
        return `status-${status.toLowerCase().replace('_', '-')}`;
    }
};
