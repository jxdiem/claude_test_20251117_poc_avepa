-- Database System Service
-- Monitoring e audit

-- Tabella health checks
CREATE TABLE IF NOT EXISTS health_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    servizio TEXT NOT NULL,
    status TEXT NOT NULL,
    response_time REAL,
    error_message TEXT,
    timestamp TEXT DEFAULT (datetime('now'))
);

-- Tabella audit logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    servizio TEXT NOT NULL,
    azione TEXT NOT NULL,
    dettagli_json TEXT,
    timestamp TEXT DEFAULT (datetime('now'))
);

-- Tabella statistiche
CREATE TABLE IF NOT EXISTS statistiche (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metrica TEXT NOT NULL,
    valore TEXT NOT NULL,
    timestamp TEXT DEFAULT (datetime('now'))
);

-- Indici
CREATE INDEX IF NOT EXISTS idx_health_servizio ON health_checks(servizio);
CREATE INDEX IF NOT EXISTS idx_health_timestamp ON health_checks(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_stats_metrica ON statistiche(metrica);
