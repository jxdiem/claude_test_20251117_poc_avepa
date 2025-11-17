// Authentication Management
const Auth = {
    currentUser: null,

    // Inizializza autenticazione
    init() {
        this.checkAuth();
        this.setupLogout();
    },

    // Verifica se l'utente è autenticato
    checkAuth() {
        const token = API.getToken();
        const userData = localStorage.getItem(CONFIG.STORAGE.USER_DATA);

        if (token && userData) {
            this.currentUser = JSON.parse(userData);
            this.showDashboard();
        } else {
            this.showLogin();
        }
    },

    // Mostra pagina di login
    showLogin() {
        document.getElementById('login-page').classList.remove('hidden');
        document.getElementById('dashboard-page').classList.add('hidden');
        document.getElementById('app-header').classList.add('hidden');
    },

    // Mostra dashboard
    showDashboard() {
        document.getElementById('login-page').classList.add('hidden');
        document.getElementById('dashboard-page').classList.remove('hidden');
        document.getElementById('app-header').classList.remove('hidden');

        this.updateUserInfo();
        this.setupRoleBasedUI();
        Dashboard.init();
    },

    // Aggiorna info utente nell'header
    updateUserInfo() {
        if (this.currentUser) {
            document.getElementById('user-name').textContent = this.currentUser.username;
            document.getElementById('user-role').textContent = this.currentUser.role;
        }
    },

    // Setup UI basata sul ruolo
    setupRoleBasedUI() {
        const role = this.currentUser?.role;

        // Mostra/nascondi tab basate sul ruolo
        const adminTab = document.getElementById('tab-admin');
        const systemTab = document.getElementById('tab-system');

        if (role === CONFIG.ROLES.AMMINISTRATORE) {
            adminTab.classList.remove('hidden');
        }

        if (role === CONFIG.ROLES.SISTEMISTA) {
            systemTab.classList.remove('hidden');
        }

        // Per istruttori, mostra tutte le domande
        if (role === CONFIG.ROLES.ISTRUTTORE) {
            document.getElementById('tab-domande').textContent = 'Istruttoria Domande';
        }
    },

    // Login
    async login(username, password) {
        try {
            const response = await API.login(username, password);

            if (response.success) {
                // Salva token e dati utente
                API.saveToken(response.access_token, response.refresh_token);

                this.currentUser = {
                    id: response.user_id,
                    username: response.username,
                    role: response.role,
                };

                localStorage.setItem(CONFIG.STORAGE.USER_DATA, JSON.stringify(this.currentUser));

                this.showDashboard();
                UI.hideError();
            }
        } catch (error) {
            UI.showError('Credenziali non valide. Riprova.');
            throw error;
        }
    },

    // Logout
    logout() {
        API.clearToken();
        this.currentUser = null;
        this.showLogin();
    },

    // Setup evento logout
    setupLogout() {
        document.getElementById('logout-btn').addEventListener('click', () => {
            this.logout();
        });
    },

    // Verifica permesso
    hasPermission(permission) {
        const role = this.currentUser?.role;
        const permissions = {
            [CONFIG.ROLES.BENEFICIARIO]: ['fascicolo:own', 'domanda:own'],
            [CONFIG.ROLES.ISTRUTTORE]: ['fascicolo:all', 'domanda:all', 'calcolo'],
            [CONFIG.ROLES.AMMINISTRATORE]: ['admin', 'fascicolo:all', 'domanda:all'],
            [CONFIG.ROLES.SISTEMISTA]: ['system', 'stats'],
        };

        return permissions[role]?.includes(permission) || false;
    }
};
