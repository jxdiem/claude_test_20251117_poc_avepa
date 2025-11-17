-- Database Admin Service
-- Gestione parametri normativi, colture, contributi

-- Tabella campagne
CREATE TABLE IF NOT EXISTS campagne (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    anno INTEGER NOT NULL UNIQUE,
    descrizione TEXT NOT NULL,
    data_inizio TEXT NOT NULL,
    data_fine TEXT NOT NULL,
    attiva INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Tabella colture
CREATE TABLE IF NOT EXISTS colture (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codice TEXT UNIQUE NOT NULL,
    descrizione TEXT NOT NULL,
    attiva INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Tabella contributi unitari
CREATE TABLE IF NOT EXISTS contributi_unitari (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campagna_id INTEGER NOT NULL,
    coltura_id INTEGER NOT NULL,
    importo_per_mq REAL NOT NULL,
    massimale_superficie REAL,
    massimale_importo REAL,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (campagna_id) REFERENCES campagne (id) ON DELETE CASCADE,
    FOREIGN KEY (coltura_id) REFERENCES colture (id) ON DELETE CASCADE,
    UNIQUE(campagna_id, coltura_id)
);

-- Tabella parametri normativi
CREATE TABLE IF NOT EXISTS parametri_normativi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chiave TEXT UNIQUE NOT NULL,
    valore TEXT NOT NULL,
    descrizione TEXT,
    tipo_dato TEXT DEFAULT 'string',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Indici
CREATE INDEX IF NOT EXISTS idx_campagne_anno ON campagne(anno);
CREATE INDEX IF NOT EXISTS idx_campagne_attiva ON campagne(attiva);
CREATE INDEX IF NOT EXISTS idx_colture_codice ON colture(codice);
CREATE INDEX IF NOT EXISTS idx_colture_attiva ON colture(attiva);
CREATE INDEX IF NOT EXISTS idx_contributi_campagna_id ON contributi_unitari(campagna_id);
CREATE INDEX IF NOT EXISTS idx_contributi_coltura_id ON contributi_unitari(coltura_id);

-- Trigger per aggiornare updated_at
CREATE TRIGGER IF NOT EXISTS update_campagne_timestamp
AFTER UPDATE ON campagne
FOR EACH ROW
BEGIN
    UPDATE campagne SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_colture_timestamp
AFTER UPDATE ON colture
FOR EACH ROW
BEGIN
    UPDATE colture SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_contributi_timestamp
AFTER UPDATE ON contributi_unitari
FOR EACH ROW
BEGIN
    UPDATE contributi_unitari SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- Dati di esempio
INSERT OR IGNORE INTO campagne (anno, descrizione, data_inizio, data_fine, attiva) VALUES
    (2024, 'Campagna 2024', '2024-01-01', '2024-12-31', 1);

INSERT OR IGNORE INTO colture (codice, descrizione, attiva) VALUES
    ('GRANO', 'Grano tenero', 1),
    ('MAIS', 'Mais', 1),
    ('ORZO', 'Orzo', 1),
    ('OLIVO', 'Oliveto', 1),
    ('VITE', 'Vigneto', 1);

INSERT OR IGNORE INTO contributi_unitari (campagna_id, coltura_id, importo_per_mq, massimale_superficie, massimale_importo) VALUES
    (1, 1, 0.50, 100000, 50000),
    (1, 2, 0.45, 100000, 45000),
    (1, 3, 0.40, 100000, 40000),
    (1, 4, 0.80, 50000, 40000),
    (1, 5, 0.70, 50000, 35000);
