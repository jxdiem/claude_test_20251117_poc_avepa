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
-- Hash generato con pbkdf2_hmac SHA256, 100000 iterazioni (vedere PasswordHasher in shared/auth_utils.py)

-- Rimuovi utenti di test esistenti e reinseriscili con hash corretti
DELETE FROM users WHERE username IN ('admin', 'sistemista', 'istruttore1', 'beneficiario1');

INSERT INTO users (username, email, password_hash, role) VALUES
    ('admin', 'admin@example.com', 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6$72eea5c577564d9191afbb59c4db0e3f23864e5de290ad0dc81da0c8241f7dba', 'AMMINISTRATORE'),
    ('sistemista', 'sistemista@example.com', 'b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7$8870bb3e991f77daa9831311b04849c1f54f6f1e55426ad9cc8f54467a1c3cb5', 'SISTEMISTA'),
    ('istruttore1', 'istruttore1@example.com', 'c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8$9b0bdb10f37f4918eaf4fdf4553d3265eee10e3abecbff29d8ce9f7f4bccdb47', 'ISTRUTTORE'),
    ('beneficiario1', 'beneficiario1@example.com', 'd4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9$58d39bdd62b679b6ce9688ca56537b50ae629acdfcc672a39d3ea14c34921d49', 'BENEFICIARIO');
