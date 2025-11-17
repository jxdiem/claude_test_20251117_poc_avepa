-- Database Request Service
-- Gestione domande di aiuto e istruttoria

-- Tabella domande
CREATE TABLE IF NOT EXISTS domande (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fascicolo_id INTEGER NOT NULL,
    anno_campagna INTEGER NOT NULL,
    stato TEXT NOT NULL DEFAULT 'BOZZA' CHECK(stato IN ('BOZZA', 'PRESENTATA', 'IN_ISTRUTTORIA', 'APPROVATA', 'RESPINTA', 'LIQUIDATA')),
    data_presentazione TEXT,
    istruttore_id INTEGER,
    data_istruttoria TEXT,
    importo_calcolato REAL,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Tabella colture dichiarate
CREATE TABLE IF NOT EXISTS colture_dichiarate (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domanda_id INTEGER NOT NULL,
    particella_id INTEGER NOT NULL,
    coltura_id INTEGER NOT NULL,
    superficie_mq REAL NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (domanda_id) REFERENCES domande (id) ON DELETE CASCADE
);

-- Tabella note istruttoria
CREATE TABLE IF NOT EXISTS note_istruttoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domanda_id INTEGER NOT NULL,
    istruttore_id INTEGER NOT NULL,
    nota TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (domanda_id) REFERENCES domande (id) ON DELETE CASCADE
);

-- Indici
CREATE INDEX IF NOT EXISTS idx_domande_fascicolo_id ON domande(fascicolo_id);
CREATE INDEX IF NOT EXISTS idx_domande_anno_campagna ON domande(anno_campagna);
CREATE INDEX IF NOT EXISTS idx_domande_stato ON domande(stato);
CREATE INDEX IF NOT EXISTS idx_domande_istruttore_id ON domande(istruttore_id);
CREATE INDEX IF NOT EXISTS idx_colture_domanda_id ON colture_dichiarate(domanda_id);
CREATE INDEX IF NOT EXISTS idx_note_domanda_id ON note_istruttoria(domanda_id);

-- Trigger per aggiornare updated_at
CREATE TRIGGER IF NOT EXISTS update_domande_timestamp
AFTER UPDATE ON domande
FOR EACH ROW
BEGIN
    UPDATE domande SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_colture_timestamp
AFTER UPDATE ON colture_dichiarate
FOR EACH ROW
BEGIN
    UPDATE colture_dichiarate SET updated_at = datetime('now') WHERE id = NEW.id;
END;
