-- Database Auth Service
-- Gestione utenti, autenticazione e autorizzazione

-- Tabella utenti
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('BENEFICIARIO', 'ISTRUTTORE', 'AMMINISTRATORE', 'SISTEMISTA')),
    active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Tabella refresh tokens
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    expires_at TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Indici
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens(token);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);

-- Trigger per aggiornare updated_at
CREATE TRIGGER IF NOT EXISTS update_users_timestamp
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    UPDATE users SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- Inserimento utenti di default per testing
-- Password per tutti: "password123"
-- Hash generato con: salt$hash (vedere PasswordHasher in shared/auth_utils.py)

INSERT OR IGNORE INTO users (username, email, password_hash, role) VALUES
    ('admin', 'admin@example.com', 'e5c8f2a1b3d4e5f6$8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'AMMINISTRATORE'),
    ('sistemista', 'sistemista@example.com', 'f6d5e4c3b2a1e5f4$8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'SISTEMISTA'),
    ('istruttore1', 'istruttore1@example.com', 'a1b2c3d4e5f6a7b8$8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'ISTRUTTORE'),
    ('beneficiario1', 'beneficiario1@example.com', 'b8a7f6e5d4c3b2a1$8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'BENEFICIARIO');
