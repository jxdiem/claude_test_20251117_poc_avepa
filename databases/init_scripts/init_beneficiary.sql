-- Database Beneficiary Service
-- Gestione fascicoli aziendali, dati bancari, particelle, macchinari

-- Tabella fascicoli
CREATE TABLE IF NOT EXISTS fascicoli (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    ragione_sociale TEXT NOT NULL,
    cf_piva TEXT NOT NULL,
    indirizzo TEXT NOT NULL,
    cap TEXT NOT NULL,
    comune TEXT NOT NULL,
    provincia TEXT NOT NULL,
    telefono TEXT,
    email TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Tabella dati bancari
CREATE TABLE IF NOT EXISTS dati_bancari (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fascicolo_id INTEGER NOT NULL,
    iban TEXT NOT NULL,
    bic TEXT,
    intestatario TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (fascicolo_id) REFERENCES fascicoli (id) ON DELETE CASCADE
);

-- Tabella particelle catastali
CREATE TABLE IF NOT EXISTS particelle_catastali (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fascicolo_id INTEGER NOT NULL,
    comune TEXT NOT NULL,
    foglio TEXT NOT NULL,
    particella TEXT NOT NULL,
    subalterno TEXT,
    superficie_mq REAL NOT NULL,
    superficie_calcolata_mq REAL,  -- Area calcolata dalla geometria disegnata
    coordinate_geojson TEXT,  -- Geometria in formato GeoJSON (Polygon o MultiPolygon)
    centroid_lat REAL,  -- Latitudine centroide per zoom rapido
    centroid_lng REAL,  -- Longitudine centroide per zoom rapido
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (fascicolo_id) REFERENCES fascicoli (id) ON DELETE CASCADE
);

-- Tabella macchinari
CREATE TABLE IF NOT EXISTS macchinari (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fascicolo_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    marca TEXT NOT NULL,
    modello TEXT NOT NULL,
    anno INTEGER,
    targa TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (fascicolo_id) REFERENCES fascicoli (id) ON DELETE CASCADE
);

-- Indici
CREATE INDEX IF NOT EXISTS idx_fascicoli_user_id ON fascicoli(user_id);
CREATE INDEX IF NOT EXISTS idx_fascicoli_cf_piva ON fascicoli(cf_piva);
CREATE INDEX IF NOT EXISTS idx_dati_bancari_fascicolo_id ON dati_bancari(fascicolo_id);
CREATE INDEX IF NOT EXISTS idx_particelle_fascicolo_id ON particelle_catastali(fascicolo_id);
CREATE INDEX IF NOT EXISTS idx_macchinari_fascicolo_id ON macchinari(fascicolo_id);

-- Trigger per aggiornare updated_at
CREATE TRIGGER IF NOT EXISTS update_fascicoli_timestamp
AFTER UPDATE ON fascicoli
FOR EACH ROW
BEGIN
    UPDATE fascicoli SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_dati_bancari_timestamp
AFTER UPDATE ON dati_bancari
FOR EACH ROW
BEGIN
    UPDATE dati_bancari SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_particelle_timestamp
AFTER UPDATE ON particelle_catastali
FOR EACH ROW
BEGIN
    UPDATE particelle_catastali SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_macchinari_timestamp
AFTER UPDATE ON macchinari
FOR EACH ROW
BEGIN
    UPDATE macchinari SET updated_at = datetime('now') WHERE id = NEW.id;
END;
