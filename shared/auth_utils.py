"""
Utility per autenticazione e autorizzazione
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
import hashlib
import secrets
import jwt
from shared.config import settings

class PasswordHasher:
    """Gestore hashing password"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash di una password con salt

        Args:
            password: Password in chiaro

        Returns:
            Password hashata con salt (formato: salt$hash)
        """
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return f"{salt}${pwd_hash.hex()}"

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verifica se una password corrisponde all'hash

        Args:
            password: Password in chiaro
            hashed_password: Password hashata (formato: salt$hash)

        Returns:
            True se la password è corretta
        """
        try:
            salt, stored_hash = hashed_password.split('$')
            pwd_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            return pwd_hash.hex() == stored_hash
        except Exception:
            return False


class JWTManager:
    """Gestore token JWT"""

    @staticmethod
    def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Crea un access token JWT

        Args:
            data: Dati da includere nel token
            expires_delta: Durata del token

        Returns:
            Token JWT
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: Dict) -> str:
        """
        Crea un refresh token JWT

        Args:
            data: Dati da includere nel token

        Returns:
            Token JWT per refresh
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Optional[Dict]:
        """
        Decodifica e valida un token JWT

        Args:
            token: Token JWT da decodificare

        Returns:
            Payload del token se valido, None altrimenti
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None


def get_role_permissions(role: str) -> list:
    """
    Ritorna i permessi associati a un ruolo

    Args:
        role: Nome del ruolo

    Returns:
        Lista di permessi
    """
    permissions = {
        "BENEFICIARIO": [
            "fascicolo:read_own",
            "fascicolo:write_own",
            "domanda:read_own",
            "domanda:create",
            "domanda:update_own_draft",
        ],
        "ISTRUTTORE": [
            "fascicolo:read_all",
            "domanda:read_all",
            "domanda:istruttoria",
            "calcolo:read",
            "calcolo:execute",
        ],
        "AMMINISTRATORE": [
            "coltura:read",
            "coltura:write",
            "contributo:read",
            "contributo:write",
            "campagna:read",
            "campagna:write",
            "parametro:read",
            "parametro:write",
            "user:manage",
            "stats:read",
        ],
        "SISTEMISTA": [
            "health:read",
            "logs:read",
            "monitoring:read",
            "backup:execute",
            "fascicolo:read_all",
            "domanda:read_all",
            "calcolo:read",
        ],
    }
    return permissions.get(role, [])
