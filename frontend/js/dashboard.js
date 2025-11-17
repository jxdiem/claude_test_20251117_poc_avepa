// Dashboard Management
const Dashboard = {
    init() {
        this.setupTabs();
        this.setupModal();
        this.loadOverview();
    },

    // Setup tab navigation
    setupTabs() {
        const tabButtons = document.querySelectorAll('.tab-btn');

        tabButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const tabName = btn.dataset.tab;
                this.switchTab(tabName);
            });
        });
    },

    // Switch between tabs
    switchTab(tabName) {
        // Update active button
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update active content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`tab-content-${tabName}`).classList.add('active');

        // Load tab data
        this.loadTabData(tabName);
    },

    // Load data for specific tab
    async loadTabData(tabName) {
        switch (tabName) {
            case 'overview':
                await this.loadOverview();
                break;
            case 'fascicolo':
                await this.loadFascicolo();
                break;
            case 'domande':
                await this.loadDomande();
                break;
            case 'admin':
                await this.loadAdmin();
                break;
            case 'system':
                await this.loadSystem();
                break;
        }
    },

    // Load overview tab
    async loadOverview() {
        try {
            // Carica statistiche se sistemista
            if (Auth.currentUser.role === CONFIG.ROLES.SISTEMISTA) {
                const stats = await API.getStats();
                if (stats.success) {
                    document.getElementById('stat-fascicoli').textContent = stats.data.total_fascicoli || 0;
                    document.getElementById('stat-domande').textContent = stats.data.total_domande || 0;
                    document.getElementById('stat-colture').textContent = stats.data.total_colture_attive || 0;
                }
            } else {
                // Per altri ruoli, carica statistiche base
                const domande = await API.getDomande();
                document.getElementById('stat-domande').textContent = domande.data?.length || 0;
            }
        } catch (error) {
            console.error('Error loading overview:', error);
        }
    },

    // Load fascicolo tab
    async loadFascicolo() {
        const container = document.getElementById('fascicolo-container');

        try {
            const response = await API.getFascicolo();
            const fascicoli = response.data;

            if (!fascicoli || fascicoli.length === 0) {
                container.innerHTML = this.renderCreateFascicoloForm();
                this.setupFascicoloForm();
                return;
            }

            const fascicolo = fascicoli[0]; // Prendi il primo fascicolo
            container.innerHTML = this.renderFascicolo(fascicolo);
            this.setupParticelleManagement(fascicolo.id);

        } catch (error) {
            console.error('Error loading fascicolo:', error);
            container.innerHTML = '<p class="error">Errore nel caricamento del fascicolo</p>';
        }
    },

    // Render create fascicolo form
    renderCreateFascicoloForm() {
        return `
            <div class="card">
                <h3>Crea Nuovo Fascicolo</h3>
                <form id="fascicolo-form">
                    <div class="form-group">
                        <label>Ragione Sociale</label>
                        <input type="text" name="ragione_sociale" required>
                    </div>
                    <div class="form-group">
                        <label>CF/P.IVA</label>
                        <input type="text" name="cf_piva" required>
                    </div>
                    <div class="form-group">
                        <label>Indirizzo</label>
                        <input type="text" name="indirizzo" required>
                    </div>
                    <div class="form-group">
                        <label>CAP</label>
                        <input type="text" name="cap" pattern="[0-9]{5}" required>
                    </div>
                    <div class="form-group">
                        <label>Comune</label>
                        <input type="text" name="comune" required>
                    </div>
                    <div class="form-group">
                        <label>Provincia</label>
                        <input type="text" name="provincia" maxlength="2" required>
                    </div>
                    <div class="form-group">
                        <label>Telefono</label>
                        <input type="tel" name="telefono">
                    </div>
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" name="email">
                    </div>
                    <button type="submit" class="btn btn-primary">Crea Fascicolo</button>
                </form>
            </div>
        `;
    },

    // Render fascicolo
    renderFascicolo(fascicolo) {
        return `
            <div class="card">
                <h3>${fascicolo.ragione_sociale}</h3>
                <p><strong>CF/P.IVA:</strong> ${fascicolo.cf_piva}</p>
                <p><strong>Indirizzo:</strong> ${fascicolo.indirizzo}, ${fascicolo.cap} ${fascicolo.comune} (${fascicolo.provincia})</p>
                <p><strong>Telefono:</strong> ${fascicolo.telefono || '-'}</p>
                <p><strong>Email:</strong> ${fascicolo.email || '-'}</p>
            </div>

            <div class="card">
                <h3>Particelle Catastali</h3>
                <div id="particelle-list"></div>
                <button class="btn btn-primary btn-sm" id="btn-add-particella">Aggiungi Particella</button>
            </div>
        `;
    },

    // Setup fascicolo form
    setupFascicoloForm() {
        const form = document.getElementById('fascicolo-form');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);

            try {
                await API.createFascicolo(data);
                alert('Fascicolo creato con successo!');
                this.loadFascicolo();
            } catch (error) {
                alert('Errore nella creazione del fascicolo');
            }
        });
    },

    // Setup particelle management
    async setupParticelleManagement(fascicoloId) {
        const listContainer = document.getElementById('particelle-list');

        try {
            const response = await API.getParticelle(fascicoloId);
            const particelle = response.data;

            if (particelle && particelle.length > 0) {
                listContainer.innerHTML = `
                    <table>
                        <thead>
                            <tr>
                                <th>Comune</th>
                                <th>Foglio</th>
                                <th>Particella</th>
                                <th>Superficie (mq)</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${particelle.map(p => `
                                <tr>
                                    <td>${p.comune}</td>
                                    <td>${p.foglio}</td>
                                    <td>${p.particella}</td>
                                    <td>${p.superficie_mq.toLocaleString('it-IT')}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `;
            } else {
                listContainer.innerHTML = '<p>Nessuna particella catastale inserita.</p>';
            }
        } catch (error) {
            listContainer.innerHTML = '<p class="error">Errore nel caricamento delle particelle</p>';
        }

        // Setup add particella button
        document.getElementById('btn-add-particella')?.addEventListener('click', () => {
            this.showAddParticellaModal(fascicoloId);
        });
    },

    // Show add particella modal
    showAddParticellaModal(fascicoloId) {
        const content = `
            <form id="particella-form">
                <div class="form-group">
                    <label>Comune</label>
                    <input type="text" name="comune" required>
                </div>
                <div class="form-group">
                    <label>Foglio</label>
                    <input type="text" name="foglio" required>
                </div>
                <div class="form-group">
                    <label>Particella</label>
                    <input type="text" name="particella" required>
                </div>
                <div class="form-group">
                    <label>Superficie (mq)</label>
                    <input type="number" name="superficie_mq" required>
                </div>
                <button type="submit" class="btn btn-primary">Aggiungi</button>
            </form>
        `;

        UI.showModal('Aggiungi Particella Catastale', content);

        document.getElementById('particella-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            data.superficie_mq = parseFloat(data.superficie_mq);

            try {
                await API.createParticella(data, fascicoloId);
                UI.hideModal();
                this.loadFascicolo();
                alert('Particella aggiunta con successo!');
            } catch (error) {
                alert('Errore nell\'aggiunta della particella');
            }
        });
    },

    // Load domande tab
    async loadDomande() {
        const container = document.getElementById('domande-container');

        try {
            const response = await API.getDomande();
            const domande = response.data;

            if (!domande || domande.length === 0) {
                container.innerHTML = `
                    <p>Nessuna domanda presente.</p>
                    <button class="btn btn-primary" id="btn-create-domanda">Crea Nuova Domanda</button>
                `;
                return;
            }

            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Anno</th>
                            <th>Stato</th>
                            <th>Data Presentazione</th>
                            <th>Importo Calcolato</th>
                            <th>Azioni</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${domande.map(d => `
                            <tr>
                                <td>${d.id}</td>
                                <td>${d.anno_campagna}</td>
                                <td><span class="status-badge ${UI.getStatusClass(d.stato)}">${d.stato}</span></td>
                                <td>${UI.formatDate(d.data_presentazione)}</td>
                                <td>${UI.formatCurrency(d.importo_calcolato)}</td>
                                <td>
                                    ${this.renderDomandaActions(d)}
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
                <button class="btn btn-primary" id="btn-create-domanda" style="margin-top: 20px;">Crea Nuova Domanda</button>
            `;

            this.setupDomandeActions();

        } catch (error) {
            console.error('Error loading domande:', error);
            container.innerHTML = '<p class="error">Errore nel caricamento delle domande</p>';
        }
    },

    // Render domanda actions
    renderDomandaActions(domanda) {
        const role = Auth.currentUser.role;
        const stato = domanda.stato;
        let actions = '';

        if (role === CONFIG.ROLES.BENEFICIARIO && stato === 'BOZZA') {
            actions += `<button class="btn btn-success btn-sm" onclick="Dashboard.presentaDomanda(${domanda.id})">Presenta</button>`;
        }

        if (role === CONFIG.ROLES.ISTRUTTORE) {
            if (stato === 'PRESENTATA') {
                actions += `<button class="btn btn-primary btn-sm" onclick="Dashboard.avviaIstruttoria(${domanda.id})">Prendi in Carico</button>`;
            }
            if (stato === 'IN_ISTRUTTORIA') {
                actions += `
                    <button class="btn btn-primary btn-sm" onclick="Dashboard.calcolaContributo(${domanda.id})">Calcola</button>
                    <button class="btn btn-success btn-sm" onclick="Dashboard.approvaDomanda(${domanda.id})">Approva</button>
                    <button class="btn btn-danger btn-sm" onclick="Dashboard.respingiDomanda(${domanda.id})">Respingi</button>
                `;
            }
        }

        return actions;
    },

    // Setup domande actions
    setupDomandeActions() {
        document.getElementById('btn-create-domanda')?.addEventListener('click', () => {
            alert('Funzione in sviluppo: Creazione nuova domanda');
        });
    },

    // Presenta domanda
    async presentaDomanda(id) {
        if (!confirm('Sei sicuro di voler presentare questa domanda?')) return;

        try {
            await API.presentaDomanda(id);
            alert('Domanda presentata con successo!');
            this.loadDomande();
        } catch (error) {
            alert('Errore nella presentazione della domanda');
        }
    },

    // Avvia istruttoria
    async avviaIstruttoria(id) {
        if (!confirm('Vuoi prendere in carico questa domanda?')) return;

        try {
            await API.avviaIstruttoria(id);
            alert('Domanda presa in carico!');
            this.loadDomande();
        } catch (error) {
            alert('Errore nell\'avvio istruttoria');
        }
    },

    // Calcola contributo
    async calcolaContributo(id) {
        try {
            const result = await API.calcolaContributo(id);
            alert(`Contributo calcolato: ${UI.formatCurrency(result.data.importo_totale)}`);
            this.loadDomande();
        } catch (error) {
            alert('Errore nel calcolo del contributo');
        }
    },

    // Approva domanda
    async approvaDomanda(id) {
        if (!confirm('Sei sicuro di voler approvare questa domanda?')) return;

        try {
            await API.approvaDomanda(id);
            alert('Domanda approvata!');
            this.loadDomande();
        } catch (error) {
            alert('Errore nell\'approvazione');
        }
    },

    // Respingi domanda
    async respingiDomanda(id) {
        const motivo = prompt('Inserisci il motivo del respingimento:');
        if (!motivo) return;

        try {
            await API.respingiDomanda(id, motivo);
            alert('Domanda respinta');
            this.loadDomande();
        } catch (error) {
            alert('Errore nel respingimento');
        }
    },

    // Load admin tab
    async loadAdmin() {
        await this.loadColture();
        await this.loadContributi();
    },

    async loadColture() {
        const container = document.getElementById('colture-list');

        try {
            const response = await API.getColture();
            const colture = response.data;

            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>Codice</th>
                            <th>Descrizione</th>
                            <th>Attiva</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${colture.map(c => `
                            <tr>
                                <td>${c.codice}</td>
                                <td>${c.descrizione}</td>
                                <td>${c.attiva ? '✓' : '✗'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } catch (error) {
            container.innerHTML = '<p class="error">Errore nel caricamento colture</p>';
        }
    },

    async loadContributi() {
        const container = document.getElementById('contributi-list');

        try {
            const response = await API.getContributi();
            const contributi = response.data;

            container.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>Coltura</th>
                            <th>Importo/mq</th>
                            <th>Massimale Superficie</th>
                            <th>Massimale Importo</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${contributi.map(c => `
                            <tr>
                                <td>${c.coltura_descrizione}</td>
                                <td>${UI.formatCurrency(c.importo_per_mq)}</td>
                                <td>${c.massimale_superficie ? c.massimale_superficie.toLocaleString() : '-'} mq</td>
                                <td>${c.massimale_importo ? UI.formatCurrency(c.massimale_importo) : '-'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } catch (error) {
            container.innerHTML = '<p class="error">Errore nel caricamento contributi</p>';
        }
    },

    // Load system tab
    async loadSystem() {
        await this.loadHealth();
        await this.loadSystemStats();
    },

    async loadHealth() {
        const container = document.getElementById('health-status');

        try {
            const response = await API.getHealth();

            container.innerHTML = `
                <div class="card">
                    <h3>Stato Servizi</h3>
                    <p><strong>Overall Status:</strong> <span class="status-badge status-${response.overall_status}">${response.overall_status}</span></p>
                    <table>
                        <thead>
                            <tr>
                                <th>Servizio</th>
                                <th>Stato</th>
                                <th>Response Time</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${Object.entries(response.services).map(([name, data]) => `
                                <tr>
                                    <td>${name}</td>
                                    <td><span class="status-badge status-${data.status}">${data.status}</span></td>
                                    <td>${data.response_time_ms} ms</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        } catch (error) {
            container.innerHTML = '<p class="error">Errore nel caricamento stato servizi</p>';
        }
    },

    async loadSystemStats() {
        const container = document.getElementById('system-stats');

        try {
            const response = await API.getStats();
            const stats = response.data;

            container.innerHTML = `
                <div class="card">
                    <h3>Statistiche Sistema</h3>
                    <p><strong>Utenti Totali:</strong> ${stats.total_users}</p>
                    <p><strong>Fascicoli:</strong> ${stats.total_fascicoli}</p>
                    <p><strong>Particelle:</strong> ${stats.total_particelle}</p>
                    <p><strong>Domande:</strong> ${stats.total_domande}</p>
                    <p><strong>Colture Attive:</strong> ${stats.total_colture_attive}</p>
                </div>
            `;
        } catch (error) {
            container.innerHTML = '<p class="error">Errore nel caricamento statistiche</p>';
        }
    },

    // Setup modal
    setupModal() {
        document.querySelector('.modal-close').addEventListener('click', () => {
            UI.hideModal();
        });

        document.getElementById('modal-overlay').addEventListener('click', (e) => {
            if (e.target.id === 'modal-overlay') {
                UI.hideModal();
            }
        });
    }
};
