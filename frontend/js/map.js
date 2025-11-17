/**
 * Map Module - Gestione mappa interattiva con disegno geometrie
 * Usa Leaflet + Leaflet.draw per disegnare poligoni
 */

class MapManager {
    constructor(containerId) {
        this.containerId = containerId;
        this.map = null;
        this.drawnItems = null;
        this.drawControl = null;
        this.currentGeometry = null;
        this.currentArea = 0;
        this.onGeometryChange = null; // Callback quando la geometria cambia
    }

    /**
     * Inizializza la mappa
     */
    init(options = {}) {
        const {
            center = [45.4408, 12.3155], // Default: Venezia
            zoom = 13,
            editable = true
        } = options;

        // Crea mappa
        this.map = L.map(this.containerId).setView(center, zoom);

        // Layer base
        const baseLayers = {
            'Satellitare': L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
                maxZoom: 19
            }),
            'Topografica': L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
                attribution: 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)',
                maxZoom: 17
            }),
            'Stradale': L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                maxZoom: 19
            })
        };

        // Aggiungi layer default
        baseLayers['Stradale'].addTo(this.map);

        // Aggiungi controllo layer
        L.control.layers(baseLayers).addTo(this.map);

        if (editable) {
            this.initDrawControls();
        }

        // Aggiungi scala
        L.control.scale({ metric: true, imperial: false }).addTo(this.map);
    }

    /**
     * Inizializza controlli di disegno
     */
    initDrawControls() {
        // Layer per contenere le geometrie disegnate
        this.drawnItems = new L.FeatureGroup();
        this.map.addLayer(this.drawnItems);

        // Controllo disegno
        this.drawControl = new L.Control.Draw({
            position: 'topright',
            draw: {
                polygon: {
                    allowIntersection: false,
                    showArea: true,
                    metric: true,
                    shapeOptions: {
                        color: '#3388ff',
                        fillOpacity: 0.4
                    }
                },
                rectangle: {
                    showArea: true,
                    metric: true,
                    shapeOptions: {
                        color: '#3388ff',
                        fillOpacity: 0.4
                    }
                },
                circle: false,
                circlemarker: false,
                polyline: false,
                marker: false
            },
            edit: {
                featureGroup: this.drawnItems,
                remove: true
            }
        });
        this.map.addControl(this.drawControl);

        // Eventi disegno
        this.map.on(L.Draw.Event.CREATED, (e) => {
            const layer = e.layer;

            // Rimuovi geometrie precedenti (solo una geometria per volta)
            this.drawnItems.clearLayers();

            // Aggiungi nuova geometria
            this.drawnItems.addLayer(layer);

            // Salva geometria
            this.updateGeometry();
        });

        this.map.on(L.Draw.Event.EDITED, () => {
            this.updateGeometry();
        });

        this.map.on(L.Draw.Event.DELETED, () => {
            this.currentGeometry = null;
            this.currentArea = 0;
            if (this.onGeometryChange) {
                this.onGeometryChange(null, 0);
            }
        });
    }

    /**
     * Aggiorna geometria corrente
     */
    updateGeometry() {
        const layers = this.drawnItems.getLayers();
        if (layers.length === 0) {
            this.currentGeometry = null;
            this.currentArea = 0;
            return;
        }

        const layer = layers[0];
        const geojson = layer.toGeoJSON();

        // Calcola area in m²
        this.currentArea = L.GeometryUtil.geodesicArea(layer.getLatLngs()[0]);

        // Salva GeoJSON
        this.currentGeometry = geojson;

        // Callback
        if (this.onGeometryChange) {
            const centroid = this.calculateCentroid(layer);
            this.onGeometryChange(geojson, this.currentArea, centroid);
        }
    }

    /**
     * Calcola il centroide di un layer
     */
    calculateCentroid(layer) {
        const bounds = layer.getBounds();
        const center = bounds.getCenter();
        return {
            lat: center.lat,
            lng: center.lng
        };
    }

    /**
     * Carica geometria sulla mappa
     */
    loadGeometry(geojson, zoomTo = true) {
        if (!geojson) return;

        // Parse GeoJSON se è stringa
        const geometry = typeof geojson === 'string' ? JSON.parse(geojson) : geojson;

        // Rimuovi geometrie precedenti
        if (this.drawnItems) {
            this.drawnItems.clearLayers();
        }

        // Aggiungi geometria
        const layer = L.geoJSON(geometry, {
            style: {
                color: '#3388ff',
                fillOpacity: 0.4
            }
        });

        if (this.drawnItems) {
            this.drawnItems.addLayer(layer.getLayers()[0]);
        } else {
            layer.addTo(this.map);
        }

        // Zoom sulla geometria
        if (zoomTo) {
            this.map.fitBounds(layer.getBounds());
        }

        // Aggiorna geometria corrente
        this.currentGeometry = geometry;
        if (layer.getLayers()[0] && layer.getLayers()[0].getLatLngs) {
            this.currentArea = L.GeometryUtil.geodesicArea(layer.getLayers()[0].getLatLngs()[0]);
        }
    }

    /**
     * Zoom su coordinate
     */
    zoomTo(lat, lng, zoom = 16) {
        this.map.setView([lat, lng], zoom);
    }

    /**
     * Ottiene geometria corrente in formato GeoJSON
     */
    getGeometry() {
        return this.currentGeometry;
    }

    /**
     * Ottiene area corrente in m²
     */
    getArea() {
        return this.currentArea;
    }

    /**
     * Pulisce la mappa
     */
    clear() {
        if (this.drawnItems) {
            this.drawnItems.clearLayers();
        }
        this.currentGeometry = null;
        this.currentArea = 0;
    }

    /**
     * Distrugge la mappa
     */
    destroy() {
        if (this.map) {
            this.map.remove();
            this.map = null;
        }
    }
}

// Esporta per uso globale
window.MapManager = MapManager;
