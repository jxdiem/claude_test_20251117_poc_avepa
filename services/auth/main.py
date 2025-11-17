"""
Auth Service - Gestione autenticazione e autorizzazione
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import sys
import os

# Aggiungi la directory root al path per import shared
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.config import settings
from shared.database import DatabaseManager
from shared.auth_utils import PasswordHasher, JWTManager
from shared.schemas import (
    UserRole,
    LoginRequest,
    LoginResponse,
    TokenRefreshRequest,
    UserCreate,
    UserResponse,
    BaseResponse,
    ErrorResponse
)

# Inizializzazione app
app = FastAPI(
    title="Auth Service",
    description="Servizio di autenticazione e autorizzazione",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
DB_PATH = os.path.join(settings.DATABASE_DIR, "auth.db")
db = DatabaseManager(DB_PATH)

# Inizializza database
def init_database():
    """Inizializza il database con lo schema"""
    init_script_path = os.path.join(settings.DATABASE_DIR, "init_scripts", "init_auth.sql")
    if os.path.exists(init_script_path):
        with open(init_script_path, 'r') as f:
            db.execute_script(f.read())
        print(f"Database inizializzato: {DB_PATH}")
    else:
        print(f"Warning: Script di inizializzazione non trovato: {init_script_path}")

# Inizializza al startup
@app.on_event("startup")
async def startup_event():
    init_database()


# Endpoints

@app.get("/")
async def root():
    """Health check"""
    return {"service": "auth", "status": "running", "version": "1.0.0"}


@app.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login utente

    Args:
        request: Credenziali di login

    Returns:
        Access token, refresh token e info utente
    """
    # Cerca utente per username
    users = db.execute_query(
        "SELECT * FROM users WHERE username = ? AND active = 1",
        (request.username,)
    )

    if not users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenziali non valide"
        )

    user = users[0]

    # Verifica password
    if not PasswordHasher.verify_password(request.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenziali non valide"
        )

    # Crea access token
    access_token = JWTManager.create_access_token(
        data={"sub": str(user['id']), "username": user['username'], "role": user['role']}
    )

    # Crea refresh token
    refresh_token = JWTManager.create_refresh_token(
        data={"sub": str(user['id'])}
    )

    # Salva refresh token nel database
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db.execute_update(
        "INSERT INTO refresh_tokens (token, user_id, expires_at) VALUES (?, ?, ?)",
        (refresh_token, user['id'], expires_at.isoformat())
    )

    # Pulisci refresh token scaduti
    db.execute_update(
        "DELETE FROM refresh_tokens WHERE expires_at < datetime('now')"
    )

    return LoginResponse(
        success=True,
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user['id'],
        username=user['username'],
        role=UserRole(user['role'])
    )


@app.post("/refresh")
async def refresh_token(request: TokenRefreshRequest):
    """
    Rinnova access token usando refresh token

    Args:
        request: Refresh token

    Returns:
        Nuovo access token
    """
    # Decodifica refresh token
    payload = JWTManager.decode_token(request.refresh_token)
    if not payload or payload.get('type') != 'refresh':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token non valido"
        )

    # Verifica che il token sia nel database e non scaduto
    tokens = db.execute_query(
        "SELECT * FROM refresh_tokens WHERE token = ? AND expires_at > datetime('now')",
        (request.refresh_token,)
    )

    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token non valido o scaduto"
        )

    user_id = int(payload['sub'])

    # Recupera info utente
    users = db.execute_query(
        "SELECT * FROM users WHERE id = ? AND active = 1",
        (user_id,)
    )

    if not users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utente non trovato"
        )

    user = users[0]

    # Crea nuovo access token
    access_token = JWTManager.create_access_token(
        data={"sub": str(user['id']), "username": user['username'], "role": user['role']}
    )

    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """
    Crea un nuovo utente (solo per amministratori)

    Args:
        user_data: Dati del nuovo utente

    Returns:
        Utente creato
    """
    # Verifica che username non esista già
    existing = db.execute_query(
        "SELECT id FROM users WHERE username = ? OR email = ?",
        (user_data.username, user_data.email)
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username o email già esistenti"
        )

    # Hash password
    password_hash = PasswordHasher.hash_password(user_data.password)

    # Inserisci utente
    user_id = db.execute_update(
        "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
        (user_data.username, user_data.email, password_hash, user_data.role.value)
    )

    # Recupera utente creato
    users = db.execute_query("SELECT * FROM users WHERE id = ?", (user_id,))
    user = users[0]

    return UserResponse(
        id=user['id'],
        username=user['username'],
        email=user['email'],
        role=UserRole(user['role']),
        active=bool(user['active']),
        created_at=user['created_at']
    )


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """
    Recupera informazioni utente per ID

    Args:
        user_id: ID dell'utente

    Returns:
        Dati utente
    """
    users = db.execute_query("SELECT * FROM users WHERE id = ?", (user_id,))

    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato"
        )

    user = users[0]

    return UserResponse(
        id=user['id'],
        username=user['username'],
        email=user['email'],
        role=UserRole(user['role']),
        active=bool(user['active']),
        created_at=user['created_at']
    )


@app.post("/verify-token")
async def verify_token(token: str):
    """
    Verifica validità di un access token

    Args:
        token: Token JWT da verificare

    Returns:
        Payload del token se valido
    """
    payload = JWTManager.decode_token(token)

    if not payload or payload.get('type') != 'access':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token non valido"
        )

    return {
        "success": True,
        "payload": payload
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.AUTH_SERVICE_PORT)
