-- Database Calculation Service
-- Gestione calcoli contributi

-- Tabella calcoli
CREATE TABLE IF NOT EXISTS calcoli (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domanda_id INTEGER NOT NULL UNIQUE,
    importo_totale REAL NOT NULL,
    data_calcolo TEXT DEFAULT (datetime('now')),
    dettaglio_json TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Tabella dettaglio calcolo
CREATE TABLE IF NOT EXISTS dettaglio_calcolo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    calcolo_id INTEGER NOT NULL,
    coltura_id INTEGER NOT NULL,
    superficie_mq REAL NOT NULL,
    importo_unitario REAL NOT NULL,
    importo_totale REAL NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (calcolo_id) REFERENCES calcoli (id) ON DELETE CASCADE
);

-- Indici
CREATE INDEX IF NOT EXISTS idx_calcoli_domanda_id ON calcoli(domanda_id);
CREATE INDEX IF NOT EXISTS idx_dettaglio_calcolo_id ON dettaglio_calcolo(calcolo_id);
