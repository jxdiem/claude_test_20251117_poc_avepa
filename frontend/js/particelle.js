/**
 * Particelle Module - Gestione particelle catastali con mappa
 */

const ParticelleManager = {
    mapManager: null,
    currentFascicoloId: null,
    particelle: [],

    /**
     * Inizializza il gestore particelle
     */
    init(fascicoloId) {
        this.currentFascicoloId = fascicoloId;
        this.render();
        this.loadParticelle();
    },

    /**
     * Render della sezione particelle
     */
    render() {
        const container = document.getElementById('particelle-section');
        if (!container) return;

        container.innerHTML = `
            <div class="map-info-panel">
                <h4>📍 Mappa Particelle</h4>
                <p>Disegna le particelle catastali sulla mappa. Usa gli strumenti di disegno per creare poligoni o rettangoli.</p>

                <div class="map-stats">
                    <div class="map-stat-item">
                        <label>Area disegnata:</label>
                        <strong id="current-area">-</strong>
                    </div>
                    <div class="map-stat-item">
                        <label>Centroide:</label>
                        <strong id="current-centroid">-</strong>
                    </div>
                </div>
            </div>

            <div class="map-container">
                <div id="particelle-map"></div>
            </div>

            <div class="card">
                <h3>Elenco Particelle</h3>
                <div id="particelle-list-container"></div>
                <button class="btn btn-primary" id="btn-add-particella-modal">
                    ➕ Aggiungi Nuova Particella
                </button>
            </div>
        `;

        // Inizializza mappa
        this.initMap();

        // Setup eventi
        document.getElementById('btn-add-particella-modal').addEventListener('click', () => {
            this.showAddParticellaModal();
        });
    },

    /**
     * Inizializza la mappa
     */
    initMap() {
        this.mapManager = new MapManager('particelle-map');
        this.mapManager.init({
            center: [45.4408, 12.3155], // Default Venezia, cambierà al primo zoom
            zoom: 8,
            editable: true
        });

        // Callback quando cambia la geometria
        this.mapManager.onGeometryChange = (geojson, area, centroid) => {
            // Aggiorna UI
            document.getElementById('current-area').textContent =
                `${(area / 10000).toFixed(2)} ha (${area.toFixed(0)} m²)`;

            document.getElementById('current-centroid').textContent =
                `${centroid.lat.toFixed(6)}, ${centroid.lng.toFixed(6)}`;
        };
    },

    /**
     * Carica particelle dal server
     */
    async loadParticelle() {
        try {
            const response = await API.getParticelle(this.currentFascicoloId);
            this.particelle = response.data || [];
            this.renderParticelleList();
            this.loadParticelleOnMap();
        } catch (error) {
            console.error('Error loading particelle:', error);
        }
    },

    /**
     * Render lista particelle
     */
    renderParticelleList() {
        const container = document.getElementById('particelle-list-container');

        if (!this.particelle || this.particelle.length === 0) {
            container.innerHTML = '<p>Nessuna particella presente. Aggiungi la prima particella.</p>';
            return;
        }

        container.innerHTML = '<div class="particelle-list">' +
            this.particelle.map(p => `
                <div class="particella-item" data-id="${p.id}">
                    <div class="particella-info">
                        <h4>
                            ${p.comune} - Foglio ${p.foglio}, Particella ${p.particella}
                            ${p.coordinate_geojson ?
                                '<span class="geometry-badge has-geometry">✓ Geometria</span>' :
                                '<span class="geometry-badge no-geometry">⚠ No geometria</span>'
                            }
                        </h4>
                        <p><strong>Superficie dichiarata:</strong> ${(p.superficie_mq / 10000).toFixed(2)} ha</p>
                        ${p.superficie_calcolata_mq ?
                            `<p><strong>Superficie calcolata:</strong> ${(p.superficie_calcolata_mq / 10000).toFixed(2)} ha</p>` :
                            ''
                        }
                        ${p.subalterno ? `<p><strong>Subalterno:</strong> ${p.subalterno}</p>` : ''}
                    </div>
                    <div class="particella-actions">
                        ${p.centroid_lat && p.centroid_lng ? `
                            <button class="btn-map-zoom" data-lat="${p.centroid_lat}" data-lng="${p.centroid_lng}" data-geojson='${p.coordinate_geojson || ''}'>
                                🔍 Zoom
                            </button>
                        ` : ''}
                        <button class="btn btn-sm" onclick="ParticelleManager.editParticella(${p.id})">
                            ✏️ Modifica
                        </button>
                    </div>
                </div>
            `).join('') +
            '</div>';

        // Setup zoom buttons
        container.querySelectorAll('.btn-map-zoom').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const lat = parseFloat(e.target.dataset.lat);
                const lng = parseFloat(e.target.dataset.lng);
                const geojson = e.target.dataset.geojson;

                if (geojson && geojson !== 'null') {
                    this.mapManager.loadGeometry(geojson, true);
                } else {
                    this.mapManager.zoomTo(lat, lng);
                }
            });
        });
    },

    /**
     * Carica particelle sulla mappa
     */
    loadParticelleOnMap() {
        // Per ora mostra solo la prima particella con geometria
        const particellaConGeometria = this.particelle.find(p => p.coordinate_geojson);
        if (particellaConGeometria && particellaConGeometria.coordinate_geojson) {
            this.mapManager.loadGeometry(particellaConGeometria.coordinate_geojson, true);
        }
    },

    /**
     * Mostra modal per aggiungere particella
     */
    showAddParticellaModal() {
        const geometry = this.mapManager.getGeometry();
        const area = this.mapManager.getArea();

        let centroid = null;
        if (geometry) {
            // Calcola centroide dalla geometria
            const layers = this.mapManager.drawnItems.getLayers();
            if (layers.length > 0) {
                centroid = this.mapManager.calculateCentroid(layers[0]);
            }
        }

        const modalBody = `
            <form id="add-particella-form">
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
                    <label>Subalterno (opzionale)</label>
                    <input type="text" name="subalterno">
                </div>
                <div class="form-group">
                    <label>Superficie catastale (ha)</label>
                    <input type="number" name="superficie_ha" step="0.01" min="0" required>
                </div>

                ${geometry ? `
                    <div class="map-info-panel">
                        <h4>✅ Geometria disegnata</h4>
                        <p><strong>Area calcolata:</strong> ${(area / 10000).toFixed(2)} ha (${area.toFixed(0)} m²)</p>
                        <p><strong>Centroide:</strong> ${centroid.lat.toFixed(6)}, ${centroid.lng.toFixed(6)}</p>
                    </div>
                ` : `
                    <div class="map-info-panel" style="background: #fff3cd; border: 1px solid #ffc107;">
                        <p>⚠️ Nessuna geometria disegnata sulla mappa. Puoi comunque salvare la particella e aggiungere la geometria in seguito.</p>
                    </div>
                `}

                <div style="margin-top: 20px; display: flex; gap: 10px;">
                    <button type="submit" class="btn btn-primary">Salva Particella</button>
                    <button type="button" class="btn btn-secondary modal-close">Annulla</button>
                </div>
            </form>
        `;

        showModal('Aggiungi Particella Catastale', modalBody);

        // Setup form submit
        document.getElementById('add-particella-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.saveParticella(e.target, geometry, area, centroid);
        });
    },

    /**
     * Salva particella
     */
    async saveParticella(form, geometry, area, centroid) {
        const formData = new FormData(form);
        const data = {
            comune: formData.get('comune'),
            foglio: formData.get('foglio'),
            particella: formData.get('particella'),
            subalterno: formData.get('subalterno') || null,
            superficie_mq: parseFloat(formData.get('superficie_ha')) * 10000,
            superficie_calcolata_mq: area > 0 ? area : null,
            coordinate_geojson: geometry ? JSON.stringify(geometry) : null,
            centroid_lat: centroid ? centroid.lat : null,
            centroid_lng: centroid ? centroid.lng : null
        };

        try {
            showLoading();
            await API.createParticella(data, this.currentFascicoloId);
            hideLoading();
            hideModal();
            alert('Particella aggiunta con successo!');

            // Ricarica particelle
            this.mapManager.clear();
            await this.loadParticelle();
        } catch (error) {
            hideLoading();
            console.error('Error saving particella:', error);
            alert('Errore nel salvataggio della particella');
        }
    },

    /**
     * Modifica particella (placeholder)
     */
    editParticella(id) {
        alert(`Modifica particella ${id} - Funzionalità da implementare`);
    }
};

// Esporta per uso globale
window.ParticelleManager = ParticelleManager;
